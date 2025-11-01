"""
Модуль для поиска текстов песен
Строгий алгоритм: поиск → фильтрация → выбор лучшего
Приоритет: синхронизированные тексты → обычные тексты
"""
import re
import requests
import logging
from typing import Optional, Tuple, List, Dict

try:
    from rapidfuzz import fuzz
    FUZZ_AVAILABLE = True
except ImportError:
    FUZZ_AVAILABLE = False
    logging.warning("Библиотека rapidfuzz не установлена. Сравнение строк будет менее точным. Рекомендуется: pip install rapidfuzz")


logger = logging.getLogger(__name__)


class LyricsSearcher:
    """
    Класс для надежного поиска текстов песен с приоритетом синхронизированных версий
    и строгой фильтрацией для предотвращения ложных срабатываний.
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Qobuz GUI Downloader v1.0.5 (https://github.com/Basil-AS/Qobuz_Gui_Downloader)'
        })
    
    def _is_instrumental_text(self, text: str) -> bool:
        """
        Проверяет, является ли текст маркером инструментального трека.
        Возвращает True, если текст - это заглушка типа "[Instrumental]".
        """
        if not text or not text.strip():
            return False
        
        # Убираем таймкоды и метаданные
        plain_text = re.sub(r'\[.*?\]', '', text).strip().lower()
        if not plain_text:
            return False
        
        # Короткий текст с ключевыми словами
        if len(plain_text) < 30 and any(m in plain_text for m in ['instrumental', 'инструментал']):
            return True
        
        return False
    
    def _get_clean_title(self, title: str) -> str:
        """
        Убирает из названия ремиксы, версии и прочее для более чистого сравнения.
        Удаляет всё в скобках () и [] и одинарных кавычках для точного сравнения базового названия.
        """
        # Убираем номера треков в начале (01., 1., 001. и т.д.)
        clean_title = re.sub(r'^\d+\.\s*', '', title)
        # Убираем все в скобках, квадратных скобках, одинарных и двойных кавычках, а также кавычки-ёлочки
        clean_title = re.sub(r"\s*\(.*?\)\s*|\s*\[.*?\]\s*|\s*'.*?'\s*|\s*\".*?\"\s*|\s*«.*?»\s*", '', clean_title)
        # Убираем подчёркивания и подряд идущие символы подчёркивания
        clean_title = re.sub(r'_+', ' ', clean_title)
        # Убираем распространенные "лишние" слова
        clean_title = re.sub(r'\s*-\s*(live|remix|reprise|acoustic|version)\s*', '', clean_title, flags=re.IGNORECASE)
        # Нормализуем пробелы и спецсимволы
        clean_title = re.sub(r'\s+', ' ', clean_title)
        clean_title = clean_title.strip(' _-\t\n\r').strip()
        return clean_title.strip().lower()
    
    def search_lyrics(self, artist: str, title: str, album: str = None, duration: int = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Основной метод поиска, реализующий алгоритм "Поиск → Фильтрация → Выбор лучшего".
        
        Returns:
            Tuple[plain_text, lrc_text] - обычный текст и LRC (если найден synced)
        """
        logger.info(f"🔍 Поиск текста для: {artist} - {title} (длительность: {duration}с)")
        
        # Проверка на инструментальный трек по названию
        instrumental_keywords = ['instrumental', 'инструментал']
        title_lower = title.lower()
        if any(keyword in title_lower for keyword in instrumental_keywords):
            if not any(word in title_lower for word in ['feat', 'vocals', 'with', 'sung']):
                logger.info("🎼 Инструментальный трек - пропускаем поиск текстов")
                return None, None
        
        # --- Шаг 1: Получаем кандидатов с помощью /api/search ---
        try:
            url = "https://lrclib.net/api/search"
            params = {'track_name': title, 'artist_name': artist}
            if album:
                params['album_name'] = album
            
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            candidates = response.json()
            
            if not candidates:
                logger.warning("❌ LRCLib: Поиск не дал результатов")
                return None, None
        except (requests.RequestException, ValueError) as e:
            logger.error(f"❌ LRCLib: Ошибка при запросе /api/search: {e}")
            return None, None
        
        logger.info(f"✓ Найдено {len(candidates)} кандидатов. Начинаем строгую фильтрацию...")
        
        # --- Шаг 2: Фильтрация и выбор лучшего кандидата ---
        
        # Сначала ищем идеальный вариант: с синхронизированным текстом
        best_synced_match = self._find_best_match(candidates, artist, title, duration or 0, require_synced=True)
        if best_synced_match:
            logger.info("✅ Найден лучший кандидат с СИНХРОНИЗИРОВАННЫМ текстом")
            synced_lyrics = best_synced_match.get('syncedLyrics')
            is_instr = self._is_instrumental_text(synced_lyrics) or best_synced_match.get('instrumental')
            if is_instr:
                logger.info("🎼 Трек определен как ИНСТРУМЕНТАЛЬНЫЙ")
                return None, None
            plain_lyrics = self._lrc_to_plain(synced_lyrics)
            return plain_lyrics, synced_lyrics
        
        # Если синхронизированный не найден, ищем лучший вариант с обычным текстом
        logger.info("⚠️ Синхронизированный текст не найден. Ищем лучший вариант с обычным текстом...")
        best_plain_match = self._find_best_match(candidates, artist, title, duration or 0, require_synced=False)
        if best_plain_match:
            logger.info("✅ Найден лучший кандидат с ОБЫЧНЫМ текстом")
            plain_lyrics = best_plain_match.get('plainLyrics')
            is_instr = self._is_instrumental_text(plain_lyrics) or best_plain_match.get('instrumental')
            if is_instr:
                logger.info("🎼 Трек определен как ИНСТРУМЕНТАЛЬНЫЙ")
                return None, None
            return plain_lyrics, None
        
        logger.warning(f"❌ Текст не найден после строгой фильтрации для: {artist} - {title}")
        return None, None
    
    def _find_best_match(self, candidates: List[Dict], target_artist: str, target_title: str, target_duration: int, require_synced: bool) -> Optional[Dict]:
        """
        Итерируется по списку кандидатов и выбирает лучший на основе набора строгих правил.
        
        Args:
            candidates: список кандидатов от lrclib API
            target_artist: целевой исполнитель
            target_title: целевое название
            target_duration: целевая длительность в секундах
            require_synced: требовать наличие syncedLyrics
        
        Returns:
            Лучший кандидат или None
        """
        best_candidate = None
        highest_score = float('-inf')  # Минус бесконечность, чтобы любой score был лучше
        
        MIN_ARTIST_SCORE = 90  # Требуем почти идеального совпадения исполнителя
        
        # Получаем "чистое" название целевого трека для сравнения
        target_title_clean = self._get_clean_title(target_title)
        
        for item in candidates:
            # --- Правило 1: Проверяем наличие нужного типа текста ---
            if require_synced:
                if not item.get('syncedLyrics'):
                    continue
            else:
                if not item.get('plainLyrics') and not item.get('syncedLyrics'):
                    continue
            
            # --- Правило 2: Строгая проверка метаданных ---
            item_title = item.get('trackName', '')
            item_artist = item.get('artistName', '')
            
            # Сравниваем исполнителей
            if FUZZ_AVAILABLE:
                artist_score = fuzz.ratio(target_artist.lower(), item_artist.lower())
                if artist_score < MIN_ARTIST_SCORE:
                    logger.debug(f"Отброшен (артист): '{item_artist}' vs '{target_artist}' (схожесть {artist_score:.0f}%)")
                    continue
            else:  # Если fuzz недоступен, проверяем на простое вхождение
                if target_artist.lower() not in item_artist.lower() and item_artist.lower() not in target_artist.lower():
                    logger.debug(f"Отброшен (артист): '{item_artist}' vs '{target_artist}'")
                    continue
                artist_score = 95  # Присваиваем высокий балл при простом совпадении
            
            # Сравниваем названия. ЭТО КЛЮЧЕВОЙ МОМЕНТ!
            item_title_clean = self._get_clean_title(item_title)
            
            # Мы требуем, чтобы "чистые" названия совпадали на 100%
            if item_title_clean != target_title_clean:
                logger.debug(f"Отброшен (название): '{item_title_clean}' vs '{target_title_clean}'")
                continue
            
            # --- Правило 3: Проверка длительности ---
            item_duration = item.get('duration', 0)
            duration_diff = abs(target_duration - item_duration)
            if target_duration > 0 and duration_diff > 100:  # Погрешность до 100 секунд (альбомные/расширенные версии)
                logger.debug(f"Отброшен (длительность): {item_duration}с vs {target_duration}с (разница {duration_diff:.1f}с)")
                continue
            
            # --- Оценка кандидата ---
            # Все проверки пройдены. Теперь выбираем лучшего из прошедших.
            # Более высокое совпадение по артисту лучше.
            # Меньшая разница в длительности лучше.
            # Наличие synced-текста всегда лучше.
            score = artist_score - (duration_diff * 10)  # Штрафуем за разницу в длительности
            if item.get('syncedLyrics'):
                score += 100  # Бонус за synced-текст
            
            if score > highest_score:
                highest_score = score
                best_candidate = item
        
        if best_candidate:
            logger.info(f"✓ Выбран лучший кандидат: '{best_candidate['artistName']} - {best_candidate['trackName']}' (ID: {best_candidate['id']})")
        
        return best_candidate
    
    def _lrc_to_plain(self, lyrics_lrc: str) -> str:
        """Преобразование LRC в обычный текст (удаление таймкодов)"""
        if not lyrics_lrc:
            return ""
        text_no_timestamps = re.sub(r'\[\d{2}:\d{2}\.\d{2,3}\]', '', lyrics_lrc)
        text_no_karaoke = re.sub(r'<\d{2}:\d{2}\.\d{2,3}>', '', text_no_timestamps)
        return "\n".join(line.strip() for line in text_no_karaoke.splitlines() if line.strip())
    
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
