# ShortSwap GUI

**Graphical Interface for YouTube Shorts Face-Swap Pipeline**

Easy-to-use desktop application for automating YouTube Shorts face-swapping with a simple point-and-click interface.

## Location
- **GUI Script:** `/home/panda/Documents/PythonScripts/shortswap_gui.py`
- **Launcher Script:** `/home/panda/Documents/PythonScripts/run_shortswap_gui.sh`
- **Desktop Shortcut:** `~/Desktop/shortswap.desktop`
- **Application Menu:** Search for "ShortSwap" in your application launcher

## How to Launch

### Method 1: Desktop Icon
Double-click the **ShortSwap** icon on your desktop

### Method 2: Application Menu
1. Open your application launcher
2. Search for "ShortSwap"
3. Click the ShortSwap icon

### Method 3: Command Line
```bash
/home/panda/Documents/PythonScripts/run_shortswap_gui.sh
```

Or directly:
```bash
python3 /home/panda/Documents/PythonScripts/shortswap_gui.py
```

## How to Use

### Step-by-Step Guide

1. **Enter YouTube URL**
   - Paste the YouTube Shorts URL in the URL field
   - Format: `https://youtube.com/shorts/abc123`

2. **Select Source Face**
   - Click "Browse..." next to the Source Face Image field
   - Select the image containing the face you want to apply
   - Supported formats: JPG, JPEG, PNG, BMP

3. **Choose Output Directory** (Optional)
   - Default: `~/Videos/ShortSwap`
   - Click "Browse..." to select a different location

4. **Configure Options** (Optional)
   - ☑ **Use GPU/CUDA (Faster)** - Enable for 10-30x speedup if you have NVIDIA GPU
   - ☑ **Add Watermark** - Adds "AI face-swap (consented)" watermark to frames
   - ☑ **Keep Frame Files** - Preserve intermediate frame directories for debugging

5. **Start Processing**
   - Click the **"Start Face Swap"** button
   - Watch progress in the log window
   - Wait for completion (typically 7-22 minutes on CPU, 1-4 minutes on GPU)

6. **View Results**
   - When complete, click "Yes" to open the output folder
   - Your face-swapped video will be named `[Original Title]_swapped.mp4`

## Interface Overview

```
╔════════════════════════════════════════════════════════════╗
║                        ShortSwap                           ║
║           YouTube Shorts Face-Swap Pipeline                ║
╠════════════════════════════════════════════════════════════╣
║ YouTube Short URL                                          ║
║ ┌────────────────────────────────────────────────────────┐ ║
║ │ https://youtube.com/shorts/abc123                      │ ║
║ └────────────────────────────────────────────────────────┘ ║
╠════════════════════════════════════════════════════════════╣
║ Source Face Image                                          ║
║ ┌────────────────────────────────────────┐ [Browse...]    ║
║ │ /home/panda/Pictures/my_face.jpg       │                ║
║ └────────────────────────────────────────┘                ║
╠════════════════════════════════════════════════════════════╣
║ Output Settings                                            ║
║ ┌────────────────────────────────────────┐ [Browse...]    ║
║ │ /home/panda/Videos/ShortSwap           │                ║
║ └────────────────────────────────────────┘                ║
╠════════════════════════════════════════════════════════════╣
║ Options                                                    ║
║ ☐ Use GPU/CUDA  ☐ Add Watermark  ☐ Keep Frame Files      ║
╠════════════════════════════════════════════════════════════╣
║              [ Start Face Swap ]                           ║
╠════════════════════════════════════════════════════════════╣
║ Progress                                                   ║
║ ┌────────────────────────────────────────────────────────┐ ║
║ │ Starting ShortSwap Pipeline...                         │ ║
║ │ ==> Step 1/5: Downloading YouTube Short...             │ ║
║ │ ✓ Downloaded: Amazing Dance Video                     │ ║
║ │ ==> Step 2/5: Extracting video frames...              │ ║
║ │ ✓ Extracted 450 frames                                │ ║
║ │ ...                                                     │ ║
║ └────────────────────────────────────────────────────────┘ ║
║ [████████████████████████░░░░░░░░░░░░] Processing...      ║
║ Status: Processing...                                      ║
╚════════════════════════════════════════════════════════════╝
```

## Features

### User-Friendly Interface
- Simple, intuitive layout
- File browser dialogs for easy file selection
- Real-time progress monitoring
- Color-coded status messages:
  - 🟢 Green - Success messages
  - 🔵 Blue - Step indicators
  - 🔴 Red - Errors
  - 🟡 Orange - Warnings

### Automatic Processing
- Downloads YouTube Short automatically
- Extracts all frames
- Batch processes face-swapping
- Rebuilds video with audio
- Cleans up temporary files (unless "Keep Frame Files" is checked)

### Progress Tracking
- Live output from the pipeline
- Step-by-step status updates
- Progress bar animation
- Completion notifications

### Smart Error Handling
- Validates URLs before processing
- Checks if source image exists
- Displays helpful error messages
- Prevents starting multiple processes simultaneously

## Requirements

All requirements are the same as the command-line version:
- Python 3.x with tkinter (pre-installed on most Linux systems)
- yt-dlp
- ffmpeg
- InsightFace
- OpenCV
- inswapper_128.onnx model

If the command-line `shortswap.sh` works, the GUI will work too!

## Examples

### Example 1: Basic Face Swap
1. Paste URL: `https://youtube.com/shorts/dQw4w9WgXcQ`
2. Browse and select: `~/Pictures/my_face.jpg`
3. Leave output as default: `~/Videos/ShortSwap`
4. Click "Start Face Swap"
5. Wait for completion
6. Open output folder when prompted

**Result:** Video saved as `~/Videos/ShortSwap/Amazing Dance Video_swapped.mp4`

