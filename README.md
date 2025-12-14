# ShortSwap

Complete end-to-end automation of YouTube Shorts face-swapping with both CLI and GUI interfaces.

## Features

- **CLI Interface** - Fully automated command-line pipeline
- **GUI Interface** - User-friendly graphical interface with desktop integration
- **Resume Capability** - Resume incomplete jobs that failed mid-processing
- **YouTube Download** - Automatic download of YouTube Shorts
- **Face Swapping** - Batch face-swap all video frames using InsightFace
- **GPU Acceleration** - CUDA support for faster processing
- **Gender Filtering** - Target specific genders for face swapping
- **Person Targeting** - Swap faces of specific individuals using reference images
- **Watermarking** - Optional watermark on output videos
- **Progress Tracking** - Real-time progress monitoring

## What It Does

1. Downloads YouTube Short (or uses local video file)
2. Extracts video into frames
3. Batch face-swaps all frames using InsightFace + inswapper
4. Rebuilds video from swapped frames
5. Adds original audio to final video

## Components

### Core Scripts
- **shortswap.sh** - Main automated CLI pipeline
- **shortswap_gui.py** - Graphical user interface
- **run_shortswap_gui.sh** - GUI launcher script
- **resume_shortswap.sh** - Resume incomplete/failed jobs

### Dependencies
- **impostr_cli.py** - Face-swapping engine
- **youtube_shorts_downloader.py** - YouTube download component

### Documentation
- **ShortSwap_README.md** - CLI documentation
- **ShortSwap_GUI_README.md** - GUI documentation
- **impostr_cli_README.md** - Face-swapping component docs
- **youtube_shorts_downloader_README.md** - YouTube downloader docs

## Requirements

### System Dependencies
- Python 3.7+
- ffmpeg
- CUDA toolkit (optional, for GPU acceleration)

### Python Dependencies
```bash
pip install insightface onnxruntime opencv-python Pillow numpy
# For GPU support:
pip install onnxruntime-gpu
```

### AI Model
Download the inswapper_128.onnx model and place it in `models/` directory:
- Model: inswapper_128.onnx
- Size: ~554MB
- Download: [InsightFace Model Zoo](https://github.com/deepinsight/insightface/releases)

## Quick Start

### CLI Usage
```bash
# Basic usage with YouTube URL
./shortswap.sh --url <YOUTUBE_URL> --face <SOURCE_IMAGE>

# With GPU acceleration
./shortswap.sh --url <YOUTUBE_URL> --face <SOURCE_IMAGE> --cuda

# With local video file
./shortswap.sh --video <VIDEO_FILE> --face <SOURCE_IMAGE>

# With gender filtering
./shortswap.sh --url <YOUTUBE_URL> --face <SOURCE_IMAGE> --gender male --cuda
```

### GUI Usage
```bash
# Launch GUI
./run_shortswap_gui.sh

# Or directly
python3 shortswap_gui.py
```

### Resume Failed Jobs
```bash
# Resume an incomplete job
./resume_shortswap.sh <job_directory> <source_face_image> --cuda
```

## Desktop Integration

The GUI includes desktop integration with:
- Desktop launcher icon
- Application menu entry
- Icon: `/home/panda/Pictures/logos/shortswap_logo.jpg`

Desktop files:
- `~/Desktop/shortswap.desktop`
- `~/.local/share/applications/shortswap.desktop`

## Performance

- **CPU Processing**: 7-22 minutes for 15-second video
- **GPU Processing**: 45 seconds - 4 minutes for 15-second video

## Advanced Features

### Gender Filtering
Target only male or female faces:
```bash
./shortswap.sh --url <URL> --face <IMAGE> --gender male
./shortswap.sh --url <URL> --face <IMAGE> --gender female
```

### Person-Specific Targeting
Swap face of a specific person using a reference image:
```bash
./shortswap.sh --url <URL> --face <SOURCE> --target-person <REFERENCE_IMAGE>
```

### Watermarking
Add watermark to output videos:
```bash
./shortswap.sh --url <URL> --face <IMAGE> --watermark
```

## Architecture

```
ShortSwap Pipeline:
├── YouTube Download (youtube_shorts_downloader.py)
├── Frame Extraction (ffmpeg)
├── Face Swapping (impostr_cli.py + InsightFace)
├── Video Reconstruction (ffmpeg)
└── Audio Integration (ffmpeg)
```

## Troubleshooting

### Computer Freezes During Processing
If the computer freezes mid-processing, use the resume script:
```bash
./resume_shortswap.sh /path/to/job/directory /path/to/face/image --cuda
```

This will:
- Identify incomplete/failed frames
- Re-process only the missing frames
- Complete the video assembly

### GPU Out of Memory
If you encounter GPU memory errors:
1. Use CPU mode (remove `--cuda` flag)
2. Close other GPU-intensive applications
3. Reduce video resolution before processing

### No Face Detected
If frames have no detectable faces, they will be saved as-is without swapping.

## License

This project uses InsightFace for face detection and swapping. Please review their license terms.

## Credits

Built with:
- [InsightFace](https://github.com/deepinsight/insightface) - Face detection and swapping
- [ONNX Runtime](https://onnxruntime.ai/) - Model inference
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube downloading
- [FFmpeg](https://ffmpeg.org/) - Video processing

---

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
