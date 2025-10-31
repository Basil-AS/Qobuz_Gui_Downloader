"""
Модуль для скачивания музыки с Qobuz
"""
import os
import re
import string
import requests
import logging
from pathlib import Path
from typing import Dict, Callable, Optional
from core.metadata import MetadataWriter
from core.lyrics_search import LyricsSearcher


logger = logging.getLogger(__name__)


class PartialFormatter(string.Formatter):
    """Форматтер для шаблонов с пропущенными значениями"""
    
    def __init__(self, missing="", bad_fmt=""):
        self.missing, self.bad_fmt = missing, bad_fmt
    
    def get_field(self, field_name, args, kwargs):
        try:
            val = super().get_field(field_name, args, kwargs)
        except (KeyError, AttributeError):
            val = None, field_name
        return val
    
    def format_field(self, value, spec):
        if not value:
            return self.missing
        try:
            return super().format_field(value, spec)
        except ValueError:
            if self.bad_fmt:
                return self.bad_fmt
            raise


def sanitize_filename(filename: str) -> str:
    """Очистка имени файла от недопустимых символов"""
    # Заменяем недопустимые символы для Windows
    invalid_chars = r'<>:"/\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Удаляем точки в конце (Windows не любит)
    filename = filename.rstrip('.')
    return filename


def get_url_info(url: str):
    """
    Извлечение типа и ID из URL Qobuz.
    Поддерживает URL со скобками в названии, например:
    https://www.qobuz.com/us-en/album/song-title-(remastered)/abc123def
    """
    r = re.search(
        r"(?:https?:\/\/(?:w{3}|open|play)\.qobuz\.com)?(?:\/[a-z]{2}-[a-z]{2})"
        r"?\/(album|artist|track|playlist|label)(?:\/[-\w\d\s.,'%()]+)?\/([\w\d]+)",
        url,
    )
    if r:
        return r.groups()
    return None, None


