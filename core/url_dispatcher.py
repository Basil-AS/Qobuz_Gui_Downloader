"""
Универсальный диспетчер URL для обработки различных типов контента Qobuz
"""
import re
import os
from typing import List, Tuple, Optional, Callable
import logging

logger = logging.getLogger(__name__)


def get_url_info(url: str) -> Optional[Tuple[str, str]]:
    """
    Извлекает тип контента (album, track, artist и т.д.) и его ID из любой ссылки Qobuz.
    
    Args:
        url: Строка, предположительно содержащая URL
        
    Returns:
        Кортеж (content_type, content_id) или None, если ссылка не распознана
        
    Examples:
        >>> get_url_info("https://play.qobuz.com/album/xjbxh1dc3xyb")
        ('album', 'xjbxh1dc3xyb')
        
        >>> get_url_info("https://www.qobuz.com/us-en/artist/pink-floyd/45749")
        ('artist', '45749')
    """
    # Регулярное выражение покрывает форматы:
    # - https://play.qobuz.com/album/id
    # - https://open.qobuz.com/track/id
    # - https://www.qobuz.com/xx-xx/artist/name/id
    # - и другие вариации
    pattern = re.compile(
        r"(?:https?://)?(?:www\.|open\.|play\.)?qobuz\.com(?:/[a-z]{2}-[a-z]{2})?/"
        r"(album|artist|track|playlist|label)(?:/[\w\d\-.,'%()]+)?/([\w\d]+)"
    )
    match = pattern.search(url)
    
    if match:
        content_type = match.group(1)
        content_id = match.group(2)
        logger.debug(f"Распознан URL: type={content_type}, id={content_id}")
        return content_type, content_id
    
    logger.warning(f"URL не распознан: {url}")
    return None


def parse_sources(sources_list: List[str]) -> List[str]:
    """
    Принимает список строк и раскрывает их в плоский список URL.
    Если строка - это путь к файлу, читает URL из него.
    
    Args:
        sources_list: Список строк (URL или пути к файлам)
        
    Returns:
        Плоский список всех URL для обработки
        
    Examples:
        >>> parse_sources(["https://play.qobuz.com/album/abc", "links.txt"])
        ['https://play.qobuz.com/album/abc', 'https://...', '...']
    """
    urls_to_process = []
    
    for source in sources_list:
        source = source.strip()
        if not source:
            continue
        
        # Проверяем, является ли источник путем к существующему файлу
        if os.path.isfile(source):
            logger.info(f"Чтение URL из файла: {source}")
            try:
                with open(source, 'r', encoding='utf-8') as f:
                    # Читаем строки, игнорируем пустые и закомментированные
                    lines = [
                        line.strip() 
                        for line in f 
                        if line.strip() and not line.strip().startswith('#')
                    ]
                    urls_to_process.extend(lines)
                    logger.info(f"Прочитано {len(lines)} URL из файла")
            except Exception as e:
                logger.error(f"Не удалось прочитать файл {source}: {e}")
        else:
            # Считаем, что это URL
            urls_to_process.append(source)
            
    return urls_to_process


