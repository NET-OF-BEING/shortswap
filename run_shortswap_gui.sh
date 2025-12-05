#!/bin/bash
# Launcher for ShortSwap GUI

# Add CUDA libraries to library path for GPU acceleration
# Prioritize system CUDA libraries over pip-installed ones
export LD_LIBRARY_PATH="/usr/local/cuda-13.0/targets/x86_64-linux/lib:/usr/local/cuda-13.0/lib64:$LD_LIBRARY_PATH"

# Remove pip CUDA libraries from Python path to avoid conflicts
export PYTHONPATH=""

cd /home/panda/Documents/PythonScripts
python3 shortswap_gui.py
