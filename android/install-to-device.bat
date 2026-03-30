@echo off
chcp 65001 >nul
echo ========================================
echo   Install APK to Device
echo ========================================
echo.

echo Checking device connection...
adb devices

echo.
echo Installing APK...
adb install -r app\build\outputs\apk\debug\app-debug.apk

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Install Success!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Install Failed!
    echo ========================================
)

pause
