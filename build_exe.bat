@echo off
chcp 65001 >nul
echo =====================================
echo  Сборка Qobuz GUI Downloader
echo =====================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ОШИБКА] Python не найден!
    echo Установите Python с https://python.org
    pause
    exit /b 1
)

echo [1/5] Проверка зависимостей...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [*] Установка PyInstaller...
    pip install pyinstaller
)

echo [2/5] Очистка старых сборок...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/5] Запуск PyInstaller...
pyinstaller Qobuz_Gui_Downloader.spec

if errorlevel 1 (
    echo.
    echo [ОШИБКА] Сборка не удалась!
    pause
    exit /b 1
)

echo [4/5] Проверка результата...
if not exist "dist\Qobuz_Gui_Downloader.exe" (
    echo [ОШИБКА] EXE файл не создан!
    pause
    exit /b 1
)

echo [5/5] Создание README для dist...
(
echo Qobuz GUI Downloader v1.0.1
echo.
echo Запуск: Qobuz_Gui_Downloader.exe
echo.
echo При первом запуске введите:
echo - Email от Qobuz
echo - Пароль
echo.
echo Настройки сохраняются в папке config/
echo.
echo Поддержка: https://github.com/Basil-AS/Qobuz_Gui_Downloader
) > dist\README.txt

echo.
echo =====================================
echo  ✓ СБОРКА ЗАВЕРШЕНА УСПЕШНО!
echo =====================================
echo.
echo Файл: dist\Qobuz_Gui_Downloader.exe
for %%A in (dist\Qobuz_Gui_Downloader.exe) do echo Размер: %%~zA байт
echo.
echo Для тестирования запустите:
echo   dist\Qobuz_Gui_Downloader.exe
echo.
pause
