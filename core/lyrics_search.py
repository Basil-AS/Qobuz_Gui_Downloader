"""
Модуль для поиска текстов песен
Двухэтапный алгоритм: /api/search (все варианты) → фильтрация synced/plain
Приоритет: синхронизированные тексты → обычные тексты
"""
import re
import requests
import logging
from typing import Optional, Tuple


logger = logging.getLogger(__name__)


class LyricsSearcher:
    """Класс для поиска текстов песен"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Qobuz GUI Downloader v1.0.0 (https://github.com/Basil-AS/Qobuz_Gui_Downloader)'
        })
    
    def _is_instrumental_text(self, text: str) -> bool:
        """
        Проверяет, является ли текст маркером инструментального трека.
        Возвращает True, если текст - это заглушка типа "[Instrumental]".
        """
        if not text or not text.strip():
            return False
        
        # Сначала проверяем на маркеры в ПОЛНОМ тексте (включая скобки)
        instrumental_markers_full = [
            r'^\s*\[instrumental\]\s*$',
            r'^\s*\[инструментал\]\s*$',
            r'\[au:\s*instrumental\]'
        ]
        
        for marker in instrumental_markers_full:
            if re.search(marker, text, re.IGNORECASE | re.MULTILINE):
                return True
        
        # Убираем таймкоды LRC, чтобы они не мешали поиску
        plain_text = re.sub(r'\[\d{2}:\d{2}\.\d{2,3}\]', '', text).strip()
        
        # Если после очистки ничего не осталось (только таймкоды)
        if not plain_text:
            return False  # Это не "инструментал", а просто пустой LRC
        
        # Проверяем длину текста - маркеры обычно короткие (до 30 символов)
        if len(plain_text) > 30:
            return False
        
        # Если слишком много строк, маловероятно что это просто маркер
        lines = [line.strip() for line in plain_text.splitlines() if line.strip()]
        if len(lines) > 3:
            return False
        
        # Ключевые слова инструментальных треков (без скобок) - только для коротких текстов
        instrumental_markers = [
            r'^\s*instrumental\s*$',
            r'^\s*инструментал\s*$',
            r'^\s*instrumental\s+version\s*$'
        ]
        
        # Проверяем наличие маркеров в очищенном тексте
        for marker in instrumental_markers:
            if re.search(marker, plain_text, re.IGNORECASE):
                return True
        
        return False
    
    def search_lyrics(self, artist: str, title: str, album: str = None, duration: int = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Двухэтапный поиск текстов: сначала synced, потом plain
        
        Returns:
            Tuple[plain_text, lrc_text] - обычный текст и LRC (если найден synced)
        """
        logger.info(f"🔍 Поиск текста: {artist} - {title}")
        
        # Проверка на инструментальный трек по названию
        instrumental_keywords = ['instrumental', 'инструментал', 'piano version', 'orchestral', 'acoustic']
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in instrumental_keywords):
            # Для инструментальных треков не ищем тексты
            if not any(word in title_lower for word in ['feat', 'vocals', 'with', 'sung']):
                logger.info("🎼 Инструментальный трек - пропускаем поиск текстов")
                return None, None
        
        # Шаг 1: Используем /api/search для получения всех вариантов
        search_results = self._search_lrclib_all(artist, title, album, duration)
        
        if search_results:
            logger.info(f"✓ Найдено {len(search_results)} вариантов текста")
            
            # Фильтруем результаты: должно быть СТРОГОЕ совпадение по названию И исполнителю
            filtered_results = self._filter_results_strict(search_results, artist, title)
            
            if not filtered_results:
                logger.warning("⚠ Нет результатов с точным совпадением названия и исполнителя")
                logger.info("💡 Это предотвращает получение текстов от других песен")
                return None, None
            
            logger.info(f"✓ После строгой фильтрации осталось {len(filtered_results)} совпадений")
            
            # Приоритет 1: Синхронизированный текст
            for result in filtered_results:
                synced = result.get('syncedLyrics')
                if synced and not result.get('instrumental'):
                    # Проверяем, не является ли текст заглушкой
                    if self._is_instrumental_text(synced):
                        logger.info("🎼 Обнаружена заглушка [Instrumental] в LRC - пропускаем")
                        continue
                    
                    # Проверяем наличие таймкодов
                    if re.search(r'\[\d{2}:\d{2}\.\d{2,3}\]', synced):
                        plain_text, lrc_text = self._process_lyrics(synced)
                        if lrc_text:
                            logger.info("✅ Получен СИНХРОНИЗИРОВАННЫЙ текст (lrclib.net)")
                            return plain_text, lrc_text
            
            # Приоритет 2: Обычный текст (если synced нигде нет)
            for result in filtered_results:
                plain = result.get('plainLyrics')
                if plain and not result.get('instrumental'):
                    # Проверяем, не является ли текст заглушкой
                    if self._is_instrumental_text(plain):
                        logger.info("🎼 Обнаружена заглушка [Instrumental] - пропускаем")
                        continue
                    
                    logger.info("✅ Получен ОБЫЧНЫЙ текст (без таймкодов, lrclib.net)")
                    return plain, None
        
        # Шаг 2: Широкий поиск через syncedlyrics (несколько провайдеров)
        logger.info(f"🔍 Расширенный поиск через syncedlyrics...")
        result = self._search_syncedlyrics(artist, title)
        if result:
            # Проверяем на заглушку перед обработкой
            if self._is_instrumental_text(result):
                logger.info("🎼 Обнаружена заглушка [Instrumental] - пропускаем")
                return None, None
            
            plain_text, lrc_text = self._process_lyrics(result)
            if lrc_text:
                logger.info("✅ Получен СИНХРОНИЗИРОВАННЫЙ текст (syncedlyrics)")
                return plain_text, lrc_text
            elif plain_text:
                logger.info("✅ Получен ОБЫЧНЫЙ текст (syncedlyrics)")
                return plain_text, None
        
        logger.warning(f"❌ Текст не найден: {artist} - {title}")
        logger.info("💡 Рекомендации: проверьте правильность написания (включая регистр)")
        return None, None
    
    def _filter_results_strict(self, results, target_artist: str, target_title: str):
        """
        МАКСИМАЛЬНО СТРОГАЯ фильтрация по исполнителю И названию.
        Проверяет оба поля для предотвращения ложных совпадений.
        """
        # Нормализуем целевые значения
        target_artist_norm = target_artist.lower().strip()
        target_title_norm = target_title.lower().strip()
        target_title_base = re.sub(r'\s*\([^)]*\)\s*', '', target_title_norm).strip()
        
        # Создаём список допустимых вариантов исполнителя (для транслитерации)
        target_artist_variants = [target_artist_norm]
        
        # Простая проверка: если исполнитель на кириллице, он может быть и латиницей
        # Например: Земфира / Zemfira
        if any(ord(c) > 127 for c in target_artist_norm):
            # Содержит не-ASCII символы (кириллица)
            target_artist_variants.append(target_artist_norm)
        
        filtered = []
        for result in results:
            # Проверка исполнителя
            result_artist = result.get('artistName', '').lower().strip()
            
            # Для исполнителя допускаем небольшую вариативность
            artist_match = False
            for variant in target_artist_variants:
                if (result_artist == variant or
                    result_artist in variant or
                    variant in result_artist or
                    # Проверка первых 4 символов для транслитерации
                    (len(result_artist) >= 4 and len(variant) >= 4 and 
                     result_artist[:4] == variant[:4])):
                    artist_match = True
                    break
            
            if not artist_match:
                continue
            
            # Проверка названия - ТОЛЬКО точное совпадение
            result_title = result.get('trackName', '').lower().strip()
            result_title_base = re.sub(r'\s*\([^)]*\)\s*', '', result_title).strip()
            
            title_match = (
                result_title == target_title_norm or
                result_title_base == target_title_base
            )
            
            if title_match:
                filtered.append(result)
                logger.debug(f"  ✓ Совпадение: '{result.get('artistName')}' - '{result.get('trackName')}'")
        
        return filtered
    
    def _filter_results_by_title(self, results, target_title: str):
        """
        МАКСИМАЛЬНО СТРОГАЯ фильтрация результатов по совпадению названия.
        Возвращает ТОЛЬКО точные совпадения, предотвращает получение текстов от других песен.
        """
        # Нормализуем целевое название
        target_normalized = target_title.lower().strip()
        # Убираем всё в скобках для сравнения базовой части
        target_base = re.sub(r'\s*\([^)]*\)\s*', '', target_normalized).strip()
        
        filtered = []
        for result in results:
            track_name = result.get('trackName', '').lower().strip()
            track_base = re.sub(r'\s*\([^)]*\)\s*', '', track_name).strip()
            
            # ТОЛЬКО точное совпадение! Никаких "startswith" или "contains"
            # Вариант 1: Точное совпадение полного названия
            if track_name == target_normalized:
                filtered.append(result)
                continue
            
            # Вариант 2: Точное совпадение базовой части (без скобок)
            if track_base == target_base:
                filtered.append(result)
                continue
        
        if filtered:
            logger.debug(f"✓ Строгая фильтрация: {len(results)} → {len(filtered)} результатов")
        else:
            logger.debug(f"✗ Строгая фильтрация: нет точных совпадений для '{target_title}'")
        
        # ВАЖНО: Не возвращаем все результаты, если фильтр пустой!
        # Лучше не найти текст, чем найти чужой
        return filtered
    
    def _search_lrclib_all(self, artist: str, title: str, album: str = None, duration: int = None):
        """
        Двухэтапный поиск через lrclib.net: /api/search → массив результатов
        
        Args:
            artist: имя исполнителя
            title: название трека
            album: название альбома (опционально)
            duration: длительность в секундах (опционально)
        
        Returns:
            List[dict] - массив всех найденных вариантов текста
        """
        results = []
        
        try:
            # Вариант 1: Поиск по точной сигнатуре (GET /api/get)
            if duration:
                url = "https://lrclib.net/api/get"
                params = {
                    'artist_name': artist,
                    'track_name': title,
                }
                if album:
                    params['album_name'] = album
                if duration:
                    params['duration'] = int(duration)
                
                response = self.session.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('syncedLyrics') or data.get('plainLyrics'):
                        results.append(data)
                        logger.debug(f"✓ Точный поиск (GET /api/get): найдено")
            
            # Вариант 2: Широкий поиск (GET /api/search) - основной
            url = "https://lrclib.net/api/search"
            
            # Формируем разные варианты поисковых запросов
            search_queries = []
            
            # 1. Полный запрос: artist + title + album
            if album:
                search_queries.append(f"{artist} {title} {album}")
            
            # 2. Базовый: artist + title
            search_queries.append(f"{artist} {title}")
            
            # 3. Только title (для песен с разным написанием исполнителя)
            search_queries.append(title)
            
            for query in search_queries:
                try:
                    params = {'q': query}
                    response = self.session.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list) and len(data) > 0:
                            logger.debug(f"✓ Поиск '{query}': найдено {len(data)} результатов")
                            # Добавляем только новые результаты (по id)
                            existing_ids = {r.get('id') for r in results}
                            for item in data:
                                if item.get('id') not in existing_ids:
                                    results.append(item)
                except Exception as e:
                    logger.debug(f"Ошибка поиска '{query}': {e}")
                    continue
        
        except Exception as e:
            logger.debug(f"Ошибка поиска через lrclib.net: {e}")
        
        return results
    
    def _search_syncedlyrics(self, artist: str, title: str) -> Optional[str]:
        """
        Поиск через библиотеку syncedlyrics (приоритет synced, fallback на plain)
        
        Args:
            artist: имя исполнителя
            title: название трека
        
        Returns:
            Синхронизированный или обычный текст
        """
        try:
            import syncedlyrics
            
            search_query = f"{artist} - {title}"
            
            # Сначала пытаемся найти synced
            result = syncedlyrics.search(search_query, allow_plain_format=False)
            if result:
                logger.debug("✓ syncedlyrics: найден СИНХРОНИЗИРОВАННЫЙ текст")
                return result
            
            # Если synced не найден, пробуем plain
            result = syncedlyrics.search(search_query, allow_plain_format=True)
            if result:
                logger.debug("✓ syncedlyrics: найден ОБЫЧНЫЙ текст")
                return result
            
            logger.debug("syncedlyrics: текст не найден")
            
        except ImportError:
            logger.warning("Библиотека syncedlyrics не установлена")
        except Exception as e:
            logger.debug(f"Ошибка поиска через syncedlyrics: {e}")
        
        return None
    
    def _process_lyrics(self, lyrics_raw: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Обработка найденного текста: определение формата и разделение
        
        Returns:
            Tuple[plain_text, lrc_text]
            - Если LRC: (plain_version, lrc_version)
            - Если plain: (plain_text, None)
        """
        if not lyrics_raw:
            return None, None
        
        # Проверяем, есть ли LRC таймкоды (должно быть хотя бы 3 строки с таймкодами)
        lrc_lines = [line for line in lyrics_raw.splitlines() 
                     if re.search(r"\[\s*\d{1,2}:\d{2}(?:[\.:]\d{1,2})?\s*\]", line)]
        
        if len(lrc_lines) >= 3:  # Минимум 3 строки с таймкодами
            lrc_text = self._normalize_lrc(lyrics_raw)
            plain_text = self._lrc_to_plain(lrc_text)
            logger.debug(f"✓ Обработан LRC текст ({len(lrc_lines)} строк с таймкодами)")
            return plain_text, lrc_text
        else:
            # Обычный текст без таймкодов
            plain_text = lyrics_raw.strip()
            logger.debug(f"✓ Обработан обычный текст (без таймкодов)")
            return plain_text, None
    
    def _normalize_lrc(self, lyrics_lrc: str) -> str:
        """Нормализация LRC: приведение таймкодов к единому формату [mm:ss.xx]"""
        lines = lyrics_lrc.splitlines()
        normalized_lines = []
        
        for line in lines:
            # Проверяем наличие таймкода
            if re.search(r"\[\s*\d{1,2}:\d{2}(?:[\.:]\d{1,2})?\s*\]", line):
                # Приводим таймкоды к формату [mm:ss.xx]
                def repl(m):
                    ts = m.group(0).replace('[', '').replace(']', '').strip()
                    parts = re.split(r"[:\.]", ts)
                    mm = int(parts[0]) if parts and parts[0].isdigit() else 0
                    ss = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
                    ff = 0
                    if len(parts) > 2 and parts[2].isdigit():
                        ff = int(parts[2])
                        ff = max(0, min(ff, 99))
                    return f"[{mm:02d}:{ss:02d}.{ff:02d}]"
                
                line = re.sub(r"\[\s*\d{1,2}:\d{2}(?:[\.:]\d{1,2})?\s*\]", repl, line, count=1)
                normalized_lines.append(line)
            else:
                normalized_lines.append(line)
        
        # Удаляем пустые строки в начале и конце
        while normalized_lines and not normalized_lines[0].strip():
            normalized_lines.pop(0)
        while normalized_lines and not normalized_lines[-1].strip():
            normalized_lines.pop()
        
        return "\n".join(normalized_lines)
    
    def _lrc_to_plain(self, lyrics_lrc: str) -> str:
        """Преобразование LRC в обычный текст (удаление таймкодов)"""
        plain_lines = []
        for line in lyrics_lrc.splitlines():
            text = re.sub(r"^\s*\[[^\]]+\]\s*", "", line)
            plain_lines.append(text)
        return "\n".join(plain_lines)
    
    def lrc_to_srt(self, lyrics_lrc: str) -> str:
        """
        Конвертация LRC в SubRip (.srt) для VLC
        
        Args:
            lyrics_lrc: текст в формате LRC
        
        Returns:
            текст в формате SRT
        """
        entries = []
        time_pattern = re.compile(r"\[(\d{1,2}):(\d{2})(?:[\.:](\d{1,2}))?\]")
        
        for raw_line in lyrics_lrc.splitlines():
            if not raw_line.strip():
                continue
            times = list(time_pattern.finditer(raw_line))
            if not times:
                continue
            
            # Текст без таймкодов
            text = time_pattern.sub("", raw_line).strip()
            if not text:
                text = "♪"
            
            for m in times:
                mm = int(m.group(1) or 0)
                ss = int(m.group(2) or 0)
                ff = int(m.group(3) or 0)
                # ff трактуем как сотые доли секунды
                ms = ff * 10 if ff < 10 else ff if ff < 100 else 0
                total_ms = (mm * 60 + ss) * 1000 + ms
                entries.append((total_ms, text))
        
        if not entries:
            return ""
        
        entries.sort(key=lambda x: x[0])
        
        def fmt_srt_time(ms: int) -> str:
            if ms < 0:
                ms = 0
            h = ms // 3600000
            ms %= 3600000
            m = ms // 60000
            ms %= 60000
            s = ms // 1000
            ms %= 1000
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"
        
        srt_lines = []
        for idx, (start_ms, text) in enumerate(entries, start=1):
            if idx < len(entries):
                # Конец - на 0.5 секунды раньше следующего старта
                end_ms = max(start_ms + 500, entries[idx][0] - 500)
            else:
                end_ms = start_ms + 4000
            
            srt_lines.append(str(idx))
            srt_lines.append(f"{fmt_srt_time(start_ms)} --> {fmt_srt_time(end_ms)}")
            srt_lines.append(text)
            srt_lines.append("")
        
        return "\n".join(srt_lines)
