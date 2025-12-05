# ShortSwap

**Automated YouTube Shorts Face-Swap Pipeline**

ShortSwap is a complete end-to-end automation tool that downloads a YouTube Short, replaces faces in every frame, and rebuilds the video with original audio - all in one command.

## Location
- **Main Script:** `/home/panda/Documents/PythonScripts/shortswap.sh`
- **README:** `/home/panda/Documents/PythonScripts/ShortSwap_README.md`

## What It Does

ShortSwap automates the entire 5-step face-swapping pipeline:

1. **Download YouTube Short** - Uses yt-dlp to fetch the video
2. **Extract Frames** - Splits video into individual PNG images using ffmpeg
3. **Batch Face-Swap** - Applies your face to every frame using InsightFace deep learning
4. **Rebuild Video** - Reassembles swapped frames into video using ffmpeg
5. **Add Audio** - Merges original audio track back into the final video

All of this happens automatically with a single command.

## Requirements

### Software Dependencies
- **Python 3.x** (already installed)
- **yt-dlp** - YouTube downloader
- **ffmpeg** - Video processing
- **InsightFace** - Face detection/swapping
- **OpenCV** - Image processing
- **PIL/Pillow** - Image manipulation

### Model Files
- **inswapper_128.onnx** - Face-swapping model (must be in `models/` directory)

### Disk Space
- Temporary files for a 15-second video: ~2-5 GB
- Final video file: ~5-50 MB (depends on length and quality)

## Installation

### Quick Setup

If you already have the faceswap_cli.py working, you're all set!

### First-Time Setup

```bash
# Install Python dependencies
pip install yt-dlp opencv-python insightface pillow

# Ensure ffmpeg is installed
sudo zypper install ffmpeg

# Download the inswapper model (if not already present)
# Place inswapper_128.onnx in /home/panda/Documents/PythonScripts/models/
```

## Usage

### Basic Syntax

```bash
shortswap.sh --url <YOUTUBE_URL> --face <SOURCE_IMAGE>
```

### Quick Start

```bash
# Download and face-swap a YouTube Short
/home/panda/Documents/PythonScripts/shortswap.sh \
  --url https://youtube.com/shorts/abc123 \
  --face my_face.jpg
```

### Common Usage Patterns

#### 1. Basic Face Swap
```bash
shortswap.sh -u https://youtube.com/shorts/abc123 -f my_face.jpg
```

**Output:** `~/Videos/ShortSwap/[Video Title]_swapped.mp4`

#### 2. Custom Output Location and Name
```bash
shortswap.sh \
  -u https://youtube.com/shorts/abc123 \
  -f my_face.jpg \
  --output ~/Desktop \
  --name "my_awesome_video"
```

**Output:** `~/Desktop/my_awesome_video.mp4`

#### 3. GPU Acceleration (Much Faster!)
```bash
shortswap.sh -u URL -f face.jpg --cuda
```

**Speed comparison:**
- CPU: ~1-3 seconds per frame
- GPU: ~0.1-0.5 seconds per frame

#### 4. Add Watermark
```bash
shortswap.sh -u URL -f face.jpg --watermark
```

Adds "AI face-swap (consented)" watermark to every frame.

#### 5. Keep Intermediate Frames
```bash
shortswap.sh -u URL -f face.jpg --keep-frames
```

Preserves the extracted and swapped frame directories for inspection or manual editing.

#### 6. Custom Framerate
```bash
shortswap.sh -u URL -f face.jpg --framerate 60
```

Use higher framerate for smoother video (if source supports it).

## Command-Line Options

### Required Arguments

| Option | Short | Description |
|--------|-------|-------------|
| `--url` | `-u` | YouTube Shorts URL to download |
| `--face` | `-f` | Source face image to apply onto video |

### Optional Arguments

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output` | `-o` | `~/Videos/ShortSwap` | Output directory |
| `--name` | `-n` | Auto from video title | Custom output filename |
| `--framerate` | `-r` | `30` | Video framerate (fps) |
| `--watermark` | `-w` | Off | Add watermark to frames |
| `--cuda` | - | Off | Use GPU acceleration |
| `--keep-frames` | - | Off | Keep intermediate directories |
| `--help` | `-h` | - | Show help message |

## Examples

### Example 1: Quick Face Swap
```bash
shortswap.sh \
  -u https://youtube.com/shorts/dQw4w9WgXcQ \
  -f derek_face.jpg
