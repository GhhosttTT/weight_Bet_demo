@echo off
REM Install APK to connected device/emulator

echo Installing app to device...
adb install -r app\build\outputs\apk\debug\app-debug.apk

if %errorlevel% equ 0 (
    echo.
    echo Installation successful!
    echo Starting app...
    adb shell am start -n com.weightloss.betting/.ui.MainActivity
) else (
    echo.
    echo Installation failed. Make sure a device or emulator is connected.
)

pause