### Example 2: GPU-Accelerated with Watermark
1. Enter YouTube Shorts URL
2. Select source face image
3. Check ✓ "Use GPU/CUDA (Faster)"
4. Check ✓ "Add Watermark"
5. Click "Start Face Swap"
6. Processing completes in ~1-4 minutes instead of 7-22 minutes

### Example 3: Debug Mode
1. Enter URL and select source face
2. Check ✓ "Keep Frame Files"
3. Click "Start Face Swap"
4. After completion, inspect frames in the ShortSwap temporary directory
5. Review individual frames to troubleshoot issues

## Tips for Best Results

### Source Face Image
- Use high-resolution images (1024x1024 or higher)
- Front-facing, well-lit photos work best
- Avoid sunglasses, masks, or heavy occlusions
- Single person in the image

### YouTube Shorts Selection
- Choose videos with relatively still heads
- Good lighting helps
- Front or near-front angles work better than profiles
- Single camera angle preferred over quick cuts

### Performance
- Enable "Use GPU/CUDA" if you have an NVIDIA GPU (10-30x faster!)
- Close other applications during processing
- Ensure sufficient disk space (~2-5 GB per video temporarily)

## Troubleshooting

### "Process exited with code 1"
Check the progress log for specific errors. Common issues:
- Invalid YouTube URL
- No face detected in source image
- No face detected in video frames
- Missing dependencies or model file

### GUI Doesn't Open
Try running from terminal to see error messages:
```bash
python3 /home/panda/Documents/PythonScripts/shortswap_gui.py
```

### "Browse" Button Doesn't Work
Ensure tkinter is properly installed:
```bash
python3 -c "import tkinter; print('tkinter OK')"
```

### Can't Find Desktop Icon
Update the desktop database:
```bash
update-desktop-database ~/.local/share/applications
xdg-icon-resource forceupdate
```

Or manually launch:
```bash
/home/panda/Documents/PythonScripts/run_shortswap_gui.sh
```

### Processing Stuck or Frozen
- Check the progress log for errors
- Ensure internet connection is stable (for downloading)
- Verify enough disk space is available
- If truly frozen, close GUI and check if background process is still running:
  ```bash
  ps aux | grep shortswap
  ```

### CUDA Not Working
Even if checkbox is enabled, GPU may not be used if:
- CUDA is not installed
- onnxruntime-gpu is not installed
- No compatible NVIDIA GPU detected

The script will fall back to CPU automatically.

## Advantages Over Command Line

| Feature | GUI | Command Line |
|---------|-----|--------------|
| **Ease of Use** | Click and select | Type commands |
| **File Selection** | Browse dialogs | Manual paths |
| **Progress Monitoring** | Live log window | Terminal output |
| **Error Messages** | Dialog boxes | Text output |
| **Multi-tasking** | Run in background | Blocks terminal |
| **Learning Curve** | Minimal | Requires CLI knowledge |
| **Desktop Integration** | Icon, menus | Command only |

## Integration

### Works With Existing Tools
The GUI is a wrapper around the command-line `shortswap.sh` script, so:
- All command-line features are available
- Same backend processing
- Same quality results
- Can use both GUI and CLI interchangeably

### Output Files
All output files are compatible:
- Same MP4 format
- Same quality settings
- Same file naming convention
- Can be used in any video editor

## Advanced Usage

### Running from Terminal
For debugging or logging:
```bash
cd /home/panda/Documents/PythonScripts
python3 shortswap_gui.py 2>&1 | tee shortswap_gui.log
```

### Customizing Defaults
Edit `shortswap_gui.py` to change defaults:
```python
# Line ~21
self.default_output = os.path.expanduser("~/Videos/ShortSwap")

# Line ~23 (change default CUDA setting)
self.use_cuda = tk.BooleanVar(value=True)  # Enable CUDA by default
```

### Creating Multiple Shortcuts
Copy the desktop file with different names:
```bash
cp ~/Desktop/shortswap.desktop ~/Desktop/shortswap_gpu.desktop
```

Edit the new file to add `--cuda` flag by default.

## Keyboard Shortcuts

- **Tab** - Navigate between fields
- **Enter** - (when in URL/path fields) Move to next field
- **Alt+F4** - Close window (only when not processing)
- **Ctrl+A** - Select all text in focused field

## Safety Features

- **Input Validation** - Verifies URL and file paths before starting
- **Single Process** - Prevents multiple simultaneous swaps
- **Progress Indication** - Shows that processing is active
- **Automatic Cleanup** - Removes temporary files after completion
- **Error Recovery** - Gracefully handles failures and shows error details

## Ethical Use

The GUI includes the same ethical considerations as the CLI:
- ✅ Use with consent from all parties
- ✅ Consider enabling watermark for transparency
- ✅ Use for personal, educational, or authorized projects
- ❌ Never create deceptive content
- ❌ Never use for fraud or impersonation

The watermark option is easily accessible for ethical content marking.

## Version History

- **v1.0** (2025-11-20) - Initial release
  - Complete GUI wrapper for shortswap.sh
  - Real-time progress monitoring
  - Desktop integration with icon
  - File browser dialogs
  - Color-coded status messages
  - Success/error notifications

## Related Documentation

- **ShortSwap_README.md** - Command-line documentation
- **impostr_cli_README.md** - Face-swapping component
- **youtube_shorts_downloader_README.md** - Download component

## Support

If you encounter issues:
1. Check the progress log in the GUI for error details
2. Try the command-line version to isolate GUI-specific issues
3. Verify all dependencies are installed
4. Check that the shortswap.sh script works independently

---

**Enjoy easy YouTube Shorts face-swapping with the ShortSwap GUI!**
