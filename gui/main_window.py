"""
Главное окно приложения Qobuz GUI Downloader
"""
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLineEdit, QPushButton, QTextEdit, QProgressBar,
                              QLabel, QTabWidget, QStatusBar, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont, QIcon


def create_message_box(parent, icon, title, text, buttons, default_button=None):
    """Создание QMessageBox с правильными стилями"""
    msg = QMessageBox(parent)
    msg.setIcon(icon)
    msg.setWindowTitle(title)
    msg.setText(text)
    msg.setStandardButtons(buttons)
    if default_button:
        msg.setDefaultButton(default_button)
    
    # Применяем стили для белого фона
    msg.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QLabel {
            color: black;
            background-color: white;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
    """)
    
    return msg


class DownloadThread(QThread):
    """Поток для скачивания, чтобы не блокировать GUI"""
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, url, settings, qobuz_client):
        super().__init__()
        self.url = url
        self.settings = settings
        self.qobuz_client = qobuz_client
        self._is_running = True
        self._is_paused = False
        
    def run(self):
        """Выполнение скачивания в фоновом потоке"""
        try:
            from core.downloader import QobuzDownloader
            import time
            
            downloader = QobuzDownloader(
                self.qobuz_client,
                self.settings,
                progress_callback=self.progress_signal.emit,
                log_callback=self.log_signal.emit
            )
            
            # Передаём ссылку на поток чтобы downloader мог проверять паузу
            downloader._download_thread = self
            
            self.log_signal.emit(f"Начинаю обработку: {self.url}")
            success = downloader.download_url(self.url)
            
            if success:
                self.finished_signal.emit(True, "Скачивание завершено успешно!")
            else:
                self.finished_signal.emit(False, "Произошла ошибка при скачивании")
                
        except Exception as e:
            self.finished_signal.emit(False, f"Ошибка: {str(e)}")
    
    def stop(self):
        """Остановка потока"""
        self._is_running = False


class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, qobuz_client=None):
        super().__init__()
        self.qobuz_client = qobuz_client
        self.download_thread = None
        self.settings = None
        self.is_paused = False
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("Qobuz GUI Downloader")
        self.setMinimumSize(900, 600)
        
        # Устанавливаем иконку приложения
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Главный layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Верхняя панель с вводом URL
        url_layout = QHBoxLayout()
        url_label = QLabel("URL Qobuz:")
        url_label.setMinimumWidth(80)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Вставьте ссылку на трек, альбом, артиста или плейлист...")
        self.url_input.returnPressed.connect(self.start_download)
        
        self.download_btn = QPushButton("Скачать")
        self.download_btn.setMinimumWidth(120)
        self.download_btn.clicked.connect(self.start_download)
        
        self.pause_btn = QPushButton("⏸ Пауза")
        self.pause_btn.setMinimumWidth(100)
        self.pause_btn.clicked.connect(self.toggle_pause)
        self.pause_btn.setEnabled(False)
        
        self.stop_btn = QPushButton("⏹ Стоп")
        self.stop_btn.setMinimumWidth(100)
        self.stop_btn.clicked.connect(self.stop_download)
        self.stop_btn.setEnabled(False)
        
        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.setMinimumWidth(120)
        self.settings_btn.clicked.connect(self.open_settings)
        
        self.logout_btn = QPushButton("Выход из аккаунта")
        self.logout_btn.setMinimumWidth(140)
        self.logout_btn.clicked.connect(self.logout)
        
        self.exit_btn = QPushButton("✕ Выход")
        self.exit_btn.setMinimumWidth(100)
        self.exit_btn.clicked.connect(self.exit_app)
        
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.download_btn)
        url_layout.addWidget(self.pause_btn)
        url_layout.addWidget(self.stop_btn)
        url_layout.addWidget(self.settings_btn)
        url_layout.addWidget(self.logout_btn)
        url_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(url_layout)
        
        # Прогресс-бар
        progress_layout = QHBoxLayout()
        progress_label = QLabel("Прогресс:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        main_layout.addLayout(progress_layout)
        
        # Область логов
        log_label = QLabel("Лог процесса:")
        main_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        main_layout.addWidget(self.log_text)
        
        # Статусная строка
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Готов к работе")
        
        # Применяем стили
        self.apply_styles()
        
    def apply_styles(self):
        """Применение стилей к интерфейсу"""
        style = """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QLineEdit {
            padding: 8px;
            border: 2px solid #ddd;
            border-radius: 4px;
            font-size: 12px;
            background-color: white;
            color: #000000;
        }
        QLineEdit:focus {
            border-color: #4CAF50;
        }
        QPushButton {
            padding: 8px 16px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            font-weight: bold;
            font-size: 12px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3d8b40;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        QTextEdit {
            border: 2px solid #ddd;
            border-radius: 4px;
            padding: 8px;
            background-color: #ffffff;
            color: #000000;
        }
        QProgressBar {
            border: 2px solid #ddd;
            border-radius: 4px;
            text-align: center;
            height: 25px;
        }
        QProgressBar::chunk {
            background-color: #4CAF50;
            border-radius: 2px;
        }
        QLabel {
            font-size: 12px;
            color: #333;
        }
        """
        self.setStyleSheet(style)
        
    def set_settings(self, settings):
        """Установка настроек"""
        self.settings = settings
        
    def log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.append(message)
        # Прокрутка вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def update_progress(self, value):
        """Обновление прогресс-бара"""
        self.progress_bar.setValue(value)
        
    def start_download(self):
        """Начало процесса скачивания"""
        url = self.url_input.text().strip()
        
        if not url:
            self.log("⚠ Ошибка: Введите URL")
            self.statusBar.showMessage("Ошибка: URL не указан")
            return
            
        if not self.qobuz_client:
            self.log("⚠ Ошибка: Нет авторизации в Qobuz")
            self.statusBar.showMessage("Ошибка: Требуется авторизация")
            return
            
        if not self.settings:
            self.log("⚠ Ошибка: Настройки не загружены")
            self.statusBar.showMessage("Ошибка: Настройки не найдены")
            return
        
        # Отключаем кнопку скачивания, включаем управление
        self.download_btn.setEnabled(False)
        self.download_btn.setText("Скачиваю...")
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.is_paused = False
        self.progress_bar.setValue(0)
        self.statusBar.showMessage("Скачивание...")
        
        # Очищаем лог
        self.log_text.clear()
        
        # Создаем и запускаем поток скачивания
        self.download_thread = DownloadThread(url, self.settings, self.qobuz_client)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.log_signal.connect(self.log)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.start()
    
    def toggle_pause(self):
        """Переключение паузы/возобновления"""
        if not self.download_thread or not self.download_thread.isRunning():
            return
        
        if self.is_paused:
            # Возобновить
            self.download_thread._is_paused = False
            self.pause_btn.setText("⏸ Пауза")
            self.is_paused = False
            self.log("▶ Скачивание возобновлено")
            self.statusBar.showMessage("Скачивание возобновлено...")
        else:
            # Пауза
            self.download_thread._is_paused = True
            self.pause_btn.setText("▶ Продолжить")
            self.is_paused = True
            self.log("⏸ Скачивание приостановлено")
            self.statusBar.showMessage("Приостановлено")
    
    def stop_download(self):
        """Остановка скачивания"""
        if not self.download_thread or not self.download_thread.isRunning():
            return
        
        msg = create_message_box(
            self,
            QMessageBox.Icon.Question,
            "Подтверждение",
            "Вы уверены, что хотите остановить скачивание?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log("⏹ Остановка скачивания...")
            self.download_thread.stop()
            self.download_thread.wait(3000)  # Ждём 3 секунды
            if self.download_thread.isRunning():
                self.download_thread.terminate()  # Принудительная остановка
            
            self.download_finished(False, "Скачивание прервано пользователем")
    
    def exit_app(self):
        """Выход из приложения"""
        
        # Проверяем, идёт ли скачивание
        if self.download_thread and self.download_thread.isRunning():
            msg = create_message_box(
                self,
                QMessageBox.Icon.Question,
                "Подтверждение выхода",
                "Идёт скачивание. Прервать и выйти?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            reply = msg.exec()
            
            if reply == QMessageBox.StandardButton.No:
                return
            
            # Останавливаем скачивание
            self.download_thread.stop()
            self.download_thread.wait(2000)
            if self.download_thread.isRunning():
                self.download_thread.terminate()
        
        self.close()
        
    def download_finished(self, success, message):
        """Обработка завершения скачивания"""
        self.download_btn.setEnabled(True)
        self.download_btn.setText("Скачать")
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("⏸ Пауза")
        self.stop_btn.setEnabled(False)
        self.is_paused = False
        
        if success:
            self.log(f"\n✓ {message}")
            self.statusBar.showMessage(message)
            self.progress_bar.setValue(100)
        else:
            self.log(f"\n✗ {message}")
            self.statusBar.showMessage(message)
            
        self.download_thread = None
        
    def open_settings(self):
        """Открытие окна настроек"""
        from gui.settings_window import SettingsWindow
        
        settings_window = SettingsWindow(self.settings, self)
        if settings_window.exec():
            self.settings = settings_window.get_settings()
            self.log("✓ Настройки обновлены")
            # Сохраняем настройки сразу
            self.save_settings_to_file()
    
    def save_settings_to_file(self):
        """Сохранение настроек в файл"""
        try:
            from pathlib import Path
            import json
            
            config_dir = Path(__file__).parent.parent / "config"
            config_dir.mkdir(exist_ok=True)
            settings_file = config_dir / "settings.json"
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            
            self.log("💾 Настройки сохранены")
        except Exception as e:
            self.log(f"⚠ Ошибка сохранения настроек: {e}")
    
    def logout(self):
        """Выход из аккаунта"""
        from pathlib import Path
        import json
        
        msg = create_message_box(
            self,
            QMessageBox.Icon.Question,
            "Выход из аккаунта",
            "Вы уверены, что хотите выйти из текущего аккаунта?\n\n"
            "Сохранённые учетные данные будут удалены.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        reply = msg.exec()
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Удаляем файл с учетными данными
                config_dir = Path(__file__).parent.parent / "config"
                credentials_file = config_dir / "credentials.json"
                
                if credentials_file.exists():
                    credentials_file.unlink()
                    self.log("✓ Учетные данные удалены")
                
                msg = create_message_box(
                    self,
                    QMessageBox.Icon.Information,
                    "Выход выполнен",
                    "Вы вышли из аккаунта.\nПриложение будет перезапущено.",
                    QMessageBox.StandardButton.Ok
                )
                msg.exec()
                
                # Перезапуск приложения
                import sys
                from PyQt6.QtCore import QCoreApplication
                QCoreApplication.quit()
                import os
                os.execv(sys.executable, ['python'] + sys.argv)
                
            except Exception as e:
                msg = create_message_box(
                    self,
                    QMessageBox.Icon.Critical,
                    "Ошибка",
                    f"Не удалось выполнить выход:\n{str(e)}",
                    QMessageBox.StandardButton.Ok
                )
                msg.exec()
            
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        if self.download_thread and self.download_thread.isRunning():
            self.download_thread.stop()
            self.download_thread.wait()
        event.accept()
