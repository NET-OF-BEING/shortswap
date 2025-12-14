# Face Swap CLI

Command-line interface for batch face swapping, extracted from the Impostr Face Swap Studio GUI.

## Description

This tool allows you to swap faces in images from the command line, making it perfect for:
- Batch processing multiple images
- Processing video frames
- Automation and scripting
- Integration into workflows

## Requirements

- Python 3.x
- InsightFace
- OpenCV (cv2)
- NumPy
- Pillow (PIL)
- inswapper_128.onnx model file (must be in `models/` directory)

## Installation

The script uses the same environment as the face_swap_gui. If you already have the GUI working, you're all set.

If not, install dependencies:
```bash
pip install insightface opencv-python numpy pillow
```

**Important:** You need the `inswapper_128.onnx` model file in a `models/` subdirectory relative to where you run the script.

## Basic Usage

### Single Image Swap

Swap one face into one image:

```bash
python impostr_cli.py --source my_face.jpg --target scene.jpg --output result.jpg
```

- `--source`: Your face (the face to copy FROM)
- `--target`: The image to modify (the image to apply face ONTO)
- `--output`: Where to save the result

### Batch Processing (Directory)

Process multiple images at once:

```bash
python impostr_cli.py --source my_face.jpg --target-dir frames/ --output-dir swapped/
```

- `--source`: Your face (same as above)
- `--target-dir`: Directory containing images to process
- `--output-dir`: Directory where swapped images will be saved

The script will process all images (.jpg, .jpeg, .png, .bmp, .tiff, .webp) in the target directory.

## Command-Line Options

```
Required Arguments:
  --source, -s          Source image with the face to copy FROM

  One of:
  --target, -t          Single target image to apply face ONTO
  --target-dir, -td     Directory containing target images to process

Output:
  --output, -o          Output path for single image swap (required with --target)
  --output-dir, -od     Output directory for batch processing (required with --target-dir)

Optional:
  --watermark, -w       Add watermark to output images
  --use-cuda            Use CUDA/GPU if available (default: CPU)
  --help, -h            Show help message
```

## Video Face Swap Workflow

Perfect for swapping faces in video scenes!

### Step 1: Extract Video Frames

```bash
# Extract all frames at 30fps
ffmpeg -i input_video.mp4 frames/frame_%04d.png

# This creates: frame_0001.png, frame_0002.png, ... frame_0900.png (for 30 sec video)
```

### Step 2: Batch Process Frames

```bash
# Swap your face onto all frames
python impostr_cli.py \
  --source my_face.jpg \
  --target-dir frames/ \
  --output-dir swapped_frames/
```

The script will show progress:
```
Batch processing 900 images:
  Source: my_face.jpg
  Target dir: frames/
  Output dir: swapped_frames/

[1/900] Processing frame_0001.png... ✓
[2/900] Processing frame_0002.png... ✓
[3/900] Processing frame_0003.png... ✓
...
```

### Step 3: Reassemble Frames into Video

```bash
# Create video from swapped frames
ffmpeg -framerate 30 -i swapped_frames/frame_%04d.png \
  -c:v libx264 -pix_fmt yuv420p output_video.mp4
```

### Step 4: Add Original Audio (Optional)

```bash
# Copy audio from original video to swapped video
ffmpeg -i output_video.mp4 -i input_video.mp4 \
  -c copy -map 0:v:0 -map 1:a:0 final_output.mp4
```

### Complete Video Pipeline (One-liner per step)

```bash
# Extract frames
ffmpeg -i input.mp4 frames/frame_%04d.png

# Swap faces
python impostr_cli.py -s my_face.jpg -td frames/ -od swapped/

# Reassemble with audio
ffmpeg -framerate 30 -i swapped/frame_%04d.png -c:v libx264 -pix_fmt yuv420p temp.mp4
ffmpeg -i temp.mp4 -i input.mp4 -c copy -map 0:v:0 -map 1:a:0 output.mp4
```

## Examples

### Example 1: Simple Face Swap
```bash
python impostr_cli.py \
  --source derek_face.jpg \
  --target movie_scene.jpg \
  --output derek_in_scene.jpg
```

### Example 2: Batch Process with Watermark
```bash
python impostr_cli.py \
  --source my_face.jpg \
  --target-dir photos/ \
  --output-dir swapped_photos/ \
  --watermark
```

### Example 3: Using CUDA for Faster Processing
```bash
python impostr_cli.py \
  --source face.jpg \
  --target-dir frames/ \
  --output-dir swapped/ \
  --use-cuda
```

## Tips for Video Face Swapping

**Best Results:**
- Use scenes where the head stays relatively still
- Single camera angle works better than dynamic shots
- Good lighting in both source face and target video
- Higher resolution source face = better quality

**Performance:**
- Processing 900 frames (30 sec video) takes time
- Use `--use-cuda` if you have a compatible GPU
- CPU processing: ~1-3 seconds per frame
- GPU processing: ~0.1-0.5 seconds per frame

**File Management:**
- 900 PNG frames can take ~2-5 GB of space
- Clean up intermediate frames after reassembly
- Use organized directory structure:
  ```
  project/
    input_video.mp4
    my_face.jpg
    frames/         (extracted frames)
    swapped/        (processed frames)
    output.mp4      (final video)
  ```

## Troubleshooting

**"Missing swapper model" error:**
- Download `inswapper_128.onnx` model
- Place it in `models/inswapper_128.onnx` relative to script location

**"No face detected in source/target" error:**
- Ensure faces are clearly visible
- Try images with better lighting
- Face should be front-facing and unobstructed

**Slow processing:**
- Use `--use-cuda` if you have a GPU
- Process smaller batches
- Use lower resolution frames if quality isn't critical

**CUDA not working:**
- Install CUDA-enabled version of ONNX Runtime:
  ```bash
  pip install onnxruntime-gpu
  ```

## Model Location

The script expects the model at:
```
models/inswapper_128.onnx
```

If running from `/home/panda/Documents/PythonScripts/`, create:
```
/home/panda/Documents/PythonScripts/models/inswapper_128.onnx
```

Or run the script from the same directory as your GUI installation where the model already exists.

## Credits

Extracted from Impostr - Ultimate Face Swap Studio GUI
Uses InsightFace for face detection and swapping
