@echo off
setlocal

:: -------------------------------------------------------------
:: Step 1: Check Chrome Process (Friendly Warning)
:: -------------------------------------------------------------
echo Checking for running Chrome processes...
tasklist /FI "IMAGENAME eq chrome.exe" 2>NUL | find /I /N "chrome.exe" >NUL
if "%ERRORLEVEL%"=="0" (
    :: Check if it's OUR debug instance (port 9222 listening)
    netstat -an | find "9222" >nul
    if %errorlevel% equ 0 (
        echo [INFO] Debug Chrome is already running.
        set /p USE_EXISTING="Use existing Chrome instance? (y/n): "
        if /i "%USE_EXISTING%"=="y" goto :run_python

        echo Killing existing Chrome and restarting...
        taskkill /F /IM chrome.exe /T 2>NUL
        timeout /t 2
        goto :launch_custom
    ) else (
        echo.
        echo [WARNING] Normal Chrome is running!
        echo You MUST close it to start our Debug Chrome.
        set /p KILL_CHROME="Kill Chrome now? (y/n): "
        if /i "%KILL_CHROME%"=="y" (
            taskkill /F /IM chrome.exe /T 2>NUL
            timeout /t 2
            goto :launch_custom
        ) else (
            echo Please close Chrome manually and run again.
            pause
            exit /b
        )
    )
)

:launch_custom
:: -------------------------------------------------------------
:: Step 2: Launch Chrome (Debug Mode - CUSTOM PROFILE)
:: -------------------------------------------------------------
echo.
echo Launching Chrome (Debug Mode - CUSTOM PROFILE)...
echo Profile Path: C:\selenium\ChromeProfile
echo.

if not exist "C:\selenium\ChromeProfile" mkdir "C:\selenium\ChromeProfile"
set "USER_DATA=C:\selenium\ChromeProfile"
set "CHROME_PATH=%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"

set "URL1=https://www.canva.com/projects"
set "URL2=https://ddcm.litarandfriends.uk"
set "URL3=https://www.etsy.com/your/shops/me/tools/listings/stats:true?ref=seller-platform-mcnav"

if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist "%CHROME_PATH%" set "CHROME_PATH=C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

:: LAUNCH COMMAND
start "" "%CHROME_PATH%" --remote-debugging-port=9222 --user-data-dir="%USER_DATA%" "%URL1%" "%URL2%" "%URL3%"

echo Waiting 5 seconds for Chrome to launch...
timeout /t 5

:run_python
:: -------------------------------------------------------------
:: Step 3: Run Application
:: -------------------------------------------------------------
echo.
echo Starting Application...
if not exist "venv" (
    call venv\Scripts\activate
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate
    :: Force install to ensure everything is there
    pip install -r requirements.txt
)

python gui.py
pause
