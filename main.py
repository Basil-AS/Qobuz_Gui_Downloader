"""
Qobuz GUI Downloader
Главный файл приложения
"""
import sys
import json
import base64
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('qobuz_downloader.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class ConfigManager:
    """Менеджер конфигурации приложения"""
    
    def __init__(self):
        # Используем папку программы вместо домашней папки пользователя
        self.config_dir = Path(__file__).parent / "config"
        self.config_dir.mkdir(exist_ok=True)
        
        self.credentials_file = self.config_dir / "credentials.json"
        self.settings_file = self.config_dir / "settings.json"
    
    def load_credentials(self):
        """Загрузка учетных данных"""
        if not self.credentials_file.exists():
            return None, None
        
        try:
            with open(self.credentials_file, 'r') as f:
                data = json.load(f)
                email = data.get('email')
                encrypted_password = data.get('password')
                
                if email and encrypted_password:
                    # Расшифровываем пароль
                    password = base64.b64decode(encrypted_password.encode()).decode()
                    return email, password
        except Exception as e:
            logger.error(f"Ошибка при загрузке учетных данных: {e}")
        
        return None, None
    
    def load_settings(self):
        """Загрузка настроек"""
        if not self.settings_file.exists():
            return self.get_default_settings()
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                # Дополняем недостающие значения по умолчанию
                default = self.get_default_settings()
                for key, value in default.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            logger.error(f"Ошибка при загрузке настроек: {e}")
            return self.get_default_settings()
    
    def save_settings(self, settings):
        """Сохранение настроек"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Ошибка при сохранении настроек: {e}")
            return False
    
    def get_default_settings(self):
        """Настройки по умолчанию"""
        downloads_folder = str(Path.home() / "Music" / "Qobuz Downloads")
        
        return {
            # Скачивание
            'download_folder': downloads_folder,
            'quality_index': 1,  # FLAC 16/44.1
            'download_cover': True,
            'create_playlist': False,
            
            # Именование
            'folder_template': '{artist} - {album} ({year})',
            'file_template': '{tracknumber}. {artist} - {title}',
            
            # Метаданные - основные
            'tag_title': True,
            'tag_artist': True,
            'tag_album': True,
            'tag_tracknumber': True,
            'tag_year': True,
            'tag_genre': True,
            
            # Метаданные - расширенные
            'tag_upc': True,
            'tag_isrc': True,
            'tag_copyright': True,
            'tag_label': True,
            'tag_release_type': True,
            'tag_explicit': True,
            'tag_composer': True,
            
            # Тексты песен
            'lyrics_enable': True,
            'lyrics_save_lrc': True,
            'lyrics_save_srt': False,
            'lyrics_save_txt': False,
            'lyrics_prefer_synced': True,
            'lyrics_fallback': True,
        }
    
    def delete_credentials(self):
        """Удаление сохранённых учетных данных"""
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
                logger.info("Учетные данные удалены")
                return True
        except Exception as e:
            logger.error(f"Ошибка при удалении учетных данных: {e}")
        return False


def main():
    """Главная функция"""
    
    # Windows: установка App User Model ID для отдельной иконки в панели задач
    import platform
    if platform.system() == 'Windows':
        try:
            import ctypes
            # Устанавливаем уникальный AppID для приложения
            myappid = 'qobuzguidownloader.app.1.0.2'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            logger.info("✓ Windows AppUserModelID установлен")
        except Exception as e:
            logger.warning(f"⚠ Не удалось установить AppUserModelID: {e}")
    
    # Создаем приложение
    app = QApplication(sys.argv)
    app.setApplicationName("Qobuz GUI Downloader")
    app.setOrganizationName("QobuzGuiDownloader")
    
    # Устанавливаем иконку приложения (для окна и панели задач)
    # Приоритет: ICO (лучше для Windows) → PNG (fallback)
    icon_path = Path(__file__).parent / "resources" / "icon.ico"
    if not icon_path.exists():
        icon_path = Path(__file__).parent / "resources" / "icon.png"
    
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
        logger.info(f"✓ Иконка приложения установлена: {icon_path}")
    else:
        logger.warning(f"⚠ Иконка не найдена: {icon_path}")
    
    # Настраиваем стиль
    app.setStyle("Fusion")
    
    # Менеджер конфигурации
    config = ConfigManager()
    
    # Загружаем настройки
    settings = config.load_settings()
    
    # Проверяем учетные данные
    email, password = config.load_credentials()
    
    qobuz_client = None
    
    if email and password:
        # Пытаемся авторизоваться
        try:
            from gui.login_window import LoginWindow
            from core.qobuz_api import get_qobuz_client
            
            logger.info("Попытка автоматической авторизации...")
            qobuz_client = get_qobuz_client(email, password)
            logger.info(f"✓ Авторизован: {qobuz_client.label}")
            
        except Exception as e:
            logger.warning(f"Автоматическая авторизация не удалась: {e}")
            
            # Показываем сообщение и удаляем невалидные учетные данные
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(
                None,
                "Ошибка авторизации",
                f"Сохранённые учетные данные больше не действительны.\n\n"
                f"Ошибка: {str(e)}\n\n"
                f"Пожалуйста, войдите заново."
            )
            
            # Удаляем невалидные данные
            config.delete_credentials()
            qobuz_client = None
    
    # Если не авторизованы, показываем окно входа
    if not qobuz_client:
        from gui.login_window import LoginWindow
        
        login_window = LoginWindow()
        if login_window.exec():
            qobuz_client = login_window.get_client()
        else:
            # Пользователь отменил вход
            logger.info("Выход из приложения")
            return 0
    
    # Создаем главное окно
    from gui.main_window import MainWindow
    
    main_window = MainWindow(qobuz_client)
    main_window.set_settings(settings)
    
    # Сохраняем настройки при закрытии
    def save_settings_on_close():
        config.save_settings(main_window.settings)
    
    app.aboutToQuit.connect(save_settings_on_close)
    
    # Показываем окно
    main_window.show()
    
    logger.info("Приложение запущено")
    
    # Запускаем приложение
    return app.exec()


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        logger.exception("Критическая ошибка")
        QMessageBox.critical(None, "Ошибка", f"Критическая ошибка:\n{str(e)}")
        sys.exit(1)
