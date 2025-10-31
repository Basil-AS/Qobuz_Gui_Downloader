"""
Модуль для встраивания метаданных в аудиофайлы
"""
import logging
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple

try:
    from mutagen.flac import FLAC, Picture
    from mutagen.mp3 import MP3
    from mutagen.id3 import (ID3, APIC, TIT2, TPE1, TALB, TDRC, TCON, TRCK, 
                             TPE2, SYLT, USLT, TSRC, TCOP, TPUB, COMM)
    from mutagen.id3._util import ID3NoHeaderError
    import mutagen.flac
    METADATA_AVAILABLE = True
except ImportError:
    METADATA_AVAILABLE = False
    logging.warning("Библиотеки для метаданных не установлены. Установите: pip install mutagen")

logger = logging.getLogger(__name__)


class MetadataWriter:
    """Класс для записи метаданных в аудиофайлы"""
    
    def __init__(self, settings: Dict):
        """
        Args:
            settings: словарь с настройками (какие теги встраивать)
        """
        self.settings = settings
    
    def embed_metadata(self, file_path: Path, track_meta: Dict, 
                       lyrics_plain: Optional[str] = None,
                       lyrics_lrc: Optional[str] = None,
                       cover_data: Optional[bytes] = None) -> bool:
        """
        Встраивание метаданных в аудиофайл
        
        Args:
            file_path: путь к файлу
            track_meta: метаданные трека от Qobuz API
            lyrics_plain: обычный текст песни
            lyrics_lrc: синхронизированный текст (LRC)
            cover_data: данные обложки (JPEG)
        
        Returns:
            True если успешно
        """
        if not METADATA_AVAILABLE:
            logger.error("Библиотеки для метаданных недоступны")
            return False
        
        file_ext = file_path.suffix.lower()
        
        if file_ext == '.flac':
            return self._embed_flac(file_path, track_meta, lyrics_plain, lyrics_lrc, cover_data)
        elif file_ext == '.mp3':
            return self._embed_mp3(file_path, track_meta, lyrics_plain, lyrics_lrc, cover_data)
        else:
            logger.warning(f"Неподдерживаемый формат файла: {file_ext}")
            return False
    
    def _embed_flac(self, file_path: Path, track_meta: Dict, 
                    lyrics_plain: Optional[str] = None,
                    lyrics_lrc: Optional[str] = None,
                    cover_data: Optional[bytes] = None) -> bool:
        """Встраивание метаданных в FLAC"""
        try:
            audio = FLAC(file_path)
            audio.clear()
            
            # Основные теги
            if self.settings.get('tag_title', True) and track_meta.get('title'):
                # Добавляем version к названию, если есть
                title = track_meta['title']
                version = track_meta.get('version')
                if version:
                    title = f"{title} ({version})"
                audio['TITLE'] = title
            
            if self.settings.get('tag_artist', True):
                if track_meta.get('performer', {}).get('name'):
                    audio['ARTIST'] = track_meta['performer']['name']
                    audio['ALBUMARTIST'] = track_meta['performer']['name']
                elif track_meta.get('album', {}).get('artist', {}).get('name'):
                    audio['ARTIST'] = track_meta['album']['artist']['name']
                    audio['ALBUMARTIST'] = track_meta['album']['artist']['name']
            
            if self.settings.get('tag_album', True) and track_meta.get('album', {}).get('title'):
                audio['ALBUM'] = track_meta['album']['title']
            
            if self.settings.get('tag_tracknumber', True) and track_meta.get('track_number'):
                audio['TRACKNUMBER'] = str(track_meta['track_number'])
            
            if self.settings.get('tag_year', True):
                if track_meta.get('album', {}).get('release_date_original'):
                    year = track_meta['album']['release_date_original'][:4]
                    audio['DATE'] = year
            
            if self.settings.get('tag_genre', True) and track_meta.get('album', {}).get('genre', {}).get('name'):
                audio['GENRE'] = track_meta['album']['genre']['name']
            
            # Расширенные теги
            if self.settings.get('tag_isrc', True) and track_meta.get('isrc'):
                audio['ISRC'] = track_meta['isrc']
            
            if self.settings.get('tag_upc', True) and track_meta.get('album', {}).get('upc'):
                audio['BARCODE'] = track_meta['album']['upc']
            
            if self.settings.get('tag_copyright', True) and track_meta.get('copyright'):
                audio['COPYRIGHT'] = track_meta['copyright']
            
            if self.settings.get('tag_label', True) and track_meta.get('album', {}).get('label', {}).get('name'):
                audio['LABEL'] = track_meta['album']['label']['name']
            
            if self.settings.get('tag_release_type', True) and track_meta.get('album', {}).get('release_type'):
                audio['RELEASETYPE'] = track_meta['album']['release_type']
            
            if self.settings.get('tag_explicit', True) and track_meta.get('parental_warning'):
                audio['EXPLICIT'] = '1' if track_meta['parental_warning'] else '0'
            
            if self.settings.get('tag_composer', True) and track_meta.get('composer', {}).get('name'):
                audio['COMPOSER'] = track_meta['composer']['name']
            
            # Тексты песен
            if self.settings.get('lyrics_enable', True):
                # Предпочитаем LRC, если доступен
                if lyrics_lrc:
                    audio['LYRICS'] = lyrics_lrc
                    logger.info("✓ LRC текст встроен в FLAC")
                elif lyrics_plain:
                    audio['LYRICS'] = lyrics_plain
                    logger.info("✓ Обычный текст встроен в FLAC")
            
            # Обложка
            if self.settings.get('download_cover', True) and cover_data:
                picture = mutagen.flac.Picture()
                picture.type = 3  # Cover (front)
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                picture.data = cover_data
                audio.add_picture(picture)
                logger.info("✓ Обложка встроена в FLAC")
            
            audio.save()
            logger.info(f"✓ Метаданные сохранены: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Ошибка записи метаданных FLAC: {e}")
            return False
    
    def _embed_mp3(self, file_path: Path, track_meta: Dict,
                   lyrics_plain: Optional[str] = None,
                   lyrics_lrc: Optional[str] = None,
                   cover_data: Optional[bytes] = None) -> bool:
        """Встраивание метаданных в MP3"""
        try:
            # Загружаем MP3
            try:
                audio = MP3(file_path, ID3=ID3)
            except ID3NoHeaderError:
                audio = MP3(file_path)
                audio.add_tags()
            
            audio.delete()
            audio.add_tags()
            
            # Основные теги
            if self.settings.get('tag_title', True) and track_meta.get('title'):
                # Добавляем version к названию, если есть
                title = track_meta['title']
                version = track_meta.get('version')
                if version:
                    title = f"{title} ({version})"
                audio.tags.add(TIT2(encoding=3, text=title))
            
            if self.settings.get('tag_artist', True):
                artist_name = None
                if track_meta.get('performer', {}).get('name'):
                    artist_name = track_meta['performer']['name']
                elif track_meta.get('album', {}).get('artist', {}).get('name'):
                    artist_name = track_meta['album']['artist']['name']
                
                if artist_name:
                    audio.tags.add(TPE1(encoding=3, text=artist_name))
                    audio.tags.add(TPE2(encoding=3, text=artist_name))
            
            if self.settings.get('tag_album', True) and track_meta.get('album', {}).get('title'):
                audio.tags.add(TALB(encoding=3, text=track_meta['album']['title']))
            
            if self.settings.get('tag_tracknumber', True) and track_meta.get('track_number'):
                audio.tags.add(TRCK(encoding=3, text=str(track_meta['track_number'])))
            
            if self.settings.get('tag_year', True):
                if track_meta.get('album', {}).get('release_date_original'):
                    year = track_meta['album']['release_date_original'][:4]
                    audio.tags.add(TDRC(encoding=3, text=year))
            
            if self.settings.get('tag_genre', True) and track_meta.get('album', {}).get('genre', {}).get('name'):
                audio.tags.add(TCON(encoding=3, text=track_meta['album']['genre']['name']))
            
            # Расширенные теги
            if self.settings.get('tag_isrc', True) and track_meta.get('isrc'):
                audio.tags.add(TSRC(encoding=3, text=track_meta['isrc']))
            
            if self.settings.get('tag_copyright', True) and track_meta.get('copyright'):
                audio.tags.add(TCOP(encoding=3, text=track_meta['copyright']))
            
            if self.settings.get('tag_label', True) and track_meta.get('album', {}).get('label', {}).get('name'):
                audio.tags.add(TPUB(encoding=3, text=track_meta['album']['label']['name']))
            
            # Дополнительная информация через COMM
            comments = []
            if self.settings.get('tag_upc', True) and track_meta.get('album', {}).get('upc'):
                comments.append(f"UPC: {track_meta['album']['upc']}")
            if self.settings.get('tag_release_type', True) and track_meta.get('album', {}).get('release_type'):
                comments.append(f"Release Type: {track_meta['album']['release_type']}")
            if self.settings.get('tag_explicit', True) and track_meta.get('parental_warning'):
                comments.append(f"Explicit: {'Yes' if track_meta['parental_warning'] else 'No'}")
            
            if comments:
                audio.tags.add(COMM(encoding=3, lang='eng', desc='', text='\n'.join(comments)))
            
            # Тексты песен
            if self.settings.get('lyrics_enable', True):
                if lyrics_lrc:
                    # Встраиваем SYLT (синхронизированный текст)
                    sylt_items = self._parse_lrc_for_sylt(lyrics_lrc)
                    if sylt_items:
                        audio.tags.add(SYLT(encoding=3, lang='eng', format=2, type=1, desc='', text=sylt_items))
                        logger.info("✓ Синхронизированный текст (SYLT) встроен в MP3")
                    
                    # Дублируем как USLT для видимости
                    audio.tags.add(USLT(encoding=3, lang='eng', desc='LRC', text=lyrics_lrc))
                    logger.info("✓ LRC текст встроен в MP3 (USLT)")
                    
                elif lyrics_plain:
                    audio.tags.add(USLT(encoding=3, lang='eng', desc='', text=lyrics_plain))
                    logger.info("✓ Обычный текст встроен в MP3")
            
            # Обложка
            if self.settings.get('download_cover', True) and cover_data:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=cover_data
                ))
                logger.info("✓ Обложка встроена в MP3")
            
            audio.save()
            logger.info(f"✓ Метаданные сохранены: {file_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"✗ Ошибка записи метаданных MP3: {e}")
            return False
    
    def _parse_lrc_for_sylt(self, lyrics_lrc: str) -> List[Tuple[str, int]]:
        """Парсинг LRC для формата SYLT"""
        sylt_items = []
        time_pattern = re.compile(r"\[(\d{1,2}):(\d{2})(?:[\.:](\d{1,2}))?\]")
        
        for raw_line in lyrics_lrc.splitlines():
            if not raw_line.strip():
                continue
            times = list(time_pattern.finditer(raw_line))
            if not times:
                continue
            
            text = time_pattern.sub("", raw_line).strip() or "♪"
            
            for m in times:
                mm = int(m.group(1) or 0)
                ss = int(m.group(2) or 0)
                ff = int(m.group(3) or 0)
                ms = ff * 10 if ff < 10 else ff if ff < 100 else 0
                total_ms = (mm * 60 + ss) * 1000 + ms
                sylt_items.append((text, total_ms))
        
        return sylt_items