class UrlDispatcher:
    """
    Диспетчер для управления задачами скачивания различных типов контента.
    
    Attributes:
        downloader: Экземпляр QobuzDownloader для выполнения скачивания
        handlers: Словарь-маршрутизатор для разных типов контента
    """
    
    def __init__(self, downloader=None):
        """
        Args:
            downloader: Экземпляр QobuzDownloader (опционально)
        """
        self.downloader = downloader
        
        # Словарь-маршрутизатор: связывает тип контента с функцией-обработчиком
        self.handlers = {
            'album': self.handle_album,
            'track': self.handle_track,
            'artist': self.handle_artist,
            'playlist': self.handle_playlist,
            'label': self.handle_label,
        }
    
    # --- Обработчики для разных типов контента ---
    
    def handle_album(self, item_id: str) -> bool:
        """Обработка альбома"""
        logger.info(f"Запуск скачивания АЛЬБОМА с ID: {item_id}")
        if self.downloader:
            return self.downloader.download_album(item_id)
        return False
    
    def handle_track(self, item_id: str) -> bool:
        """Обработка трека"""
        logger.info(f"Запуск скачивания ТРЕКА с ID: {item_id}")
        if self.downloader:
            return self.downloader.download_track(item_id)
        return False
    
    def handle_artist(self, item_id: str) -> bool:
        """Обработка артиста (вся дискография)"""
        logger.info(f"Запуск скачивания АРТИСТА с ID: {item_id}")
        if self.downloader:
            return self.downloader.download_artist(item_id)
        return False
    
    def handle_playlist(self, item_id: str) -> bool:
        """Обработка плейлиста"""
        logger.info(f"Запуск скачивания ПЛЕЙЛИСТА с ID: {item_id}")
        if self.downloader:
            return self.downloader.download_playlist(item_id)
        return False
    
    def handle_label(self, item_id: str) -> bool:
        """Обработка лейбла"""
        logger.info(f"Запуск скачивания ЛЕЙБЛА с ID: {item_id}")
        if self.downloader:
            logger.warning("Скачивание лейблов пока не поддерживается")
        return False
    
    # --- Основной метод обработки ---
    
    def process_input(self, user_input: str) -> Tuple[int, int]:
        """
        Главный метод. Принимает строку от пользователя, обрабатывает и запускает задачи.
        
        Args:
            user_input: Строка с URL (одна или несколько, разделённых пробелами) или путь к файлу
            
        Returns:
            Кортеж (успешно_обработано, всего_найдено)
            
        Examples:
            >>> dispatcher.process_input("https://play.qobuz.com/album/abc123")
            (1, 1)
            
            >>> dispatcher.process_input("links.txt https://play.qobuz.com/track/xyz")
            (5, 5)
        """
        logger.info("=" * 60)
        logger.info(f"Получен ввод: \"{user_input[:100]}...\"" if len(user_input) > 100 else f"Получен ввод: \"{user_input}\"")
        
        # Разделяем ввод по пробелам, чтобы получить список источников
        sources_list = user_input.split()
        
        # Получаем полный список URL для обработки
        urls = parse_sources(sources_list)
        
        if not urls:
            logger.info("Не найдено валидных URL для обработки")
            return 0, 0
        
        logger.info(f"Найдено {len(urls)} URL для обработки")
        
        success_count = 0
        
        # Обрабатываем каждый URL
        for i, url in enumerate(urls, 1):
            logger.info(f"[{i}/{len(urls)}] Обработка URL: {url}")
            
            url_info = get_url_info(url)
            
            if url_info:
                content_type, content_id = url_info
                
                # Ищем подходящий обработчик в нашем словаре
                handler = self.handlers.get(content_type)
                
                if handler:
                    # Вызываем найденный обработчик, передавая ему ID
                    try:
                        if handler(content_id):
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Ошибка при обработке {content_type} {content_id}: {e}")
                else:
                    logger.error(f"Неизвестный тип контента: {content_type}")
            else:
                logger.warning(f"Строка не является распознаваемой ссылкой Qobuz: \"{url}\"")
        
        logger.info(f"Обработка завершена: {success_count}/{len(urls)} успешно")
        return success_count, len(urls)
    
    def process_url(self, url: str) -> bool:
        """
        Обработка одного URL (упрощённый метод для GUI).
        
        Args:
            url: Одна ссылка Qobuz
            
        Returns:
            True если обработка успешна, False иначе
        """
        url_info = get_url_info(url)
        
        if not url_info:
            logger.error(f"Невалидный URL: {url}")
            return False
        
        content_type, content_id = url_info
        handler = self.handlers.get(content_type)
        
        if not handler:
            logger.error(f"Неподдерживаемый тип: {content_type}")
            return False
        
        try:
            return handler(content_id)
        except Exception as e:
            logger.error(f"Ошибка при обработке: {e}")
            return False
