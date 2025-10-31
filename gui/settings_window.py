"""
Окно настроек приложения
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QWidget, QLabel, QLineEdit, QPushButton, QCheckBox,
                              QComboBox, QGroupBox, QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt


class SettingsWindow(QDialog):
    """Окно настроек приложения"""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings or {}
        self.init_ui()
        self.load_settings()
        self.connect_auto_save()  # Подключаем автосохранение
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Настройки")
        self.setMinimumSize(700, 600)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Вкладки настроек
        tabs = QTabWidget()
        
        # Вкладка "Скачивание"
        download_tab = self.create_download_tab()
        tabs.addTab(download_tab, "Скачивание")
        
        # Вкладка "Именование файлов"
        naming_tab = self.create_naming_tab()
        tabs.addTab(naming_tab, "Именование")
        
        # Вкладка "Метаданные"
        metadata_tab = self.create_metadata_tab()
        tabs.addTab(metadata_tab, "Метаданные")
        
        # Вкладка "Тексты песен"
        lyrics_tab = self.create_lyrics_tab()
        tabs.addTab(lyrics_tab, "Тексты песен")
        
        layout.addWidget(tabs)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        self.apply_styles()
        
    def create_download_tab(self):
        """Создание вкладки настроек скачивания"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Папка для сохранения
        folder_group = QGroupBox("Папка для сохранения")
        folder_layout = QHBoxLayout()
        
        self.download_folder = QLineEdit()
        self.download_folder.setPlaceholderText("Выберите папку...")
        
        browse_btn = QPushButton("Обзор...")
        browse_btn.clicked.connect(self.browse_folder)
        
        folder_layout.addWidget(self.download_folder)
        folder_layout.addWidget(browse_btn)
        folder_group.setLayout(folder_layout)
        
        layout.addWidget(folder_group)
        
        # Качество аудио
        quality_group = QGroupBox("Качество аудио")
        quality_layout = QVBoxLayout()
        
        quality_label = QLabel("Выберите формат и качество:")
        self.quality_combo = QComboBox()
        self.quality_combo.addItems([
            "MP3 320 kbps",
            "FLAC 16-bit/44.1kHz (CD Quality)",
            "FLAC 24-bit/96kHz (Hi-Res)",
            "FLAC 24-bit/192kHz (Hi-Res)"
        ])
        
        quality_layout.addWidget(quality_label)
        quality_layout.addWidget(self.quality_combo)
        quality_group.setLayout(quality_layout)
        
        layout.addWidget(quality_group)
        
        # Дополнительные опции
        options_group = QGroupBox("Дополнительные опции")
        options_layout = QVBoxLayout()
        
        self.download_cover = QCheckBox("Скачивать обложку альбома")
        self.download_cover.setChecked(True)
        
        self.create_playlist = QCheckBox("Создавать M3U плейлист")
        self.create_playlist.setChecked(False)
        
        options_layout.addWidget(self.download_cover)
        options_layout.addWidget(self.create_playlist)
        options_group.setLayout(options_layout)
        
        layout.addWidget(options_group)
        layout.addStretch()
        
        return widget
        
    def create_naming_tab(self):
        """Создание вкладки именования файлов"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Шаблоны
        templates_group = QGroupBox("Шаблоны именования")
        templates_layout = QVBoxLayout()
        
        # Шаблон папки альбома
        folder_label = QLabel("Шаблон папки альбома:")
        self.folder_template = QLineEdit()
        self.folder_template.setPlaceholderText("%artist% - %album% (%year%)")
        
        # Шаблон имени файла
        file_label = QLabel("Шаблон имени файла:")
        self.file_template = QLineEdit()
        self.file_template.setPlaceholderText("%tracknumber%. %artist% - %title%")
        
        templates_layout.addWidget(folder_label)
        templates_layout.addWidget(self.folder_template)
        templates_layout.addWidget(file_label)
        templates_layout.addWidget(self.file_template)
        templates_group.setLayout(templates_layout)
        
        layout.addWidget(templates_group)
        
        # Доступные переменные
        variables_group = QGroupBox("Доступные переменные")
        variables_layout = QVBoxLayout()
        
        variables_text = """
        %artist% - Имя исполнителя
        %album% - Название альбома
        %title% - Название трека
        %tracknumber% - Номер трека
        %year% - Год выпуска
        %genre% - Жанр
        %label% - Лейбл
        %upc% - UPC код
        %isrc% - ISRC код
        """
        
        variables_label = QLabel(variables_text)
        variables_layout.addWidget(variables_label)
        variables_group.setLayout(variables_layout)
        
        layout.addWidget(variables_group)
        layout.addStretch()
        
        return widget
        
    def create_metadata_tab(self):
        """Создание вкладки настроек метаданных"""
        widget = QWidget()
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Основные теги
        basic_group = QGroupBox("Основные теги")
        basic_layout = QVBoxLayout()
        
        self.tag_title = QCheckBox("Название трека (Title)")
        self.tag_title.setChecked(True)
        
        self.tag_artist = QCheckBox("Исполнитель (Artist)")
        self.tag_artist.setChecked(True)
        
        self.tag_album = QCheckBox("Альбом (Album)")
        self.tag_album.setChecked(True)
        
        self.tag_tracknumber = QCheckBox("Номер трека (Track Number)")
        self.tag_tracknumber.setChecked(True)
        
        self.tag_year = QCheckBox("Год (Year)")
        self.tag_year.setChecked(True)
        
        self.tag_genre = QCheckBox("Жанр (Genre)")
        self.tag_genre.setChecked(True)
        
        basic_layout.addWidget(self.tag_title)
        basic_layout.addWidget(self.tag_artist)
        basic_layout.addWidget(self.tag_album)
        basic_layout.addWidget(self.tag_tracknumber)
        basic_layout.addWidget(self.tag_year)
        basic_layout.addWidget(self.tag_genre)
        basic_group.setLayout(basic_layout)
        
        layout.addWidget(basic_group)
        
        # Расширенные теги
        extended_group = QGroupBox("Расширенные теги")
        extended_layout = QVBoxLayout()
        
        self.tag_upc = QCheckBox("UPC (Universal Product Code)")
        self.tag_upc.setChecked(True)
        
        self.tag_isrc = QCheckBox("ISRC (International Standard Recording Code)")
        self.tag_isrc.setChecked(True)
        
        self.tag_copyright = QCheckBox("Copyright")
        self.tag_copyright.setChecked(True)
        
        self.tag_label = QCheckBox("Лейбл (Label)")
        self.tag_label.setChecked(True)
        
        self.tag_release_type = QCheckBox("Тип релиза (Release Type)")
        self.tag_release_type.setChecked(True)
        
        self.tag_explicit = QCheckBox("Explicit (отметка о нецензурной лексике)")
        self.tag_explicit.setChecked(True)
        
        self.tag_composer = QCheckBox("Композитор (Composer)")
        self.tag_composer.setChecked(True)
        
        extended_layout.addWidget(self.tag_upc)
        extended_layout.addWidget(self.tag_isrc)
        extended_layout.addWidget(self.tag_copyright)
        extended_layout.addWidget(self.tag_label)
        extended_layout.addWidget(self.tag_release_type)
        extended_layout.addWidget(self.tag_explicit)
        extended_layout.addWidget(self.tag_composer)
        extended_group.setLayout(extended_layout)
        
        layout.addWidget(extended_group)
        layout.addStretch()
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.addWidget(scroll)
        scroll_widget.setLayout(scroll_layout)
        
        return scroll_widget
        
    def create_lyrics_tab(self):
        """Создание вкладки настроек текстов песен"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Основные настройки
        main_group = QGroupBox("Поиск и встраивание текстов")
        main_layout = QVBoxLayout()
        
        self.lyrics_enable = QCheckBox("Включить поиск и встраивание текстов")
        self.lyrics_enable.setChecked(True)
        self.lyrics_enable.stateChanged.connect(self.toggle_lyrics_options)
        
        main_layout.addWidget(self.lyrics_enable)
        main_group.setLayout(main_layout)
        
        layout.addWidget(main_group)
        
        # Опции сохранения
        save_group = QGroupBox("Опции сохранения")
        save_layout = QVBoxLayout()
        
        self.lyrics_save_lrc = QCheckBox("Сохранять .lrc файл рядом с аудиофайлом")
        self.lyrics_save_lrc.setChecked(True)
        
        self.lyrics_save_srt = QCheckBox("Создавать .srt файл для VLC")
        self.lyrics_save_srt.setChecked(False)
        
        self.lyrics_save_txt = QCheckBox("Сохранять обычный текст в .txt файл")
        self.lyrics_save_txt.setChecked(False)
        
        save_layout.addWidget(self.lyrics_save_lrc)
        save_layout.addWidget(self.lyrics_save_srt)
        save_layout.addWidget(self.lyrics_save_txt)
        save_group.setLayout(save_layout)
        
        layout.addWidget(save_group)
        
        # Настройки поиска
        search_group = QGroupBox("Настройки поиска")
        search_layout = QVBoxLayout()
        
        self.lyrics_prefer_synced = QCheckBox("Предпочитать синхронизированные тексты (LRC)")
        self.lyrics_prefer_synced.setChecked(True)
        
        self.lyrics_fallback = QCheckBox("Использовать обычные тексты, если синхронизированные не найдены")
        self.lyrics_fallback.setChecked(True)
        
        search_layout.addWidget(self.lyrics_prefer_synced)
        search_layout.addWidget(self.lyrics_fallback)
        search_group.setLayout(search_layout)
        
        layout.addWidget(search_group)
        layout.addStretch()
        
        return widget
        
    def toggle_lyrics_options(self, state):
        """Включение/отключение опций текстов песен"""
        enabled = state == Qt.CheckState.Checked.value
        self.lyrics_save_lrc.setEnabled(enabled)
        self.lyrics_save_srt.setEnabled(enabled)
        self.lyrics_save_txt.setEnabled(enabled)
        self.lyrics_prefer_synced.setEnabled(enabled)
        self.lyrics_fallback.setEnabled(enabled)
        
    def browse_folder(self):
        """Выбор папки для сохранения"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения")
        if folder:
            self.download_folder.setText(folder)
            
    def load_settings(self):
        """Загрузка настроек в UI"""
        # Скачивание
        self.download_folder.setText(self.settings.get('download_folder', ''))
        quality_index = self.settings.get('quality_index', 1)
        self.quality_combo.setCurrentIndex(quality_index)
        self.download_cover.setChecked(self.settings.get('download_cover', True))
        self.create_playlist.setChecked(self.settings.get('create_playlist', False))
        
        # Именование
        self.folder_template.setText(self.settings.get('folder_template', '%artist% - %album% (%year%)'))
        self.file_template.setText(self.settings.get('file_template', '%tracknumber%. %artist% - %title%'))
        
        # Метаданные - основные
        self.tag_title.setChecked(self.settings.get('tag_title', True))
        self.tag_artist.setChecked(self.settings.get('tag_artist', True))
        self.tag_album.setChecked(self.settings.get('tag_album', True))
        self.tag_tracknumber.setChecked(self.settings.get('tag_tracknumber', True))
        self.tag_year.setChecked(self.settings.get('tag_year', True))
        self.tag_genre.setChecked(self.settings.get('tag_genre', True))
        
        # Метаданные - расширенные
        self.tag_upc.setChecked(self.settings.get('tag_upc', True))
        self.tag_isrc.setChecked(self.settings.get('tag_isrc', True))
        self.tag_copyright.setChecked(self.settings.get('tag_copyright', True))
        self.tag_label.setChecked(self.settings.get('tag_label', True))
        self.tag_release_type.setChecked(self.settings.get('tag_release_type', True))
        self.tag_explicit.setChecked(self.settings.get('tag_explicit', True))
        self.tag_composer.setChecked(self.settings.get('tag_composer', True))
        
        # Тексты песен
        self.lyrics_enable.setChecked(self.settings.get('lyrics_enable', True))
        self.lyrics_save_lrc.setChecked(self.settings.get('lyrics_save_lrc', True))
        self.lyrics_save_srt.setChecked(self.settings.get('lyrics_save_srt', False))
        self.lyrics_save_txt.setChecked(self.settings.get('lyrics_save_txt', False))
        self.lyrics_prefer_synced.setChecked(self.settings.get('lyrics_prefer_synced', True))
        self.lyrics_fallback.setChecked(self.settings.get('lyrics_fallback', True))
        
    def get_settings(self):
        """Получение настроек из UI"""
        return {
            # Скачивание
            'download_folder': self.download_folder.text(),
            'quality_index': self.quality_combo.currentIndex(),
            'download_cover': self.download_cover.isChecked(),
            'create_playlist': self.create_playlist.isChecked(),
            
            # Именование
            'folder_template': self.folder_template.text(),
            'file_template': self.file_template.text(),
            
            # Метаданные - основные
            'tag_title': self.tag_title.isChecked(),
            'tag_artist': self.tag_artist.isChecked(),
            'tag_album': self.tag_album.isChecked(),
            'tag_tracknumber': self.tag_tracknumber.isChecked(),
            'tag_year': self.tag_year.isChecked(),
            'tag_genre': self.tag_genre.isChecked(),
            
            # Метаданные - расширенные
            'tag_upc': self.tag_upc.isChecked(),
            'tag_isrc': self.tag_isrc.isChecked(),
            'tag_copyright': self.tag_copyright.isChecked(),
            'tag_label': self.tag_label.isChecked(),
            'tag_release_type': self.tag_release_type.isChecked(),
            'tag_explicit': self.tag_explicit.isChecked(),
            'tag_composer': self.tag_composer.isChecked(),
            
            # Тексты песен
            'lyrics_enable': self.lyrics_enable.isChecked(),
            'lyrics_save_lrc': self.lyrics_save_lrc.isChecked(),
            'lyrics_save_srt': self.lyrics_save_srt.isChecked(),
            'lyrics_save_txt': self.lyrics_save_txt.isChecked(),
            'lyrics_prefer_synced': self.lyrics_prefer_synced.isChecked(),
            'lyrics_fallback': self.lyrics_fallback.isChecked(),
        }
    
    def connect_auto_save(self):
        """Подключение автосохранения для всех виджетов"""
        # QLineEdit
        self.download_folder.textChanged.connect(self.auto_save)
        self.folder_template.textChanged.connect(self.auto_save)
        self.file_template.textChanged.connect(self.auto_save)
        
        # QComboBox
        self.quality_combo.currentIndexChanged.connect(self.auto_save)
        
        # QCheckBox
        self.download_cover.stateChanged.connect(self.auto_save)
        self.create_playlist.stateChanged.connect(self.auto_save)
        
        self.tag_title.stateChanged.connect(self.auto_save)
        self.tag_artist.stateChanged.connect(self.auto_save)
        self.tag_album.stateChanged.connect(self.auto_save)
        self.tag_tracknumber.stateChanged.connect(self.auto_save)
        self.tag_year.stateChanged.connect(self.auto_save)
        self.tag_genre.stateChanged.connect(self.auto_save)
        
        self.tag_upc.stateChanged.connect(self.auto_save)
        self.tag_isrc.stateChanged.connect(self.auto_save)
        self.tag_copyright.stateChanged.connect(self.auto_save)
        self.tag_label.stateChanged.connect(self.auto_save)
        self.tag_release_type.stateChanged.connect(self.auto_save)
        self.tag_explicit.stateChanged.connect(self.auto_save)
        self.tag_composer.stateChanged.connect(self.auto_save)
        
        self.lyrics_enable.stateChanged.connect(self.auto_save)
        self.lyrics_save_lrc.stateChanged.connect(self.auto_save)
        self.lyrics_save_srt.stateChanged.connect(self.auto_save)
        self.lyrics_save_txt.stateChanged.connect(self.auto_save)
        self.lyrics_prefer_synced.stateChanged.connect(self.auto_save)
        self.lyrics_fallback.stateChanged.connect(self.auto_save)
    
    def auto_save(self):
        """Автоматическое сохранение настроек при изменении"""
        new_settings = self.get_settings()
        self.settings.update(new_settings)
        # Сохраняем в файл
        if hasattr(self.parent(), 'config_manager'):
            self.parent().config_manager.save_settings(self.settings)
        
    def apply_styles(self):
        """Применение стилей"""
        style = """
        QDialog {
            background-color: white;
        }
        QWidget {
            background-color: white;
        }
        QScrollArea {
            background-color: white;
            border: none;
        }
        QTabWidget::pane {
            background-color: white;
            border: 1px solid #ddd;
        }
        QTabBar::tab {
            background-color: #f0f0f0;
            color: #000000;
            padding: 8px 16px;
            border: 1px solid #ddd;
            border-bottom: none;
        }
        QTabBar::tab:selected {
            background-color: white;
            font-weight: bold;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #ddd;
            border-radius: 5px;
            margin-top: 10px;
            padding-top: 10px;
            color: #000000;
            background-color: white;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
            color: #000000;
        }
        QLabel {
            color: #000000;
        }
        QLineEdit {
            color: #000000;
            background-color: white;
        }
        QComboBox {
            color: #000000;
            background-color: white;
        }
        QCheckBox {
            spacing: 5px;
            color: #000000;
        }
        QCheckBox::indicator {
            width: 18px;
            height: 18px;
        }
        QPushButton {
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        """
        self.setStyleSheet(style)
