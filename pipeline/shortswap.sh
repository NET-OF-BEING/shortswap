#!/bin/bash
# ShortSwap - Automated YouTube Shorts Face-Swap Pipeline
# Downloads a YouTube Short, swaps faces in every frame, rebuilds with audio

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Default values
SCRIPT_DIR="$HOME/Documents/PythonScripts"
OUTPUT_DIR="$HOME/Videos/ShortSwap"
KEEP_FRAMES=false
USE_CUDA=false
ADD_WATERMARK=false
FRAMERATE=30
GENDER_FILTER="all"
TARGET_PERSON=""

# Print colored message
print_step() {
    echo -e "${CYAN}==>${NC} ${BLUE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗ ERROR:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Show usage
usage() {
    cat << EOF
${CYAN}ShortSwap${NC} - Automated YouTube Shorts Face-Swap Pipeline

${YELLOW}Usage:${NC}
  shortswap.sh --url <YOUTUBE_URL> --face <SOURCE_IMAGE> [OPTIONS]
  shortswap.sh --video <VIDEO_FILE> --face <SOURCE_IMAGE> [OPTIONS]

${YELLOW}Required Arguments:${NC}
  --url, -u URL             YouTube Shorts URL to download
  --video, -v FILE          Local video file to process
  --face, -f IMAGE          Source face image to apply onto video

  Note: Provide either --url OR --video (not both)

${YELLOW}Optional Arguments:${NC}
  --output, -o DIR          Output directory (default: ~/Videos/ShortSwap)
  --name, -n NAME           Output video name (default: auto from video title)
  --framerate, -r FPS       Video framerate (default: 30)
  --gender, -g GENDER       Target gender to swap (male, female, or all). Default: all
  --target-person, -tp IMG  Reference image of specific person to target
  --watermark, -w           Add watermark to frames
  --cuda                    Use CUDA/GPU for face swapping
  --keep-frames             Keep intermediate frame directories
  --help, -h                Show this help message

${YELLOW}Examples:${NC}
  # Basic usage with YouTube URL
  shortswap.sh -u https://youtube.com/shorts/abc123 -f my_face.jpg

  # Basic usage with local video file
  shortswap.sh -v ~/Videos/my_video.mp4 -f my_face.jpg

  # With custom output and GPU
  shortswap.sh -u https://youtube.com/shorts/abc123 -f my_face.jpg \\
    --output ~/Desktop --name "my_video" --cuda

  # Keep frames for inspection
  shortswap.sh -v video.mp4 -f face.jpg --keep-frames

${YELLOW}The 5-Step Pipeline:${NC}
  1. Download YouTube Short (yt-dlp)
  2. Extract video into frames (ffmpeg)
  3. Batch face-swap all frames (impostr_cli.py)
  4. Rebuild video from swapped frames (ffmpeg)
  5. Add original audio to final video (ffmpeg)

${YELLOW}Output:${NC}
  Final video saved to: <output-dir>/<video-name>_swapped.mp4

EOF
    exit 0
}

# Parse arguments
if [ $# -eq 0 ]; then
    usage
fi

while [[ $# -gt 0 ]]; do
    case $1 in
        --url|-u)
            YOUTUBE_URL="$2"
            shift 2
            ;;
        --video|-v)
            LOCAL_VIDEO="$2"
            shift 2
            ;;
        --face|-f)
            SOURCE_FACE="$2"
            shift 2
            ;;
        --output|-o)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --name|-n)
            OUTPUT_NAME="$2"
            shift 2
            ;;
        --framerate|-r)
            FRAMERATE="$2"
            shift 2
            ;;
        --gender|-g)
            GENDER_FILTER="$2"
            shift 2
            ;;
        --target-person|-tp)
            TARGET_PERSON="$2"
            shift 2
            ;;
        --watermark|-w)
            ADD_WATERMARK=true
            shift
            ;;
        --cuda)
            USE_CUDA=true
            shift
            ;;
        --keep-frames)
            KEEP_FRAMES=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Validate required arguments
if [ -z "$YOUTUBE_URL" ] && [ -z "$LOCAL_VIDEO" ]; then
    print_error "Either YouTube URL (--url) or local video file (--video) is required"
    exit 1
fi

if [ -n "$YOUTUBE_URL" ] && [ -n "$LOCAL_VIDEO" ]; then
    print_error "Cannot use both --url and --video. Choose one."
    exit 1
fi

if [ -z "$SOURCE_FACE" ]; then
    print_error "Source face image is required (--face)"
    exit 1
fi

if [ ! -f "$SOURCE_FACE" ]; then
    print_error "Source face file not found: $SOURCE_FACE"
    exit 1
fi

if [ -n "$LOCAL_VIDEO" ] && [ ! -f "$LOCAL_VIDEO" ]; then
    print_error "Local video file not found: $LOCAL_VIDEO"
    exit 1
fi

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Create temporary working directory
WORK_DIR=$(mktemp -d -p "$OUTPUT_DIR" shortswap_XXXXXX)
cd "$WORK_DIR"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                         ${BLUE}ShortSwap${CYAN}                            ║"
echo "║              Video Face-Swap Pipeline                         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
if [ -n "$YOUTUBE_URL" ]; then
    echo "YouTube URL:    $YOUTUBE_URL"
else
    echo "Video File:     $LOCAL_VIDEO"