class QobuzDownloader:
    """Класс для скачивания с Qobuz"""
    
    # Соответствие индекса качества и format_id
    QUALITY_MAP = {
        0: 5,   # MP3 320
        1: 6,   # FLAC 16/44.1
        2: 7,   # FLAC 24/96
        3: 27,  # FLAC 24/192
    }
    
    def __init__(self, qobuz_client, settings: Dict, 
                 progress_callback: Callable = None,
                 log_callback: Callable = None):
        """
        Args:
            qobuz_client: клиент Qobuz API
            settings: настройки приложения
            progress_callback: функция для обновления прогресса
            log_callback: функция для логирования
        """
        self.client = qobuz_client
        self.settings = settings
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self._download_thread = None  # Ссылка на поток для проверки паузы
        
        # Логирование настроек для отладки
        self.log(f"🔧 Настройки загружены:")
        self.log(f"  • Сохранять LRC: {self.settings.get('lyrics_save_lrc', True)}")
        self.log(f"  • Сохранять SRT: {self.settings.get('lyrics_save_srt', False)}")
        self.log(f"  • Сохранять TXT: {self.settings.get('lyrics_save_txt', False)}")
        
        self.metadata_writer = MetadataWriter(settings)
        self.lyrics_searcher = LyricsSearcher()
        self.formatter = PartialFormatter()
        
        self.session = requests.Session()
    
    def check_pause(self):
        """Проверка паузы скачивания"""
        import time
        if self._download_thread and hasattr(self._download_thread, '_is_paused'):
            while self._download_thread._is_paused and self._download_thread._is_running:
                time.sleep(0.1)
            # Если отменили - выходим
            if not self._download_thread._is_running:
                raise InterruptedError("Скачивание отменено")
    
    def log(self, message: str):
        """Вывод сообщения в лог"""
        logger.info(message)
        if self.log_callback:
            self.log_callback(message)
    
    def update_progress(self, value: int):
        """Обновление прогресса"""
        if self.progress_callback:
            self.progress_callback(value)
    
    def create_m3u_playlist(self, folder: Path, track_files: list, playlist_name: str = "playlist"):
        """
        Создание M3U плейлиста
        
        Args:
            folder: папка где находятся треки
            track_files: список имён файлов треков
            playlist_name: имя плейлиста (без расширения)
        """
        if not self.settings.get('create_playlist', False):
            return
        
        try:
            m3u_path = folder / f"{sanitize_filename(playlist_name)}.m3u"
            
            with open(m3u_path, 'w', encoding='utf-8') as f:
                f.write("#EXTM3U\n")
                for track_file in track_files:
                    if track_file.exists():
                        # Относительный путь к файлу
                        f.write(f"{track_file.name}\n")
            
            self.log(f"📝 M3U плейлист создан: {m3u_path.name}")
        except Exception as e:
            self.log(f"⚠ Не удалось создать M3U плейлист: {e}")
    
    def download_url(self, url: str) -> bool:
        """
        Скачивание контента по URL
        
        Args:
            url: URL трека/альбома/плейлиста Qobuz
        
        Returns:
            True если успешно
        """
        try:
            url_type, url_id = get_url_info(url)
            
            if not url_type or not url_id:
                self.log("✗ Неверный URL Qobuz")
                return False
            
            self.log(f"📥 Определен тип: {url_type}, ID: {url_id}")
            
            if url_type == "track":
                return self.download_track_by_id(url_id)
            elif url_type == "album":
                return self.download_album(url_id)
            elif url_type == "artist":
                return self.download_artist(url_id)
            elif url_type == "playlist":
                return self.download_playlist(url_id)
            else:
                self.log(f"✗ Тип {url_type} пока не поддерживается")
                return False
                
        except Exception as e:
            self.log(f"✗ Ошибка: {str(e)}")
            logger.exception("Ошибка при скачивании")
            return False
    
    def download_album(self, album_id: str) -> bool:
        """Скачивание альбома"""
        try:
            self.log(f"📀 Получение информации об альбоме...")
            album_meta = self.client.get_album_meta(album_id)
            
            album_title = album_meta['title']
            artist_name = album_meta['artist']['name']
            tracks_count = len(album_meta['tracks']['items'])
            
            self.log(f"📀 Альбом: {artist_name} - {album_title}")
            self.log(f"📀 Треков: {tracks_count}")
            
            # Создаем папку для альбома
            album_folder = self.get_album_folder(album_meta)
            album_folder.mkdir(parents=True, exist_ok=True)
            self.log(f"📁 Папка: {album_folder}")
            
            # Скачиваем обложку
            cover_data = None
            if self.settings.get('download_cover', True):
                cover_data = self.download_cover(album_meta.get('image', {}).get('large'))
                if cover_data:
                    cover_path = album_folder / "cover.jpg"
                    cover_path.write_bytes(cover_data)
                    self.log("✓ Обложка сохранена")
            
            # Скачиваем треки
            downloaded_files = []
            for idx, track in enumerate(album_meta['tracks']['items'], 1):
                # Проверяем паузу/остановку перед каждым треком
                self.check_pause()
                
                self.log(f"\n🎵 [{idx}/{tracks_count}] {track.get('title', 'Unknown')}")
                
                # Обновляем прогресс
                progress = int((idx - 1) / tracks_count * 100)
                self.update_progress(progress)
                
                track_file = self.download_track(track, album_folder, album_meta, cover_data)
                if track_file:
                    downloaded_files.append(track_file)
            
            # Создаём M3U плейлист если включено
            if downloaded_files:
                self.create_m3u_playlist(
                    album_folder, 
                    downloaded_files, 
                    f"{artist_name} - {album_title}"
                )
            
            self.update_progress(100)
            self.log(f"\n✓ Альбом скачан успешно!")
            return True
            
        except Exception as e:
            self.log(f"✗ Ошибка при скачивании альбома: {str(e)}")
            logger.exception("Ошибка при скачивании альбома")
            return False
    
    def download_track_by_id(self, track_id: str) -> bool:
        """Скачивание одного трека по ID"""
        try:
            self.log(f"🎵 Получение информации о треке...")
            track_meta = self.client.get_track_meta(track_id)
            
            # Получаем информацию об альбоме для папки
            album_meta = track_meta.get('album', {})
            
            # Создаем папку
            if album_meta:
                folder = self.get_album_folder(album_meta)
            else:
                folder = Path(self.settings.get('download_folder', './downloads'))
            
            folder.mkdir(parents=True, exist_ok=True)
            
            # Скачиваем обложку
            cover_data = None
            if self.settings.get('download_cover', True) and album_meta:
                cover_data = self.download_cover(album_meta.get('image', {}).get('large'))
            
            self.download_track(track_meta, folder, album_meta, cover_data)
            
            self.update_progress(100)
            self.log(f"\n✓ Трек скачан успешно!")
            return True
            
        except Exception as e:
            self.log(f"✗ Ошибка при скачивании трека: {str(e)}")
            logger.exception("Ошибка при скачивании трека")
            return False
    
    def download_playlist(self, playlist_id: str) -> bool:
        """Скачивание плейлиста"""
        try:
            self.log(f"📋 Получение информации о плейлисте...")
            playlist_meta = self.client.get_playlist_meta(playlist_id)
            
            playlist_title = playlist_meta['name']
            tracks_count = len(playlist_meta['tracks']['items'])
            
            self.log(f"📋 Плейлист: {playlist_title}")
            self.log(f"📋 Треков: {tracks_count}")
            
            # Создаем папку для плейлиста
            base_folder = Path(self.settings.get('download_folder', './downloads'))
            playlist_folder = base_folder / sanitize_filename(playlist_title)
            playlist_folder.mkdir(parents=True, exist_ok=True)
            
            # Скачиваем треки
            downloaded_files = []
            for idx, track in enumerate(playlist_meta['tracks']['items'], 1):
                # Проверяем паузу/остановку перед каждым треком
                self.check_pause()
                
                self.log(f"\n🎵 [{idx}/{tracks_count}] {track.get('title', 'Unknown')}")
                
                progress = int((idx - 1) / tracks_count * 100)
                self.update_progress(progress)
                
                # Для плейлиста используем общую папку
                album_meta = track.get('album', {})
                cover_data = None
                if self.settings.get('download_cover', True) and album_meta:
                    cover_data = self.download_cover(album_meta.get('image', {}).get('large'))
                
                track_file = self.download_track(track, playlist_folder, album_meta, cover_data)
                if track_file:
                    downloaded_files.append(track_file)
            
            # Создаём M3U плейлист если включено
            if downloaded_files:
                self.create_m3u_playlist(
                    playlist_folder,
                    downloaded_files,
                    playlist_title
                )
            
            self.update_progress(100)
            self.log(f"\n✓ Плейлист скачан успешно!")
            return True
            
        except Exception as e:
            self.log(f"✗ Ошибка при скачивании плейлиста: {str(e)}")
            logger.exception("Ошибка при скачивании плейлиста")
            return False
    
    def download_track(self, track_meta: Dict, folder: Path, 
                      album_meta: Dict = None, cover_data: bytes = None) -> Optional[Path]:
        """
        Скачивание одного трека
        
        Returns:
            Path к скачанному файлу или None в случае ошибки
        """
        try:
            track_id = track_meta['id']
            
            # Определяем качество
            quality_index = self.settings.get('quality_index', 1)
            format_id = self.QUALITY_MAP.get(quality_index, 6)
            
            # Получаем URL для скачивания
            url_data = self.client.get_track_url(track_id, format_id)
            download_url = url_data.get('url')
            
            if not download_url:
                self.log("  ✗ Не удалось получить URL для скачивания")
                return None
            
            # Определяем расширение файла
            file_ext = '.flac' if format_id in [6, 7, 27] else '.mp3'
            
            # Формируем имя файла
            filename = self.get_track_filename(track_meta, album_meta) + file_ext
            file_path = folder / filename
            
            # Скачиваем файл
            self.log(f"  ⬇ Скачивание аудио...")
            self.download_file(download_url, file_path)
            self.log(f"  ✓ Аудио сохранено: {filename}")
            
            # Встраиваем метаданные
            self.log(f"  📝 Запись метаданных...")
            
            # Объединяем метаданные трека и альбома
            combined_meta = {**track_meta}
            if album_meta:
                combined_meta['album'] = album_meta
            
            # Поиск текстов
            lyrics_plain = None
            lyrics_lrc = None
            
            if self.settings.get('lyrics_enable', True):
                self.log(f"  🔍 Поиск текстов песни...")
                
                artist = track_meta.get('performer', {}).get('name') or \
                        album_meta.get('artist', {}).get('name', '') if album_meta else ''
                
                # Формируем полное название (с version если есть)
                title = track_meta.get('title', '')
                version = track_meta.get('version')
                if version:
                    title = f"{title} ({version})"
                
                album_title = album_meta.get('title', '') if album_meta else ''
                duration = track_meta.get('duration')
                
                if artist and title:
                    lyrics_plain, lyrics_lrc = self.lyrics_searcher.search_lyrics(
                        artist, title, album_title, duration
                    )
                    
                    if lyrics_lrc or lyrics_plain:
                        # Сохраняем файлы текстов
                        if self.settings.get('lyrics_save_lrc', True) and lyrics_lrc:
                            lrc_path = file_path.with_suffix('.lrc')
                            lrc_path.write_text(lyrics_lrc, encoding='utf-8')
                            self.log(f"  ✓ LRC файл сохранен")
                        
                        if self.settings.get('lyrics_save_srt', False) and lyrics_lrc:
                            srt_text = self.lyrics_searcher.lrc_to_srt(lyrics_lrc)
                            srt_path = file_path.with_suffix('.srt')
                            srt_path.write_text(srt_text, encoding='utf-8')
                            self.log(f"  ✓ SRT файл сохранен")
                        
                        if self.settings.get('lyrics_save_txt', False) and lyrics_plain:
                            txt_path = file_path.with_suffix('.txt')
                            txt_path.write_text(lyrics_plain, encoding='utf-8')
                            self.log(f"  ✓ TXT файл сохранен")
            
            # Записываем метаданные
            self.metadata_writer.embed_metadata(
                file_path, combined_meta, lyrics_plain, lyrics_lrc, cover_data
            )
            
            return file_path  # Возвращаем путь к скачанному файлу
            
        except Exception as e:
            self.log(f"  ✗ Ошибка: {str(e)}")
            logger.exception("Ошибка при скачивании трека")
            return None
    
    def download_file(self, url: str, path: Path):
        """Скачивание файла с прогрессом"""
        response = self.session.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(path, 'wb') as f:
            if total_size == 0:
                f.write(response.content)
            else:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
    
    def download_cover(self, cover_url: str) -> Optional[bytes]:
        """Скачивание обложки"""
        if not cover_url:
            return None
        
        try:
            # Qobuz использует шаблоны размеров
            if '{size}' in cover_url:
                cover_url = cover_url.replace('{size}', '600')
            
            response = self.session.get(cover_url, timeout=10)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.warning(f"Ошибка при скачивании обложки: {e}")
            return None
    
    def download_artist(self, artist_id: str) -> bool:
        """
        Скачивание всей дискографии артиста
        
        Args:
            artist_id: ID артиста на Qobuz
            
        Returns:
            True если хотя бы один альбом скачан успешно
        """
        try:
            self.log(f"👤 Получение информации об артисте...")
            
            # Получаем информацию об артисте
            artist_info = self.client.api_call("artist/get", id=artist_id)
            artist_name = artist_info.get('name', 'Unknown Artist')
            
            self.log(f"🎤 Артист: {artist_name}")
            
            # Получаем дискографию
            self.log(f"📀 Загрузка дискографии...")
            albums_data = self.client.api_call("artist/get", id=artist_id, extra="albums", limit=500)
            
            albums_list = albums_data.get('albums', {}).get('items', [])
            
            if not albums_list:
                self.log(f"✗ У артиста не найдено альбомов")
                return False
            
            total_albums = len(albums_list)
            self.log(f"📚 Найдено альбомов: {total_albums}")
            
            # Фильтруем дубликаты (разные версии одного альбома)
            unique_albums = {}
            for album in albums_list:
                title = album.get('title', '')
                # Используем комбинацию названия и года как ключ
                year = album.get('release_date_original', '')[:4] if album.get('release_date_original') else ''
                key = f"{title}_{year}"
                
                # Оставляем версию с максимальным качеством
                if key not in unique_albums:
                    unique_albums[key] = album
                else:
                    current_quality = unique_albums[key].get('maximum_bit_depth', 0)
                    new_quality = album.get('maximum_bit_depth', 0)
                    if new_quality > current_quality:
                        unique_albums[key] = album
            
            albums_to_download = list(unique_albums.values())
            self.log(f"📥 Уникальных альбомов для скачивания: {len(albums_to_download)}")
            
            # Скачиваем каждый альбом
            success_count = 0
            for i, album in enumerate(albums_to_download, 1):
                album_id = album.get('id')
                album_title = album.get('title', 'Unknown')
                
                self.log(f"\n[{i}/{len(albums_to_download)}] Скачивание: {album_title}")
                
                try:
                    if self.download_album(album_id):
                        success_count += 1
                        self.log(f"✓ Альбом {i}/{len(albums_to_download)} завершён")
                    else:
                        self.log(f"✗ Не удалось скачать альбом {i}/{len(albums_to_download)}")
                except Exception as e:
                    self.log(f"✗ Ошибка при скачивании альбома: {e}")
                    logger.exception(f"Ошибка при скачивании альбома {album_title}")
                
                # Обновляем общий прогресс
                progress = int((i / len(albums_to_download)) * 100)
                self.update_progress(progress)
            
            self.log(f"\n{'='*60}")
            self.log(f"✓ Скачивание артиста завершено!")
            self.log(f"📊 Успешно: {success_count}/{len(albums_to_download)} альбомов")
            
            return success_count > 0
            
        except Exception as e:
            self.log(f"✗ Ошибка при скачивании артиста: {str(e)}")
            logger.exception("Ошибка при скачивании артиста")
            return False
    
    def get_album_folder(self, album_meta: Dict) -> Path:
        """Создание пути к папке альбома на основе шаблона"""
        base_folder = Path(self.settings.get('download_folder', './downloads'))
        
        # Данные для шаблона
        template_data = {
            'artist': album_meta.get('artist', {}).get('name', 'Unknown Artist'),
            'album': album_meta.get('title', 'Unknown Album'),
            'year': album_meta.get('release_date_original', '')[:4] if album_meta.get('release_date_original') else '',
            'label': album_meta.get('label', {}).get('name', ''),
            'upc': album_meta.get('upc', ''),
        }
        
        folder_template = self.settings.get('folder_template', '{artist} - {album} ({year})')
        folder_name = self.formatter.format(folder_template, **template_data)
        folder_name = sanitize_filename(folder_name)
        
        return base_folder / folder_name
    
    def get_track_filename(self, track_meta: Dict, album_meta: Dict = None) -> str:
        """Создание имени файла трека на основе шаблона"""
        # Формируем полное название трека (с version если есть)
        title = track_meta.get('title', 'Unknown')
        version = track_meta.get('version')
        if version:
            title = f"{title} ({version})"
        
        template_data = {
            'artist': track_meta.get('performer', {}).get('name') or \
                     album_meta.get('artist', {}).get('name', 'Unknown') if album_meta else 'Unknown',
            'title': title,
            'tracknumber': str(track_meta.get('track_number', 0)).zfill(2),
            'album': album_meta.get('title', '') if album_meta else '',
            'year': album_meta.get('release_date_original', '')[:4] if album_meta and album_meta.get('release_date_original') else '',
            'genre': album_meta.get('genre', {}).get('name', '') if album_meta else '',
            'label': album_meta.get('label', {}).get('name', '') if album_meta else '',
            'isrc': track_meta.get('isrc', ''),
            'upc': album_meta.get('upc', '') if album_meta else '',
        }
        
        file_template = self.settings.get('file_template', '{tracknumber}. {artist} - {title}')
        filename = self.formatter.format(file_template, **template_data)
        filename = sanitize_filename(filename)
        
        return filename
