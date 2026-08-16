#!/bin/bash

# ==============================================================
# KAVACH PULSE — ONE COMMAND LAUNCHER
# ==============================================================

set -e

PROJECT_DIR="$HOME/Documents/home credits"
ENV_DIR="$HOME/kavach-env"

API_FILE="29_kavach_live_assessment_api.py"
COMMAND_CENTER="33_kavach_command_center.py"
COMPARISON="35_kavach_comparison.py"

API_PORT=8000
COMMAND_PORT=8501
COMPARISON_PORT=8502


echo "======================================================================"
echo " KAVACH PULSE — STARTING SYSTEM"
echo "======================================================================"


# --------------------------------------------------------------
# PROJECT DIRECTORY
# --------------------------------------------------------------

cd "$PROJECT_DIR"


# --------------------------------------------------------------
# VIRTUAL ENVIRONMENT
# --------------------------------------------------------------

if [ ! -d "$ENV_DIR" ]; then

    echo "ERROR: Kavach virtual environment not found:"
    echo "$ENV_DIR"
    exit 1

fi


source "$ENV_DIR/bin/activate"

echo "[OK] Virtual environment activated"


# --------------------------------------------------------------
# REQUIRED FILES
# --------------------------------------------------------------

for file in \
    "$API_FILE" \
    "$COMMAND_CENTER" \
    "$COMPARISON"
do

    if [ ! -f "$file" ]; then

        echo "ERROR: Required file not found:"
        echo "$PROJECT_DIR/$file"

        exit 1

    fi

done


echo "[OK] Required files found"


# --------------------------------------------------------------
# CHECK PYTHON
# --------------------------------------------------------------

echo
echo "Python:"
python3 --version


# --------------------------------------------------------------
# STOP OLD KAVACH PROCESSES
# --------------------------------------------------------------

echo
echo "[1] Cleaning previous Kavach processes..."


pkill -f "$API_FILE" 2>/dev/null || true

pkill -f "$COMMAND_CENTER" 2>/dev/null || true

pkill -f "$COMPARISON" 2>/dev/null || true


sleep 2


# --------------------------------------------------------------
# START API
# --------------------------------------------------------------

echo
echo "[2] Starting Kavach API..."
echo "    Port: $API_PORT"


python3 "$API_FILE" > kavach_api.log 2>&1 &

API_PID=$!


echo "    API PID: $API_PID"


# --------------------------------------------------------------
# WAIT FOR API
# --------------------------------------------------------------

echo
echo "[3] Waiting for API health check..."


API_READY=0


for i in {1..30}
do

    if curl -s \
        --max-time 1 \
        "http://127.0.0.1:$API_PORT/health" \
        > /tmp/kavach_health.json
    then

        API_READY=1

        break

    fi

    sleep 1

done


if [ "$API_READY" -ne 1 ]; then

    echo
    echo "ERROR: Kavach API failed to start."

    echo
    echo "Last API log:"
    tail -30 kavach_api.log

    exit 1

fi


echo "[OK] Kavach API is healthy"


echo
echo "Health response:"
cat /tmp/kavach_health.json

echo


# --------------------------------------------------------------
# START COMMAND CENTER
# --------------------------------------------------------------

echo
echo "[4] Starting Command Center..."
echo "    Port: $COMMAND_PORT"


streamlit run "$COMMAND_CENTER" \
    --server.port "$COMMAND_PORT" \
    > kavach_command_center.log 2>&1 &

COMMAND_PID=$!


echo "    Command Center PID: $COMMAND_PID"


# --------------------------------------------------------------
# START COMPARISON DASHBOARD
# --------------------------------------------------------------

echo
echo "[5] Starting Comparison Dashboard..."
echo "    Port: $COMPARISON_PORT"


streamlit run "$COMPARISON" \
    --server.port "$COMPARISON_PORT" \
    > kavach_comparison.log 2>&1 &

COMPARISON_PID=$!


echo "    Comparison PID: $COMPARISON_PID"


# --------------------------------------------------------------
# FINAL STATUS
# --------------------------------------------------------------

sleep 3


echo
echo "======================================================================"
echo " KAVACH PULSE — SYSTEM READY"
echo "======================================================================"

echo
echo "API:"
echo "http://127.0.0.1:$API_PORT/health"

echo
echo "Command Center:"
echo "http://localhost:$COMMAND_PORT"

echo
echo "Applicant Comparison:"
echo "http://localhost:$COMPARISON_PORT"

echo
echo "API logs:"
echo "$PROJECT_DIR/kavach_api.log"

echo
echo "Command Center logs:"
echo "$PROJECT_DIR/kavach_command_center.log"

echo
echo "Comparison logs:"
echo "$PROJECT_DIR/kavach_comparison.log"

echo
echo "Press Ctrl+C to stop Kavach."

echo
echo "======================================================================"


# --------------------------------------------------------------
# CLEAN SHUTDOWN
# --------------------------------------------------------------

cleanup() {

    echo
    echo "Stopping Kavach..."

    kill "$API_PID" 2>/dev/null || true

    kill "$COMMAND_PID" 2>/dev/null || true

    kill "$COMPARISON_PID" 2>/dev/null || true

    echo "Kavach stopped."

}


trap cleanup SIGINT SIGTERM


# --------------------------------------------------------------
# KEEP SCRIPT RUNNING
# --------------------------------------------------------------

wait