fi
echo "Source Face:    $SOURCE_FACE"
echo "Output Dir:     $OUTPUT_DIR"
echo "Working Dir:    $WORK_DIR"
echo "Framerate:      ${FRAMERATE}fps"
echo "CUDA Enabled:   $USE_CUDA"
echo "Watermark:      $ADD_WATERMARK"
echo ""

# Step 1: Get video (download or copy)
if [ -n "$YOUTUBE_URL" ]; then
    print_step "Step 1/5: Downloading YouTube Short..."
    python3 "$SCRIPT_DIR/youtube_shorts_downloader.py" "$YOUTUBE_URL" --output "$WORK_DIR"

    # Find the downloaded video (should be the only mp4 in work dir)
    ORIGINAL_VIDEO=$(find "$WORK_DIR" -maxdepth 1 -name "*.mp4" | head -n 1)

    if [ -z "$ORIGINAL_VIDEO" ]; then
        print_error "Failed to find downloaded video"
        exit 1
    fi

    VIDEO_BASENAME=$(basename "$ORIGINAL_VIDEO" .mp4)
    print_success "Downloaded: $VIDEO_BASENAME"
else
    print_step "Step 1/5: Using local video file..."
    ORIGINAL_VIDEO="$WORK_DIR/$(basename "$LOCAL_VIDEO")"
    cp "$LOCAL_VIDEO" "$ORIGINAL_VIDEO"
    VIDEO_BASENAME=$(basename "$ORIGINAL_VIDEO" .mp4)
    print_success "Video ready: $VIDEO_BASENAME"
fi
echo ""

# Step 2: Extract frames
print_step "Step 2/5: Extracting video frames..."
mkdir -p frames
ffmpeg -i "$ORIGINAL_VIDEO" -loglevel error -stats frames/frame_%04d.png

FRAME_COUNT=$(ls frames/frame_*.png 2>/dev/null | wc -l)
print_success "Extracted $FRAME_COUNT frames"
echo ""

# Step 3: Batch face-swap
print_step "Step 3/5: Face-swapping all frames..."
mkdir -p swapped_frames

# Add CUDA libraries to library path (CUDA 11 from pip packages + CUDA 13 system)
NVIDIA_LIBS="$SCRIPT_DIR/impostr_venv/lib/python3.13/site-packages/nvidia/cudnn/lib"
NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/impostr_venv/lib/python3.13/site-packages/nvidia/cublas/lib"
NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/impostr_venv/lib/python3.13/site-packages/nvidia/cufft/lib"
NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/impostr_venv/lib/python3.13/site-packages/nvidia/cusolver/lib"
NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/impostr_venv/lib/python3.13/site-packages/nvidia/cusparse/lib"
NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/impostr_venv/lib/python3.13/site-packages/nvidia/cuda_runtime/lib"
export LD_LIBRARY_PATH="$NVIDIA_LIBS:/usr/local/cuda-13.0/lib64:/usr/local/lib/ollama/cuda_v12:$LD_LIBRARY_PATH"

SWAP_CMD="$SCRIPT_DIR/impostr_venv/bin/python3 $SCRIPT_DIR/impostr_cli.py \
    --source \"$SOURCE_FACE\" \
    --target-dir frames/ \
    --output-dir swapped_frames/"

if [ "$USE_CUDA" = true ]; then
    SWAP_CMD="$SWAP_CMD --use-cuda"
fi

if [ "$ADD_WATERMARK" = true ]; then
    SWAP_CMD="$SWAP_CMD --watermark"
fi

if [ "$GENDER_FILTER" != "all" ]; then
    SWAP_CMD="$SWAP_CMD --gender $GENDER_FILTER"
fi

if [ -n "$TARGET_PERSON" ]; then
    SWAP_CMD="$SWAP_CMD --target-person \"$TARGET_PERSON\""
fi

eval $SWAP_CMD

print_success "All frames processed"
echo ""

# Step 4: Rebuild video from frames
print_step "Step 4/5: Rebuilding video from swapped frames..."
ffmpeg -framerate "$FRAMERATE" -i swapped_frames/frame_%04d.png \
    -c:v libx264 -pix_fmt yuv420p \
    -loglevel error -stats \
    temp_video.mp4

print_success "Video rebuilt"
echo ""

# Step 5: Add original audio
print_step "Step 5/5: Adding original audio..."

# Determine output filename
if [ -z "$OUTPUT_NAME" ]; then
    FINAL_OUTPUT="$OUTPUT_DIR/${VIDEO_BASENAME}_swapped.mp4"
else
    FINAL_OUTPUT="$OUTPUT_DIR/${OUTPUT_NAME}.mp4"
fi

ffmpeg -i temp_video.mp4 -i "$ORIGINAL_VIDEO" \
    -c copy \
    -map 0:v:0 -map 1:a:0 \
    -loglevel error -stats \
    "$FINAL_OUTPUT"

print_success "Audio added"
echo ""

# Cleanup
if [ "$KEEP_FRAMES" = false ]; then
    print_step "Cleaning up temporary files..."
    cd "$OUTPUT_DIR"
    rm -rf "$WORK_DIR"
    print_success "Cleanup complete"
else
    print_warning "Keeping frame directories at: $WORK_DIR"
fi

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}                    ${GREEN}✓ ShortSwap Complete!${NC}                    ${CYAN}║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Final video saved to:${NC}"
echo -e "  ${BLUE}$FINAL_OUTPUT${NC}"
echo ""

# Show file info
FILE_SIZE=$(du -h "$FINAL_OUTPUT" | cut -f1)
echo "File size: $FILE_SIZE"
echo ""
print_success "ShortSwap pipeline completed successfully!"
