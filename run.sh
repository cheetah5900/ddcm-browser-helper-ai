#!/bin/bash

echo "Checking for running Chrome processes..."

if lsof -i :9222 > /dev/null; then
    echo "[INFO] Debug Chrome is already running. Using existing instance."
    LAUNCH_CHROME=false
else
    if pgrep -x "Google Chrome" > /dev/null; then
        echo ""
        echo "[WARNING] Normal Chrome is running!"
        echo "You MUST close it to start our Debug Chrome."
        read -p "Kill Chrome now? (y/n): " KILL_CHROME
        if [[ "$KILL_CHROME" == "y" || "$KILL_CHROME" == "Y" ]]; then
            pkill -x "Google Chrome"
            sleep 2
            LAUNCH_CHROME=true
        else
            echo "Please close Chrome manually and run again."
            exit 1
        fi
    else
        LAUNCH_CHROME=true
    fi
fi

if [ "$LAUNCH_CHROME" = true ]; then
    echo ""
    echo "Launching Chrome (Debug Mode - CUSTOM PROFILE)..."
    USER_DATA="$HOME/selenium/ChromeProfile"
    echo "Profile Path: $USER_DATA"
    echo ""

    mkdir -p "$USER_DATA"
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

    URL1="https://www.canva.com/projects"
    URL2="https://ddcm.litarandfriends.uk"
    URL3="https://www.etsy.com/your/shops/me/tools/listings/stats:true?ref=seller-platform-mcnav"
    URL4="https://gemini.google.com/app"

    if [ ! -f "$CHROME_PATH" ]; then
        echo "[ERROR] Google Chrome not found at $CHROME_PATH"
        exit 1
    fi

    # Launch Chrome in the background
    "$CHROME_PATH" --remote-debugging-port=9222 --user-data-dir="$USER_DATA" "$URL1" "$URL2" "$URL3" "$URL4" &

    echo "Waiting 5 seconds for Chrome to launch..."
    sleep 5
fi

echo ""
echo "Starting Application..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

python3 gui.py
