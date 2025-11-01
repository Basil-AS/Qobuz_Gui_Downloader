"""
Окно авторизации в Qobuz
"""
import os
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from core.localization import t


class LoginThread(QThread):
    """Поток для авторизации без блокировки GUI"""
    success_signal = pyqtSignal(object)  # Client object
    error_signal = pyqtSignal(str)
    
    def __init__(self, email, password):
        super().__init__()
        self.email = email
        self.password = password
        
    def run(self):
        """Выполнение авторизации"""
        try:
            from core.qobuz_api import get_qobuz_client
            
            client = get_qobuz_client(self.email, self.password)
            self.success_signal.emit(client)
            
        except Exception as e:
            self.error_signal.emit(str(e))


class LoginWindow(QDialog):
    """Окно авторизации в Qobuz"""
    
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.client = None
        self.login_thread = None
        self.config = config  # ConfigManager для сохранения credentials
        self.init_ui()
        
    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle(t('login_title'))
        self.setFixedSize(500, 350)
        self.setModal(True)
        
        # Устанавливаем иконку окна
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resources", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Заголовок
        title = QLabel("Qobuz Lyrics Downloader")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel(t('login_subtitle'))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Email
        email_label = QLabel(t('login_email'))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText(t('login_email_placeholder'))
        self.email_input.returnPressed.connect(self.login)
        
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)
        
        # Пароль
        password_label = QLabel(t('login_password'))
        
        # Контейнер для пароля с кнопкой показа
        password_container = QHBoxLayout()
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(t('login_password_placeholder'))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.login)
        
        # Кнопка показа/скрытия пароля
        self.show_password_btn = QPushButton("👁")
        self.show_password_btn.setFixedWidth(40)
        self.show_password_btn.setCheckable(True)
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        self.show_password_btn.setToolTip(t('login_toggle_password'))
        
        password_container.addWidget(self.password_input)
        password_container.addWidget(self.show_password_btn)
        
        layout.addWidget(password_label)
        layout.addLayout(password_container)
        
        # Прогресс-бар (скрыт по умолчанию)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Статус
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        layout.addSpacing(10)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        self.login_btn = QPushButton(t('login_button'))
        self.login_btn.setMinimumHeight(35)
        self.login_btn.clicked.connect(self.login)
        
        self.cancel_btn = QPushButton(t('cancel_button'))
        self.cancel_btn.setMinimumHeight(35)
        self.cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.login_btn)
        buttons_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        # Примечание
        note = QLabel(t('login_note'))
        note.setStyleSheet("color: #999; font-size: 10px;")
        note.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(note)
        
        self.apply_styles()
        
    def apply_styles(self):
        """Применение стилей"""
        style = """
        QDialog {
            background-color: #f5f5f5;
        }
        QLabel {
            color: #333;
            font-size: 12px;
        }
        QLineEdit {
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 13px;
            background-color: white;
            color: #000000;
        }
        QLineEdit:focus {
            border-color: #4CAF50;
        }
        QPushButton {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
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
        QPushButton#show_password_btn {
            padding: 5px;
            background-color: #e0e0e0;
            color: #333;
            font-size: 16px;
        }
        QPushButton#show_password_btn:hover {
            background-color: #d0d0d0;
        }
        QPushButton#show_password_btn:checked {
            background-color: #4CAF50;
            color: white;
        }
        """
        self.setStyleSheet(style)
        self.show_password_btn.setObjectName("show_password_btn")
        
    def toggle_password_visibility(self):
        """Переключение видимости пароля"""
        if self.show_password_btn.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_password_btn.setText("🙈")
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_password_btn.setText("👁")
        
    def login(self):
        """Начало процесса авторизации"""
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, t('error'), t('login_fill_fields'))
            return
        
        # Блокируем UI
        self.login_btn.setEnabled(False)
        self.email_input.setEnabled(False)
        self.password_input.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText(t('login_authenticating'))
        
        # Запускаем поток авторизации
        self.login_thread = LoginThread(email, password)
        self.login_thread.success_signal.connect(self.on_login_success)
        self.login_thread.error_signal.connect(self.on_login_error)
        self.login_thread.start()
        
    def on_login_success(self, client):
        """Обработка успешной авторизации"""
        self.client = client
        self.status_label.setText(t('login_success'))
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        
        # Сохраняем учетные данные через ConfigManager
        if self.config:
            self.config.save_credentials(self.email_input.text(), self.password_input.text())
        
        # Закрываем окно через небольшую задержку
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(500, self.accept)
    
    def on_login_error(self, error_msg):
        """Обработка ошибки авторизации"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("")
        
        # Разблокируем UI
        self.login_btn.setEnabled(True)
        self.email_input.setEnabled(True)
        self.password_input.setEnabled(True)
        
        QMessageBox.critical(self, t('login_error_title'), f"{t('login_error')}\n{error_msg}")
        
    def get_client(self):
        """Получение клиента Qobuz"""
        return self.client
