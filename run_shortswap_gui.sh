#!/bin/bash
# Launcher for ShortSwap 2.0 GUI with ComfyUI integration

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add CUDA libraries to library path for GPU acceleration
# Prioritize system CUDA libraries over pip-installed ones
export LD_LIBRARY_PATH="/usr/local/cuda-13.0/targets/x86_64-linux/lib:/usr/local/cuda-13.0/lib64:$LD_LIBRARY_PATH"

# Use unified_venv Python to access ComfyUI dependencies (websocket-client, etc.)
UNIFIED_VENV="/home/panda/Documents/PythonScripts/UnifiedMCP/unified_venv"

if [ -d "$UNIFIED_VENV" ]; then
    # Activate unified_venv which has all ComfyUI dependencies
    source "$UNIFIED_VENV/bin/activate"
    cd "$SCRIPT_DIR"
    python shortswap_gui.py
else
    # Fallback to system python if unified_venv not found
    echo "Warning: UnifiedMCP venv not found. ComfyUI features may not work."
    echo "Expected location: $UNIFIED_VENV"
    cd "$SCRIPT_DIR"
    python3 shortswap_gui.py
fi
