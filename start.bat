@echo off
echo ========================================
echo Qobuz Lyrics Downloader
echo ========================================
echo.

REM Проверка наличия Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ОШИБКА: Python не найден!
    echo Установите Python 3.8+ с https://www.python.org/
    pause
    exit /b 1
)

echo Проверка зависимостей...
python -c "import PyQt6" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Установка зависимостей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ОШИБКА: Не удалось установить зависимости!
        pause
        exit /b 1
    )
)

echo.
echo Запуск приложения...
echo.
python main.py

if errorlevel 1 (
    echo.
    echo ОШИБКА: Приложение завершилось с ошибкой!
    pause
)