```

**Output:**
```
╔════════════════════════════════════════════════════════════════╗
║                         ShortSwap                              ║
║           YouTube Shorts Face-Swap Pipeline                    ║
╚════════════════════════════════════════════════════════════════╝

YouTube URL:    https://youtube.com/shorts/dQw4w9WgXcQ
Source Face:    derek_face.jpg
Output Dir:     /home/panda/Videos/ShortSwap

==> Step 1/5: Downloading YouTube Short...
✓ Downloaded: Amazing Dance Video

==> Step 2/5: Extracting video frames...
✓ Extracted 450 frames

==> Step 3/5: Face-swapping all frames...
[450/450] Processing frame_0450.png... ✓
✓ All frames processed

==> Step 4/5: Rebuilding video from swapped frames...
✓ Video rebuilt

==> Step 5/5: Adding original audio...
✓ Audio added

╔════════════════════════════════════════════════════════════════╗
║                    ✓ ShortSwap Complete!                       ║
╚════════════════════════════════════════════════════════════════╝

Final video saved to:
  /home/panda/Videos/ShortSwap/Amazing Dance Video_swapped.mp4

File size: 8.2M
✓ ShortSwap pipeline completed successfully!
```

### Example 2: Production Quality with GPU
```bash
shortswap.sh \
  -u https://youtube.com/shorts/abc123 \
  -f high_res_face.jpg \
  --cuda \
  --watermark \
  --output ~/Desktop/FinalVideos \
  --name "production_v1"
```

**Features:**
- GPU acceleration for fast processing
- Watermark for transparency
- Custom output location and name

### Example 3: Debug Mode
```bash
shortswap.sh \
  -u URL \
  -f face.jpg \
  --keep-frames
```

Keeps all intermediate files for manual inspection:
```
/home/panda/Videos/ShortSwap/shortswap_XXXXXX/
  ├── [Original Video].mp4       # Downloaded video
  ├── frames/                    # Extracted frames
  │   ├── frame_0001.png
  │   ├── frame_0002.png
  │   └── ...
  ├── swapped_frames/            # Face-swapped frames
  │   ├── frame_0001.png
  │   ├── frame_0002.png
  │   └── ...
  └── temp_video.mp4             # Video without audio
