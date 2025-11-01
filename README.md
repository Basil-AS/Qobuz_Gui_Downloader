# 🎵 Qobuz GUI Downloader# 🎵 Qobuz GUI Downloader# 🎵 Qobuz GUI Downloader



[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)

[![PyQt6](https://img.shields.io/badge/PyQt6-6.10-green)](https://www.riverbankcomputing.com/software/pyqt/)

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)![Python](https://img.shields.io/badge/python-3.8%2B-blue) ![PyQt6](https://img.shields.io/badge/PyQt6-6.10-green) ![License](https://img.shields.io/badge/license-MIT-green)



[Русская версия](README.ru.md) | **English**[![PyQt6](https://img.shields.io/badge/PyQt6-6.10-green)](https://www.riverbankcomputing.com/software/pyqt/)



**Desktop GUI application for downloading high-quality music from Qobuz with automatic synchronized lyrics search and embedding.**[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)**Десктопное приложение с графическим интерфейсом для скачивания музыки высокого качества с Qobuz с автоматическим поиском и встраиванием синхронизированных текстов песен.**



---



## ✨ Features[Русская версия](README.ru.md) | **English**---



### Core Functionality



- ✅ **Qobuz Downloads** - tracks, albums, artists (full discography!), playlists**Desktop GUI application for downloading high-quality music from Qobuz with automatic synchronized lyrics search and embedding.**## ✨ Возможности

- ✅ **High Quality Audio** - MP3 320kbps, FLAC (16/44.1, 24/96, 24/192)

- ✅ **Smart Lyrics Search** - two-stage LRC search algorithm (synced → plain)

  - Finds lyrics even with different artist spelling variations

  - Priority for synchronized lyrics with timecodes---### Основное

  - Fallback to plain lyrics if synced not found

  - Multiple formats: LRC (with timestamps), SRT (for VLC), TXT (plain text)

- ✅ **Complete Metadata** - all Qobuz tags (UPC, ISRC, Copyright, Label, etc.)

- ✅ **Album Artwork** - high quality, embedded into files## ✨ Features- ✅ **Скачивание с Qobuz** - треки, альбомы, исполнители (вся дискография!), плейлисты

- ✅ **M3U Playlists** - automatic playlist creation for albums

- ✅ **Smart URL Dispatcher** - multiple link support- ✅ **Высокое качество** - MP3 320kbps, FLAC (16/44.1, 24/96, 24/192)

- ✅ **Multi-language** - English and Russian with auto-detection

### Core Functionality- ✅ **Умный поиск текстов** - двухэтапный алгоритм поиска LRC (synced → plain)

### Download Management

  - Находит тексты даже при разном написании исполнителя (земфира/Zemfira)

- ⏸️ **Pause/Resume** - download process control

- ⏹️ **Stop** - interrupt with confirmation- ✅ **Qobuz Downloads** - tracks, albums, artists (full discography!), playlists  - Приоритет синхронизированным текстам с таймкодами

- 📊 **Real-time Progress** - detailed logs and progress bar

- ✅ **High Quality Audio** - MP3 320kbps, FLAC (16/44.1, 24/96, 24/192)  - Fallback на обычные тексты, если synced не найден

### Interface

- ✅ **Smart Lyrics Search** - two-stage LRC search algorithm (synced → plain)  - Множественные форматы: LRC (с таймкодами), SRT (для VLC), TXT (обычный)

- 🎨 **Modern Design** - clean PyQt6 interface

- 🌍 **Auto Language Detection** - detects system locale (English/Russian)  - Finds lyrics even with different artist spelling variations- ✅ **Полные метаданные** - все теги Qobuz (UPC, ISRC, Copyright, Label и др.)

- 🖼️ **Taskbar Icon** - proper Windows taskbar display

- ⚙️ **Flexible Settings** - full process control  - Priority for synchronized lyrics with timecodes- ✅ **Обложки альбомов** - высокое качество, встраивание в файлы

- 🔐 **Security** - local credentials storage

  - Fallback to plain lyrics if synced not found- ✅ **M3U плейлисты** - автоматическое создание плейлистов для альбомов

---

  - Multiple formats: LRC (with timestamps), SRT (for VLC), TXT (plain text)- ✅ **Умный диспетчер URL** - поддержка множественных ссылок

## 📦 Installation

- ✅ **Complete Metadata** - all Qobuz tags (UPC, ISRC, Copyright, Label, etc.)

### Windows

- ✅ **Album Artwork** - high quality, embedded into files### Управление загрузкой

**Requirements:**

- Python 3.8 or higher- ✅ **M3U Playlists** - automatic playlist creation for albums



**Installation Steps:**- ✅ **Smart URL Dispatcher** - multiple link support- ⏸️ **Пауза/возобновление** - контроль процесса скачивания



1. **Download the project:**- ⏹️ **Остановка** - прерывание с подтверждением

   ```powershell

   git clone https://github.com/Basil-AS/Qobuz_Gui_Downloader.git### Download Management- 📊 **Прогресс в реальном времени** - детальные логи и прогресс-бар

   cd Qobuz_Gui_Downloader

   ```



2. **Install dependencies:**- ⏸️ **Pause/Resume** - download process control### Интерфейс

   ```powershell

   pip install -r requirements.txt- ⏹️ **Stop** - interrupt with confirmation

   ```

- 📊 **Real-time Progress** - detailed logs and progress bar- 🎨 **Современный дизайн** - чистый интерфейс PyQt6

3. **Run the application:**

   ```powershell- 🖼️ **Иконка в панели задач** - правильное отображение в Windows

   python main.py

   ```### Interface- ⚙️ **Гибкие настройки** - полный контроль над процессом



### Build EXE (Windows)- 🔐 **Безопасность** - локальное хранение учетных данных



To create a standalone executable:- 🎨 **Modern Design** - clean PyQt6 interface



```powershell- 🌍 **Multi-language** - English and Russian (auto-detection based on system locale)---

.\build_exe.bat

```- 🖼️ **Taskbar Icon** - proper Windows taskbar display



The EXE will be created in the `dist/` folder.- ⚙️ **Flexible Settings** - full process control## 📦 Установка



**Note:** The built EXE will store settings and credentials in a `config/` folder next to the executable.- 🔐 **Security** - local credentials storage



---### Windows



## 🚀 Usage---



### First Launch**Требования:**



1. **Login to Qobuz**## 📦 Installation- Python 3.8 или выше

   - Enter your email and password

   - Credentials will be saved locally (encrypted)

   - Next time you'll be logged in automatically

### Windows**Шаги установки:**

2. **Configure Settings** (optional)

   - Click "Settings" button

   - Set download folder

   - Choose audio quality**Requirements:**1. **Скачайте проект:**

   - Configure lyrics formats

- Python 3.8 or higher   ```powershell

### Downloading Music

   git clone https://github.com/Basil-AS/Qobuz_Gui_Downloader.git

1. **Copy Qobuz URL**

   - Open Qobuz website**Installation Steps:**   cd Qobuz_Gui_Downloader

   - Navigate to album/track/playlist

   - Copy URL from browser   ```



2. **Paste and Download**1. **Download the project:**   

   - Paste URL into the application

   - Click "Download"   ```powershell   Или скачайте ZIP: [Download](https://github.com/Basil-AS/Qobuz_Gui_Downloader/archive/refs/heads/main.zip)

   - Wait for completion

   git clone https://github.com/Basil-AS/Qobuz_Gui_Downloader.git

### Supported URLs

   cd Qobuz_Gui_Downloader2. **Установите зависимости:**

- **Tracks:** `https://play.qobuz.com/track/...`

- **Albums:** `https://play.qobuz.com/album/...`   ```   ```powershell

- **Playlists:** `https://play.qobuz.com/playlist/...`

- **Artists:** `https://play.qobuz.com/artist/...` (downloads full discography)   pip install -r requirements.txt



---2. **Install dependencies:**   ```



## ⚙️ Settings   ```powershell



### Download Settings   pip install -r requirements.txt3. **Запустите:**



- **Download Folder** - where to save files (default: `~/Music/Qobuz Downloads`)   ```   ```powershell

- **Audio Quality:**

  - Maximum (up to 24-bit/192kHz FLAC)   .\start.bat

  - CD Quality (16-bit/44.1kHz FLAC)

  - High (MP3 320kbps)3. **Run the application:**   ```

  - Low (MP3 128kbps)

- **Download Cover Art** - embed album artwork   ```powershell   

- **Create M3U Playlist** - generate playlist files for albums

   python main.py   Или:

### File Naming

   ```   ```powershell

- **Folder Template:** `{artist} - {album} ({year})`

- **File Template:** `{tracknumber}. {artist} - {title}`   python main.py



Available tags: `{artist}`, `{album}`, `{title}`, `{year}`, `{tracknumber}`### Build EXE (Windows)   ```



### Lyrics Settings



- **Save LRC** - synchronized lyrics with timestamps (`.lrc`)To create a standalone executable:### Linux/macOS

- **Save SRT** - subtitle format for VLC player (`.srt`)

- **Save TXT** - plain text lyrics (`.txt`)



---```powershell```bash



## 📁 Project Structure.\build_exe.batgit clone https://github.com/Basil-AS/Qobuz_Gui_Downloader.git



``````cd Qobuz_Gui_Downloader

Qobuz_Gui_Downloader/

├── main.py                 # Main application entry pointpip install -r requirements.txt

├── requirements.txt        # Python dependencies

├── build_exe.bat          # Build script for Windows EXEThe EXE will be created in the `dist/` folder.python main.py

├── Qobuz_Gui_Downloader.spec  # PyInstaller config

├── config/                # Configuration files (created on first run)```

│   ├── credentials.json   # Encrypted user credentials

│   └── settings.json      # Application settings**Note:** The built EXE will store settings and credentials in a `config/` folder next to the executable.

├── core/                  # Core functionality modules

│   ├── qobuz_api.py      # Qobuz API wrapper---

│   ├── downloader.py     # Download manager

│   ├── metadata.py       # Metadata tagging---

│   ├── lyrics_search.py  # Lyrics search engine

│   ├── url_dispatcher.py # URL parser## 🚀 Использование

│   └── localization.py   # Multi-language support

├── gui/                   # GUI components## 🚀 Usage

│   ├── login_window.py   # Login dialog

│   ├── main_window.py    # Main application window1. Запустите приложение

│   └── settings_window.py # Settings dialog

└── resources/             # Application resources### First Launch2. Введите email и пароль от Qobuz

    ├── icon.ico          # Windows icon

    └── icon.png          # Application icon3. Вставьте URL трека/альбома/исполнителя/плейлиста

```

1. **Login to Qobuz**4. Нажмите "Скачать"

---

   - Enter your email and password

## 🔧 Development

   - Credentials will be saved locally (encrypted)**Примеры URL:**

### Dependencies

   - Next time you'll be logged in automatically- Трек: `https://www.qobuz.com/us-en/album/album-name/1234567890`

- **PyQt6** - GUI framework

- **qobuz-dl** - Qobuz API integration- Альбом: `https://www.qobuz.com/us-en/album/dark-side-of-the-moon/0190295842413`

- **mutagen** - audio metadata editing

- **Pillow** - image processing2. **Configure Settings** (optional)- Исполнитель: `https://www.qobuz.com/us-en/artist/pink-floyd/45749`

- **requests** - HTTP client

   - Click "Settings" button- Плейлист: `https://www.qobuz.com/us-en/playlist/my-favorites/12345678`

### Building from Source

   - Set download folder

1. Clone the repository

2. Install dependencies: `pip install -r requirements.txt`   - Choose audio quality**Множественные URL:**

3. Run: `python main.py`

   - Configure lyrics formats- Через запятую: `url1, url2, url3`

### Creating Executable

- С новой строки (каждая ссылка на отдельной строке)

```powershell

# Install PyInstaller### Downloading Music

pip install pyinstaller

---

# Build EXE

.\build_exe.bat1. **Copy Qobuz URL**



# Output: dist/Qobuz_Gui_Downloader.exe   - Open Qobuz website## ⚙️ Настройки

```

   - Navigate to album/track/playlist

---

   - Copy URL from browser### Качество аудио

## 🐛 Troubleshooting

- **MP3 320 kbps** - совместимость

### Login Issues

2. **Paste and Download**- **FLAC 16bit/44.1kHz** - CD качество (по умолчанию)

- **Error: Invalid credentials**

  - Check email/password   - Paste URL into the application- **FLAC 24bit/96kHz** - Hi-Res

  - Ensure you have an active Qobuz subscription

  - Try logging in on Qobuz website first   - Click "Download"- **FLAC 24bit/192kHz** - максимальное качество



- **Error: Saved credentials invalid**   - Wait for completion

  - Delete `config/credentials.json`

  - Restart application and login again### Тексты песен



### Download Issues### Supported URLs- **Поиск текстов** - включить/выключить



- **Error: Track not available**- **Сохранять LRC** - файлы с таймкодами (по умолчанию включено)

  - Content may be geo-restricted

  - Your subscription tier may not include this quality- **Tracks:** `https://play.qobuz.com/track/...`- **Сохранять SRT** - для видеоплееров



- **Lyrics not found**- **Albums:** `https://play.qobuz.com/album/...`- **Сохранять TXT** - обычный текст

  - Not all tracks have synchronized lyrics

  - Check if artist/title spelling is correct on Qobuz- **Playlists:** `https://play.qobuz.com/playlist/...`- **Встраивать в теги** - автоматически добавлять в метаданные



### Icon Not Showing in Taskbar- **Artists:** `https://play.qobuz.com/artist/...` (downloads full discography)



- Restart Windows Explorer: `taskkill /f /im explorer.exe && start explorer.exe`### Файлы

- Or reboot your computer

---- **Папка загрузок** - куда сохранять музыку

---

- **Шаблон альбома** - структура папок: `{artist}/{year} - {title}`

## 📝 Changelog

## ⚙️ Settings- **Шаблон трека** - формат имени файла: `{tracknumber}. {artist} - {title}`

### v1.0.5 (2025-01-11)

- ✅ Added: Full internationalization (English/Russian)- **Скачивать обложки** - сохранять cover.jpg

- ✅ Added: Automatic language detection based on system locale

- ✅ Added: English as default language, switches to Russian if system is Russian### Download Settings- **M3U плейлисты** - создавать для альбомов

- ✅ Updated: All GUI components now use localization system

- ✅ Updated: Documentation now available in both languages (README.md / README.ru.md)



### v1.0.4 (2025-01-11)- **Download Folder** - where to save files (default: `~/Music/Qobuz Downloads`)### Метаданные

- ✅ Fixed: Config folder now created next to EXE (not in temp folder)

- ✅ Credentials and settings now persist correctly in built EXE- **Audio Quality:**- Встраиваются все доступные теги:



### v1.0.3 (2025-01-11)  - Maximum (up to 24-bit/192kHz FLAC)  - Базовые: исполнитель, альбом, название, год, жанр

- ✅ Added: `save_credentials()` and `delete_credentials()` methods

- ✅ Fixed: Credentials persistence after login in built EXE  - CD Quality (16-bit/44.1kHz FLAC)  - Расширенные: UPC, ISRC, Copyright, Label, Release Type



### v1.0.2 (2025-01-11)  - High (MP3 320kbps)  - Explicit метка для треков с ненормативной лексикой

- ✅ Fixed: Track numbers in titles (01., 04., etc.) now removed

- ✅ Fixed: Single quotes support in clean title matching  - Low (MP3 128kbps)

- ✅ Increased duration tolerance to 100 seconds for album versions

- ✅ Fixed critical bug: `highest_score = float('-inf')` instead of -1- **Download Cover Art** - embed album artwork---



### v1.0.1 (2025-01-11)- **Create M3U Playlist** - generate playlist files for albums

- ✅ Critical fixes for lyrics search

- ✅ Fixed negative score selection bug## 📁 Структура проекта

- ✅ Improved clean title algorithm

### File Naming

### v1.0.0 (2025-01-11)

- 🎉 Initial stable release```

- ✅ M3U playlist support

- ✅ Final lyrics search algorithm with maximum accuracy- **Folder Template:** `{artist} - {album} ({year})`Qobuz_Gui_Downloader/

- ✅ Complete GUI implementation

- **File Template:** `{tracknumber}. {artist} - {title}`├── main.py                    # Точка входа

---

├── start.bat                  # Запуск для Windows

## 📄 License

Available tags: `{artist}`, `{album}`, `{title}`, `{year}`, `{tracknumber}`├── requirements.txt           # Зависимости

MIT License - see [LICENSE](LICENSE) file for details.

├── core/

---

### Lyrics Settings│   ├── qobuz_api.py          # API клиент Qobuz

## 🤝 Contributing

│   ├── downloader.py         # Логика скачивания

Contributions are welcome! Please feel free to submit a Pull Request.

- **Save LRC** - synchronized lyrics with timestamps (`.lrc`)│   ├── lyrics_search.py      # Поиск текстов

1. Fork the repository

2. Create your feature branch (`git checkout -b feature/AmazingFeature`)- **Save SRT** - subtitle format for VLC player (`.srt`)│   ├── metadata.py           # Обработка метаданных

3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)

4. Push to the branch (`git push origin feature/AmazingFeature`)- **Save TXT** - plain text lyrics (`.txt`)│   └── url_dispatcher.py     # Парсинг URL

5. Open a Pull Request

├── gui/

---

---│   ├── main_window.py        # Главное окно

## ⚠️ Disclaimer

│   ├── login_window.py       # Окно авторизации

This tool is for educational purposes only. You must have a valid Qobuz subscription to use this application. Respect copyright laws and artists' rights.

## 📁 Project Structure│   └── settings_window.py    # Окно настроек

---

├── resources/

## 🌟 Support

```│   ├── icon.png              # Иконка приложения

If you find this project useful, please consider giving it a star ⭐ on GitHub!

Qobuz_Gui_Downloader/│   └── icon.ico              # Иконка для Windows

**GitHub:** [Basil-AS/Qobuz_Gui_Downloader](https://github.com/Basil-AS/Qobuz_Gui_Downloader)

├── main.py                 # Main application entry point└── config/

├── requirements.txt        # Python dependencies    └── settings.json         # Настройки (создаётся автоматически)

├── build_exe.bat          # Build script for Windows EXE```

├── Qobuz_Gui_Downloader.spec  # PyInstaller config

├── config/                # Configuration files (created on first run)---

│   ├── credentials.json   # Encrypted user credentials

│   └── settings.json      # Application settings## 🔍 Как работает поиск текстов

├── core/                  # Core functionality modules

│   ├── qobuz_api.py      # Qobuz API wrapperПриложение использует двухэтапный алгоритм поиска:

│   ├── downloader.py     # Download manager

│   ├── metadata.py       # Metadata tagging### Этап 1: Поиск синхронизированных текстов (LRC)

│   ├── lyrics_search.py  # Lyrics search engine1. **lrclib.net** - приоритетный источник с таймкодами

│   ├── url_dispatcher.py # URL parser2. **syncedlyrics** - резервный источник (Musixmatch, Genius, Deezer и др.)

│   └── localization.py   # Multi-language support

├── gui/                   # GUI components### Этап 2: Fallback на обычные тексты

│   ├── login_window.py   # Login dialog- Если синхронизированные не найдены - ищет обычные тексты

│   ├── main_window.py    # Main application window- Конвертирует в нужный формат (LRC/SRT/TXT)

│   └── settings_window.py # Settings dialog

└── resources/             # Application resources### Особенности фильтрации

    ├── icon.ico          # Windows icon- ✅ **Строгая проверка** - сравнивает исполнителя И название

    └── icon.png          # Application icon- ✅ **Транслитерация** - находит "Земфира" по запросу "Zemfira"

```- ✅ **Версии в скобках** - корректно обрабатывает "(live)", "(remix)" и т.д.

- ✅ **Точное совпадение** - "Сука" НЕ матчит "Сука любовь"

---- ✅ **Без ложных срабатываний** - инструментальные треки не получают чужие тексты



## 🔧 Development---



### Dependencies## 🛠️ Разработка



- **PyQt6** - GUI framework### Сборка EXE (Windows)

- **qobuz-dl** - Qobuz API integration

- **mutagen** - audio metadata editingДля создания исполняемого файла используется PyInstaller:

- **Pillow** - image processing

- **requests** - HTTP client```powershell

# Установка PyInstaller

### Building from Sourcepip install pyinstaller



1. Clone the repository# Сборка

2. Install dependencies: `pip install -r requirements.txt`.\build_exe.bat

3. Run: `python main.py````



### Creating ExecutableГотовый EXE будет в папке `dist/`



```powershell### Зависимости

# Install PyInstaller

pip install pyinstaller- **PyQt6** - графический интерфейс

- **mutagen** - работа с метаданными аудиофайлов

# Build EXE- **requests** - HTTP запросы

.\build_exe.bat- **syncedlyrics** - поиск синхронизированных текстов

- **rapidfuzz** - умное сравнение строк для транслитерации

# Output: dist/Qobuz_Gui_Downloader.exe

```Полный список в `requirements.txt`



------



## 🐛 Troubleshooting## 🐛 Отладка



### Login Issues### Логи

Приложение создаёт лог-файл `qobuz_downloader.log` в рабочей директории с подробной информацией о работе.

- **Error: Invalid credentials**

  - Check email/password### Частые проблемы

  - Ensure you have an active Qobuz subscription

  - Try logging in on Qobuz website first**❌ "Не удалось авторизоваться"**

- Проверьте правильность email и пароля

- **Error: Saved credentials invalid**- Убедитесь что у вас активная подписка Qobuz

  - Delete `config/credentials.json`

  - Restart application and login again**❌ "Не удалось получить URL для скачивания"**

- Выбранное качество недоступно для трека

### Download Issues- Попробуйте снизить качество в настройках



- **Error: Track not available****❌ "Тексты не найдены"**

  - Content may be geo-restricted- Не все треки имеют тексты в базе lrclib.net

  - Your subscription tier may not include this quality- Проверьте написание исполнителя и названия в метаданных трека на Qobuz



- **Lyrics not found****❌ "Ошибка при записи метаданных"**

  - Not all tracks have synchronized lyrics- Файл может быть заблокирован другой программой

  - Check if artist/title spelling is correct on Qobuz- Проверьте права доступа к папке загрузок



### Icon Not Showing in Taskbar---



- Restart Windows Explorer: `taskkill /f /im explorer.exe && start explorer.exe`## 📝 История изменений

- Or reboot your computer

### v1.0.0 (31 октября 2025)

---

**Первый стабильный релиз! 🎉**

## 📝 Changelog

**✨ Новые возможности**

### v1.0.4 (2025-11-01)- ✅ **M3U плейлисты** - автоматическое создание M3U8 плейлистов для альбомов и плейлистов

- ✅ Fixed: Config folder now created next to EXE (not in temp folder)- ✅ **Управление загрузкой** - полноценная поддержка паузы/возобновления

- ✅ Credentials and settings now persist correctly in built EXE- ✅ **Отладка настроек** - вывод текущих настроек при старте скачивания



### v1.0.3 (2025-11-01)**🐛 Исправления**

- ✅ Added: `save_credentials()` and `delete_credentials()` methods- ✅ Исправлена кнопка паузы - теперь корректно останавливает/возобновляет скачивание

- ✅ Fixed: Credentials persistence after login in built EXE- ✅ Проверка паузы выполняется перед каждым треком в циклах альбомов и плейлистов



### v1.0.2 (2025-11-01)**🎯 Улучшения поиска текстов**

- ✅ Fixed: Track numbers in titles (01., 04., etc.) now removed- Реализована максимально строгая фильтрация результатов

- ✅ Fixed: Single quotes support in clean title matching- Проверка соответствия как исполнителя, так и названия трека

- ✅ Increased duration tolerance to 100 seconds for album versions- Убрано мягкое сравнение (startswith/contains) - только точное совпадение

- ✅ Fixed critical bug: `highest_score = float('-inf')` instead of -1- Исправлены ложные срабатывания (например "Сука" больше не матчит "Сука любовь")

- Поддержка транслитерации имён исполнителей (Земфира = Zemfira)

### v1.0.1 (2025-11-01)- Корректная обработка версий в скобках (например "Прах (live)")

- ✅ Critical fixes for lyrics search

- ✅ Fixed negative score selection bug---

- ✅ Improved clean title algorithm

## 📄 Лицензия

### v1.0.0 (2025-11-01)

- 🎉 Initial stable releaseMIT License

- ✅ M3U playlist support

- ✅ Final lyrics search algorithm with maximum accuracyCopyright (c) 2025 Basil-AS

- ✅ Complete GUI implementation

Основные положения:

---- ✅ Коммерческое использование

- ✅ Модификация

## 📄 License- ✅ Распространение

- ✅ Приватное использование

MIT License - see [LICENSE](LICENSE) file for details.- ❌ Ответственность

- ❌ Гарантия

---

---

## 🤝 Contributing

## ⚠️ Disclaimer

Contributions are welcome! Please feel free to submit a Pull Request.

Это приложение предназначено **только для личного использования** с музыкой, которую вы **легально приобрели** на Qobuz.

1. Fork the repository

2. Create your feature branch (`git checkout -b feature/AmazingFeature`)- Не используйте для скачивания музыки, на которую у вас нет прав

3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)- Соблюдайте условия использования Qobuz

4. Push to the branch (`git push origin feature/AmazingFeature`)- Разработчики не несут ответственности за неправомерное использование

5. Open a Pull Request

**Скачивайте только то, что вы купили или на что у вас есть подписка!**

---

---

## ⚠️ Disclaimer

## 🙏 Благодарности

This tool is for educational purposes only. You must have a valid Qobuz subscription to use this application. Respect copyright laws and artists' rights.

- **Qobuz** - за отличный сервис высококачественной музыки

---- **lrclib.net** - за базу синхронизированных текстов

- **syncedlyrics** - за библиотеку поиска текстов

## 🌟 Support- **PyQt6** - за мощный GUI framework

- **Всем контрибьюторам** - за улучшения и баг-репорты

If you find this project useful, please consider giving it a star ⭐ on GitHub!

---

**GitHub:** [Basil-AS/Qobuz_Gui_Downloader](https://github.com/Basil-AS/Qobuz_Gui_Downloader)

## 📧 Контакты

- **GitHub**: [Basil-AS](https://github.com/Basil-AS)
- **Issues**: [GitHub Issues](https://github.com/Basil-AS/Qobuz_Gui_Downloader/issues)
- **Releases**: [GitHub Releases](https://github.com/Basil-AS/Qobuz_Gui_Downloader/releases)

---

<div align="center">

**Сделано с ❤️ для любителей музыки высокого качества**

[⬆ Наверх](#-qobuz-gui-downloader)

</div>
