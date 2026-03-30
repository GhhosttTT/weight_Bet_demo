@echo off
chcp 65001 >nul
echo ========================================
echo   Build Android Project with JDK 11
echo ========================================
echo.

REM Optional: Set JDK 11 path here if needed
REM set JAVA_HOME=C:\Program Files\Java\jdk-11

if not "%JAVA_HOME%"=="" (
    echo Using JAVA_HOME: %JAVA_HOME%
) else (
    echo [Warning] JAVA_HOME not set, using system default
    echo.
)

echo.
echo Starting build...
call gradlew.bat assembleDebug

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo   Build Success!
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   Build Failed!
    echo ========================================
)

pause
