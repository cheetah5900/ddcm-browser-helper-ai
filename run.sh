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

    if [ ! -f "$CHROME_PATH" ]; then
        # Try to find Chrome if default path fails
        CHROME_PATH=$(mdfind "kMDItemCFBundleIdentifier == 'com.google.Chrome'" | head -n 1)"/Contents/MacOS/Google Chrome"
    fi

    URL1="https://www.canva.com/projects"
    URL2="https://ddcm.litarandfriends.uk"
    URL3="https://www.etsy.com/your/shops/me/tools/listings/stats:true?ref=seller-platform-mcnav"
    URL4="https://gemini.google.com/app"
    URL5="http://127.0.0.1:6969"

    if [ ! -f "$CHROME_PATH" ]; then
        echo "[ERROR] Google Chrome not found! Please make sure it's installed in /Applications"
        exit 1
    fi

    # Launch Chrome independently using macOS 'open' command
    open -na "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir="$USER_DATA" "$URL1" "$URL2" "$URL3" "$URL4" "$URL5"

    echo "Waiting 5 seconds for Chrome to launch..."
    sleep 5
fi

echo ""
echo "Preparing Python Environment..."

# Try to find the best python version (3.14 -> 3.12 -> 3.x)
PYTHON_EXE=$(which python3.14)
if [ -z "$PYTHON_EXE" ]; then
    PYTHON_EXE=$(which python3.12)
fi
if [ -z "$PYTHON_EXE" ]; then
    PYTHON_EXE=$(which python3)
fi

if [ -z "$PYTHON_EXE" ]; then
    echo "[ERROR] Python 3 not found! Please install Python 3.10+."
    exit 1
fi

echo "[INFO] Using Python: $PYTHON_EXE"

# Manage venv
if [ -d "venv" ]; then
    # Optional: check if venv matches the python version
    VENV_PYTHON="./venv/bin/python"
    if [ -f "$VENV_PYTHON" ]; then
        V_OUT=$($VENV_PYTHON --version 2>&1)
        echo "[INFO] Existing venv: $V_OUT"
    else
        echo "[INFO] venv seems broken. Recreating..."
        rm -rf venv
    fi
fi

if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment (venv)..."
    $PYTHON_EXE -m venv venv
fi

# Activate venv
echo "[INFO] Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "[INFO] Updating dependencies..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet

echo ""
echo "[SUCCESS] Environment ready. Launching GUI..."

# Build React UI if needed
if [ -d "web" ]; then
  if [ ! -d "web/node_modules" ]; then
    echo "[INFO] Installing web dependencies..."
    (cd web && npm install)
  fi
  if [ ! -f "web/dist/index.html" ]; then
    echo "[INFO] Building web UI..."
    (cd web && npm run build)
  fi
fi

echo "[INFO] Starting backend on http://127.0.0.1:6969 ..."
uvicorn backend.app:app --host 127.0.0.1 --port 6969 &
BACKEND_PID=$!
sleep 1

echo "[INFO] Backend PID: $BACKEND_PID (Ctrl+C to stop)"
wait $BACKEND_PID
