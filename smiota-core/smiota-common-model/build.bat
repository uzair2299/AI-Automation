@echo off
setlocal

set "GOALS=clean install"
if not "%~1"=="" (
    set "GOALS=%*"
)

echo ========================================================
echo Building smiota-common-model
echo Command: mvn %GOALS%
echo ========================================================

call mvn %GOALS%
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Build failed with exit code %ERRORLEVEL%.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] Built and installed smiota-common-model to local Maven repository!
pause

