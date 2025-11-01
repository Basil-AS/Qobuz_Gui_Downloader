"""
Модуль локализации приложения
Поддержка английского (по умолчанию) и русского языков
"""
import locale
import logging

logger = logging.getLogger(__name__)


class Localization:
    """Класс для управления локализацией"""
    
    # Английский язык (по умолчанию)
    EN = {
        # Общие
        'app_name': 'Qobuz GUI Downloader',
        'ok': 'OK',
        'cancel': 'Cancel',
        'close': 'Close',
        'error': 'Error',
        'warning': 'Warning',
        'success': 'Success',
        'info': 'Information',
        
        # Окно логина
        'login_title': 'Login to Qobuz',
        'login_subtitle': 'Sign in to your Qobuz account',
        'login_email': 'Email:',
        'login_email_placeholder': 'Enter your email',
        'login_password': 'Password:',
        'login_password_placeholder': 'Enter your password',
        'login_toggle_password': 'Show/hide password',
        'login_button': 'Login',
        'login_authenticating': 'Authenticating...',
        'login_success': 'Login successful!',
        'login_error_title': 'Login Error',
        'login_error': 'Failed to login to Qobuz:',
        'login_fill_fields': 'Please fill in all fields',
        'login_note': 'Note: Requires paid Qobuz subscription',
        'cancel_button': 'Cancel',
        
        # Главное окно
        'app_title': 'Qobuz GUI Downloader',
        'url_label': 'Qobuz URL:',
        'url_placeholder': 'Paste link to track, album, artist or playlist...',
        'download_button': 'Download',
        'downloading': 'Downloading...',
        'pause_button': '⏸ Pause',
        'resume_button': '▶ Resume',
        'stop_button': '⏹ Stop',
        'settings_button': 'Settings',
        'logout_button': 'Logout',
        'exit_button': '✕ Exit',
        'progress_label': 'Progress:',
        'log_label': 'Process Log:',
        'status_ready': 'Ready',
        
        # Окно настроек
        'settings_title': 'Settings',
        'download_settings': 'Download Settings',
        'folder_label': 'Download Folder:',
        'browse_button': 'Browse',
        'quality_label': 'Audio Quality:',
        'quality_max': 'Maximum (up to 24/192)',
        'quality_cd': 'CD Quality (16/44.1)',
        'quality_high': 'High (MP3 320)',
        'quality_low': 'Low (MP3 128)',
        'cover_checkbox': 'Download cover art',
        'playlist_checkbox': 'Create M3U playlist',
        
        'naming_settings': 'File Naming',
        'folder_template_label': 'Folder Template:',
        'file_template_label': 'File Template:',
        'available_tags': 'Available tags: {artist}, {album}, {title}, {year}, {tracknumber}',
        
        'lyrics_settings': 'Lyrics Settings',
        'save_lrc_checkbox': 'Save synchronized lyrics (.lrc)',
        'save_srt_checkbox': 'Save subtitles (.srt)',
        'save_txt_checkbox': 'Save plain text (.txt)',
        
        'save_button': 'Save',
        'settings_saved': 'Settings saved successfully!',
        'settings_error': 'Failed to save settings',
        
        # О программе
        'about_title': 'About',
        'about_text': '''<h2>{app_name}</h2>
<p>Version: {version}</p>
<p>A GUI application for downloading music from Qobuz with high quality audio and lyrics support.</p>
<p><b>Features:</b></p>
<ul>
<li>Download albums, tracks, and playlists</li>
<li>High quality audio (up to 24-bit/192kHz)</li>
<li>Synchronized and plain lyrics</li>
<li>Automatic metadata tagging</li>
<li>M3U playlist creation</li>
</ul>
<p><b>GitHub:</b> <a href="{github_url}">{github_url}</a></p>
<p><b>License:</b> MIT</p>''',
        
        # Загрузчик
        'fetching_album': 'Fetching album information...',
        'fetching_track': 'Fetching track information...',
        'fetching_playlist': 'Fetching playlist information...',
        'album_info': 'Album: {artist} - {title}',
        'track_info': 'Track: {artist} - {title}',
        'playlist_info': 'Playlist: {title}',
        'tracks_count': 'Tracks: {count}',
        'folder_created': 'Folder: {path}',
        'cover_saved': 'Cover art saved',
        'downloading_audio': 'Downloading audio...',
        'audio_saved': 'Audio saved: {filename}',
        'writing_metadata': 'Writing metadata...',
        'searching_lyrics': 'Searching for lyrics...',
        'lyrics_found': 'Lyrics found',
        'lyrics_not_found': 'Lyrics not found',
        'lyrics_saved': 'Lyrics saved: {filename}',
        'playlist_created': 'M3U playlist created: {filename}',
        'album_downloaded': 'Album downloaded successfully!',
        'track_downloaded': 'Track downloaded successfully!',
        'playlist_downloaded': 'Playlist downloaded successfully!',
        'download_complete': 'Download completed successfully!',
        'instrumental_track': 'Instrumental track - skipping lyrics',
        'download_stopped': 'Download stopped by user',
        'download_starting': 'Starting: {url}',
        
        # Статусы
        'status_ready': 'Ready',
        'status_downloading': 'Downloading...',
        'status_paused': 'Paused',
        'status_stopped': 'Stopped',
        'status_resuming': 'Resuming...',
        'status_resumed': '▶ Download resumed',
        'status_stopping': '⏹ Stopping download...',
        
        # Настройки
        'settings_updated': '✓ Settings updated',
        'settings_saved': '💾 Settings saved',
        'error_save_settings': '⚠ Error saving settings: {error}',
        
        # Логаут
        'logout_title': 'Logout',
        'logout_confirm': 'Are you sure you want to logout from the current account?\n\nSaved credentials will be deleted.',
        'logout_success_title': 'Logged Out',
        'logout_success': 'You have been logged out.\nThe application will restart.',
        'credentials_deleted': '✓ Credentials deleted',
        'error_logout': 'Failed to logout:\n{error}',
        
        # Ошибки
        'error': 'Error',
        'error_occurred': 'Error: {error}',
        'auth_failed': 'Saved credentials are no longer valid.\n\nError: {error}\n\nPlease log in again.',
        'auth_failed_title': 'Authentication Error',
        'exiting': 'Exiting application',
        'error_no_url': '⚠ Error: Please enter a URL',
        'error_no_auth': '⚠ Error: Not logged in to Qobuz',
        'error_no_settings': '⚠ Error: Settings not loaded',
        
        # Подтверждения
        'confirm': 'Confirm',
        'confirm_stop': 'Are you sure you want to stop the download?',
        'confirm_exit': 'Download in progress. Stop and exit?',
    }
    
    # Русский язык
    RU = {
        # Общие
        'app_name': 'Qobuz GUI Downloader',
        'ok': 'OK',
        'cancel': 'Отмена',
        'close': 'Закрыть',
        'error': 'Ошибка',
        'warning': 'Предупреждение',
        'success': 'Успешно',
        'info': 'Информация',
        
        # Окно входа
        'login_title': 'Вход в Qobuz',
        'login_subtitle': 'Войдите в свой аккаунт Qobuz',
        'login_email': 'Email:',
        'login_email_placeholder': 'Введите ваш email',
        'login_password': 'Пароль:',
        'login_password_placeholder': 'Введите ваш пароль',
        'login_toggle_password': 'Показать/скрыть пароль',
        'login_button': 'Войти',
        'login_authenticating': 'Авторизация...',
        'login_success': 'Авторизация успешна!',
        'login_error_title': 'Ошибка авторизации',
        'login_error': 'Не удалось войти в Qobuz:',
        'login_fill_fields': 'Пожалуйста, заполните все поля',
        'login_note': 'Примечание: Требуется платная подписка Qobuz',
        'cancel_button': 'Отмена',
        
        # Главное окно
        'app_title': 'Qobuz GUI Downloader',
        'url_label': 'URL Qobuz:',
        'url_placeholder': 'Вставьте ссылку на трек, альбом, артиста или плейлист...',
        'download_button': 'Скачать',
        'downloading': 'Скачиваю...',
        'pause_button': '⏸ Пауза',
        'resume_button': '▶ Продолжить',
        'stop_button': '⏹ Стоп',
        'settings_button': 'Настройки',
        'logout_button': 'Выход из аккаунта',
        'exit_button': '✕ Выход',
        'progress_label': 'Прогресс:',
        'log_label': 'Лог процесса:',
        'status_ready': 'Готов к работе',
        
        # Окно настроек
        'settings_title': 'Настройки',
        'download_settings': 'Настройки загрузки',
        'folder_label': 'Папка загрузок:',
        'browse_button': 'Обзор',
        'quality_label': 'Качество аудио:',
        'quality_max': 'Максимальное (до 24/192)',
        'quality_cd': 'CD качество (16/44.1)',
        'quality_high': 'Высокое (MP3 320)',
        'quality_low': 'Низкое (MP3 128)',
        'cover_checkbox': 'Скачивать обложки',
        'playlist_checkbox': 'Создавать M3U плейлист',
        
        'naming_settings': 'Именование файлов',
        'folder_template_label': 'Шаблон папки:',
        'file_template_label': 'Шаблон файла:',
        'available_tags': 'Доступные теги: {artist}, {album}, {title}, {year}, {tracknumber}',
        
        'lyrics_settings': 'Настройки текстов',
        'save_lrc_checkbox': 'Сохранять синхронизированные тексты (.lrc)',
        'save_srt_checkbox': 'Сохранять субтитры (.srt)',
        'save_txt_checkbox': 'Сохранять обычный текст (.txt)',
        
        'save_button': 'Сохранить',
        'settings_saved': 'Настройки успешно сохранены!',
        'settings_error': 'Не удалось сохранить настройки',
        
        # О программе
        'about_title': 'О программе',
        'about_text': '''<h2>{app_name}</h2>
<p>Версия: {version}</p>
<p>GUI приложение для загрузки музыки из Qobuz с высоким качеством аудио и поддержкой текстов.</p>
<p><b>Возможности:</b></p>
<ul>
<li>Загрузка альбомов, треков и плейлистов</li>
<li>Высокое качество аудио (до 24-бит/192кГц)</li>
<li>Синхронизированные и обычные тексты песен</li>
<li>Автоматическая запись метаданных</li>
<li>Создание M3U плейлистов</li>
</ul>
<p><b>GitHub:</b> <a href="{github_url}">{github_url}</a></p>
<p><b>Лицензия:</b> MIT</p>''',
        
        # Загрузчик
        'fetching_album': 'Получение информации об альбоме...',
        'fetching_track': 'Получение информации о треке...',
        'fetching_playlist': 'Получение информации о плейлисте...',
        'album_info': 'Альбом: {artist} - {title}',
        'track_info': 'Трек: {artist} - {title}',
        'playlist_info': 'Плейлист: {title}',
        'tracks_count': 'Треков: {count}',
        'folder_created': 'Папка: {path}',
        'cover_saved': 'Обложка сохранена',
        'downloading_audio': 'Скачивание аудио...',
        'audio_saved': 'Аудио сохранено: {filename}',
        'writing_metadata': 'Запись метаданных...',
        'searching_lyrics': 'Поиск текстов песни...',
        'lyrics_found': 'Текст найден',
        'lyrics_not_found': 'Текст не найден',
        'lyrics_saved': 'Текст сохранен: {filename}',
        'playlist_created': 'M3U плейлист создан: {filename}',
        'album_downloaded': 'Альбом скачан успешно!',
        'track_downloaded': 'Трек скачан успешно!',
        'playlist_downloaded': 'Плейлист скачан успешно!',
        'download_complete': 'Скачивание завершено успешно!',
        'instrumental_track': 'Инструментальный трек - пропускаем поиск текстов',
        'download_stopped': 'Скачивание прервано пользователем',
        'download_starting': 'Начинаю обработку: {url}',
        
        # Статусы
        'status_ready': 'Готов к работе',
        'status_downloading': 'Скачивание...',
        'status_paused': 'Приостановлено',
        'status_stopped': 'Остановлено',
        'status_resuming': 'Возобновление...',
        'status_resumed': '▶ Скачивание возобновлено',
        'status_stopping': '⏹ Остановка скачивания...',
        
        # Настройки
        'settings_updated': '✓ Настройки обновлены',
        'settings_saved': '💾 Настройки сохранены',
        'error_save_settings': '⚠ Ошибка сохранения настроек: {error}',
        
        # Логаут
        'logout_title': 'Выход из аккаунта',
        'logout_confirm': 'Вы уверены, что хотите выйти из текущего аккаунта?\n\nСохранённые учетные данные будут удалены.',
        'logout_success_title': 'Выход выполнен',
        'logout_success': 'Вы вышли из аккаунта.\nПриложение будет перезапущено.',
        'credentials_deleted': '✓ Учетные данные удалены',
        'error_logout': 'Не удалось выполнить выход:\n{error}',
        
        # Ошибки
        'error': 'Ошибка',
        'error_occurred': 'Ошибка: {error}',
        'auth_failed': 'Сохранённые учетные данные больше не действительны.\n\nОшибка: {error}\n\nПожалуйста, войдите заново.',
        'auth_failed_title': 'Ошибка авторизации',
        'exiting': 'Выход из приложения',
        'error_no_url': '⚠ Ошибка: Введите URL',
        'error_no_auth': '⚠ Ошибка: Нет авторизации в Qobuz',
        'error_no_settings': '⚠ Ошибка: Настройки не загружены',
        
        # Подтверждения
        'confirm': 'Подтверждение',
        'confirm_stop': 'Вы уверены, что хотите остановить скачивание?',
        'confirm_exit': 'Идёт скачивание. Прервать и выйти?',
    }
    
    def __init__(self):
        """Инициализация с автоопределением языка системы"""
        self.current_lang = self._detect_system_language()
        logger.info(f"✓ Локализация инициализирована: {self.current_lang}")
    
    def _detect_system_language(self) -> str:
        """Определение языка системы"""
        try:
            system_locale = locale.getdefaultlocale()[0]
            if system_locale:
                # Если язык системы русский
                if system_locale.startswith('ru'):
                    return 'ru'
        except Exception as e:
            logger.warning(f"Не удалось определить язык системы: {e}")
        
        # По умолчанию английский
        return 'en'
    
    def set_language(self, lang: str):
        """Установка языка вручную"""
        if lang in ['en', 'ru']:
            self.current_lang = lang
            logger.info(f"✓ Язык изменен на: {lang}")
        else:
            logger.warning(f"Неизвестный язык: {lang}, используется английский")
            self.current_lang = 'en'
    
    def get(self, key: str, **kwargs) -> str:
        """
        Получение локализованной строки
        
        Args:
            key: ключ строки
            **kwargs: параметры для форматирования строки
        
        Returns:
            Локализованная строка
        """
        # Выбираем словарь языка
        lang_dict = self.RU if self.current_lang == 'ru' else self.EN
        
        # Получаем строку
        text = lang_dict.get(key, key)
        
        # Форматируем если есть параметры
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                logger.warning(f"Отсутствует параметр форматирования: {e}")
        
        return text
    
    def __call__(self, key: str, **kwargs) -> str:
        """Короткий синтаксис: t('key') вместо t.get('key')"""
        return self.get(key, **kwargs)


# Глобальный экземпляр локализации
_localization = None


def get_localization() -> Localization:
    """Получение глобального экземпляра локализации"""
    global _localization
    if _localization is None:
        _localization = Localization()
    return _localization


# Короткий алиас для удобства
def t(key: str, **kwargs) -> str:
    """
    Короткая функция для получения локализованных строк
    
    Пример:
        from core.localization import t
        print(t('login_button'))  # 'Login' или 'Войти'
    """
    return get_localization().get(key, **kwargs)