```

## Create a Convenient Alias

Add to your `~/.bashrc`:

```bash
alias shortswap='/home/panda/Documents/PythonScripts/shortswap.sh'
```

Reload shell:
```bash
source ~/.bashrc
```

Now you can use it like a built-in command:
```bash
shortswap -u https://youtube.com/shorts/abc123 -f my_face.jpg
```

## Processing Times

**For a typical 15-second YouTube Short (~450 frames):**

| Hardware | Time per Frame | Total Time |
|----------|----------------|------------|
| CPU (Intel/AMD) | 1-3 seconds | 7-22 minutes |
| GPU (NVIDIA CUDA) | 0.1-0.5 seconds | 45s - 4 minutes |

**Download/Rebuild steps:** ~10-30 seconds total

**Recommendation:** Use `--cuda` flag if you have a compatible NVIDIA GPU for 10-30x speedup!

## Tips for Best Results

### Source Face Image
- **High resolution** - At least 1024x1024 pixels
- **Front-facing** - Direct view of face
- **Good lighting** - Even, well-lit face
- **Clear features** - Sharp, in-focus image
- **Single person** - Only one face in image

### Target Videos That Work Best
- **Relatively still head** - Minimal head rotation
- **Single camera angle** - Consistent perspective
- **Good lighting** - Well-lit scenes
- **Clear face visibility** - Face not obscured
- **Front/near-front angles** - Not extreme side profiles

### Performance Optimization
- Use `--cuda` for GPU acceleration
- Process shorter clips first to test
- Close other applications during processing
- Use SSD storage for faster read/write

## Troubleshooting

### "yt-dlp not installed"
```bash
pip install yt-dlp
```

### "ffmpeg command not found"
```bash
sudo zypper install ffmpeg
```

### "Missing swapper model"
Download `inswapper_128.onnx` and place it at:
```
/home/panda/Documents/PythonScripts/models/inswapper_128.onnx
```

### "No face detected in source/target"
- Ensure faces are clearly visible and front-facing
- Try better-lit images
- Avoid sunglasses, masks, or heavy occlusions

### CUDA Not Working
Install CUDA-enabled ONNX Runtime:
```bash
pip install onnxruntime-gpu
```

Verify CUDA installation:
```bash
nvidia-smi
```

### Out of Disk Space
- Each video project uses 2-5 GB temporarily
- Clean up old ShortSwap temporary directories
- Don't use `--keep-frames` unless debugging

### Poor Quality Results
- Use higher resolution source face
- Ensure good lighting match between source and target
- Try videos with minimal head movement
- Avoid extreme angles or dramatic lighting changes

## Technical Details

### The 5-Step Pipeline Explained

**Step 1: Download (yt-dlp)**
- Downloads best available quality
- Saves to temporary working directory
- Preserves original audio track

**Step 2: Frame Extraction (ffmpeg)**
- Splits video into sequential PNG files
- Numbered format: `frame_0001.png`, `frame_0002.png`, etc.
- Maintains original resolution

**Step 3: Face Swapping (InsightFace + inswapper)**
- **Face Detection:** buffalo_l model detects all faces
- **Face Selection:** Automatically picks largest face
- **Neural Swapping:** Deep learning model maps source face features onto target
- **Seamless Blending:** Matches lighting, skin tone, and geometry
- Processes each frame independently

**Step 4: Video Rebuild (ffmpeg)**
- Reassembles PNG frames into MP4 video
- H.264 encoding (libx264)
- YUV420p pixel format for compatibility
- Maintains specified framerate

**Step 5: Audio Merge (ffmpeg)**
- Copies audio stream from original video
- Muxes with face-swapped video stream
- No re-encoding (fast, lossless)

### File Structure

```
~/Videos/ShortSwap/
  ├── Video1_swapped.mp4           # Final outputs
  ├── Video2_swapped.mp4
  └── shortswap_XXXXXX/            # Temp dirs (auto-deleted)
      ├── [Original].mp4
      ├── frames/
      ├── swapped_frames/
      └── temp_video.mp4
```

## Use Cases

- **Content Creation** - Create personalized video memes
- **Testing/Previsualization** - See yourself in different scenarios
- **Digital Art Projects** - Creative video manipulation
- **Educational** - Learn about AI face-swapping technology
- **Entertainment** - Make funny videos with friends (with consent!)

## Ethical Considerations

**IMPORTANT:** This tool should only be used ethically and legally:

- ✅ Only use with **explicit consent** from all parties
- ✅ Add watermarks to indicate AI manipulation (`--watermark`)
- ✅ Use for personal, educational, or authorized creative projects
- ✅ Respect copyright and platform terms of service
- ❌ Never create deceptive or harmful content
- ❌ Never use for impersonation or fraud
- ❌ Never distribute without consent

## Credits

**ShortSwap** integrates multiple technologies:
- **yt-dlp** - YouTube downloading
- **ffmpeg** - Video processing
- **InsightFace** - Face detection and swapping
- **inswapper_128.onnx** - Pre-trained face-swap model

Built on top of your existing face-swap infrastructure:
- `youtube_shorts_downloader.py`
- `faceswap_cli.py`

## Version History

- **v1.0** (2025-11-20) - Initial release
  - Complete 5-step automated pipeline
  - CPU and GPU support
  - Optional watermarking
  - Customizable output options
  - Comprehensive error handling

## Support

For issues or questions:
- Check this README's Troubleshooting section
- Review individual component READMs:
  - `youtube_shorts_downloader_README.md`
  - `faceswap_cli_README.md`
- Ensure all dependencies are properly installed
- Verify model files are in correct locations

---

**Remember:** Always use ShortSwap responsibly and ethically. Happy face-swapping!
