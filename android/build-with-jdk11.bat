@echo off
REM Build script for WeightLossBetting Android app
REM This ensures consistent builds using JDK 11

set JAVA_HOME=F:\javajdk\jdk11
set PATH=%JAVA_HOME%\bin;%PATH%

echo Building with JDK 11...
gradlew.bat clean assembleDebug --no-daemon

echo.
echo Build completed! APK location: app\build\outputs\apk\debug\app-debug.apk
pause
