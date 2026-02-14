@echo off

echo =========================================================================
echo  [IMPORTANT] Please close ALL existing Chrome windows before continuing.
echo  This is required for the debug port (9222) to listen correctly.
echo =========================================================================
pause

echo Opening MAIN Chrome Profile in Debug Mode...

:: Define User Data Dir (Standard Windows location for main profile)
:: Use specific paths for x64/x86 if this fails, but usually LOCALAPPDATA works
set "USER_DATA=%LOCALAPPDATA%\Google\Chrome\User Data"

:: URLs to open
set "URL1=https://www.canva.com/projects"
set "URL2=https://ddcm.litarandfriends.uk"
set "URL3=https://www.etsy.com/your/shops/me/tools/listings/stats:true?ref=seller-platform-mcnav"


:: Try to launch Chrome (Standard Paths)
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DATA%" "%URL1%" "%URL2%" "%URL3%"
    goto :success
)

if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DATA%" "%URL1%" "%URL2%" "%URL3%"
    goto :success
)

if exist "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" (
    start "" "%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USER_DATA%" "%URL1%" "%URL2%" "%URL3%"
    goto :success
)

echo.
echo ERROR: Chrome not found automatically.
set /p CHROME_PATH="Path to chrome.exe: "

if exist "%CHROME_PATH%" (
    start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%USER_DATA%" "%URL1%" "%URL2%" "%URL3%"
    goto :success
) else (
    echo Invalid path.
    pause
    exit /b
)

:success
echo.
echo Chrome launched on port 9222 with 3 tabs.
echo.
pause
