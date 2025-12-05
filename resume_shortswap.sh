#!/bin/bash
# Resume incomplete ShortSwap job
# Usage: ./resume_shortswap.sh <job_directory> <source_face_image> [--cuda] [--watermark]

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

print_error() { echo -e "${RED}✗ $1${NC}"; }
print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_step() { echo -e "${BLUE}▶ $1${NC}"; }
print_info() { echo -e "${CYAN}ℹ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Default options
USE_CUDA=false
ADD_WATERMARK=false
FRAMERATE=30

# Parse arguments
if [ $# -lt 2 ]; then
    echo "Usage: $0 <job_directory> <source_face_image> [--cuda] [--watermark] [--framerate N]"
    echo ""
    echo "Example:"
    echo "  $0 /home/panda/Documents/ShortSwap_API/outputs/shortswap_dZ5CyD face.jpg --cuda"
    exit 1
fi

JOB_DIR="$1"
SOURCE_FACE="$2"
shift 2

# Parse optional flags
while [ $# -gt 0 ]; do
    case "$1" in
        --cuda)
            USE_CUDA=true
            shift
            ;;
        --watermark)
            ADD_WATERMARK=true
            shift
            ;;
        --framerate)
            FRAMERATE="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Validate job directory
if [ ! -d "$JOB_DIR" ]; then
    print_error "Job directory not found: $JOB_DIR"
    exit 1
fi

if [ ! -d "$JOB_DIR/frames" ]; then
    print_error "Frames directory not found: $JOB_DIR/frames"
    exit 1
fi

if [ ! -d "$JOB_DIR/swapped_frames" ]; then
    print_error "Swapped frames directory not found: $JOB_DIR/swapped_frames"
    exit 1
fi

if [ ! -f "$SOURCE_FACE" ]; then
    print_error "Source face image not found: $SOURCE_FACE"
    exit 1
fi

# Find the original video
ORIGINAL_VIDEO=$(find "$JOB_DIR" -maxdepth 1 -name "*.mp4" | head -n 1)
if [ -z "$ORIGINAL_VIDEO" ]; then
    print_error "Original video not found in $JOB_DIR"
    exit 1
fi

cd "$JOB_DIR"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ${BLUE}ShortSwap Resume${CYAN}                          ║"
echo "║              Resume Incomplete Face-Swap Job                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "Job Directory:  $JOB_DIR"
echo "Source Face:    $SOURCE_FACE"
echo "Original Video: $(basename "$ORIGINAL_VIDEO")"
echo "CUDA Enabled:   $USE_CUDA"
echo "Watermark:      $ADD_WATERMARK"
echo "Framerate:      ${FRAMERATE}fps"
echo ""

# Step 1: Identify missing/incomplete frames
print_step "Step 1/4: Identifying missing or incomplete frames..."

TOTAL_FRAMES=$(ls frames/frame_*.png 2>/dev/null | wc -l)
COMPLETED_FRAMES=$(find swapped_frames -type f -name "frame_*.png" -size +0 2>/dev/null | wc -l)
EMPTY_FRAMES=$(find swapped_frames -type f -name "frame_*.png" -size 0 2>/dev/null | wc -l)
MISSING_FRAMES=$((TOTAL_FRAMES - COMPLETED_FRAMES - EMPTY_FRAMES))

print_info "Total original frames: $TOTAL_FRAMES"
print_info "Successfully swapped: $COMPLETED_FRAMES"
print_warning "Empty/failed frames: $EMPTY_FRAMES"
print_warning "Missing frames: $MISSING_FRAMES"

FRAMES_TO_PROCESS=$((EMPTY_FRAMES + MISSING_FRAMES))

if [ $FRAMES_TO_PROCESS -eq 0 ]; then
    print_success "All frames already completed!"
    echo ""
else
    print_info "Frames to process: $FRAMES_TO_PROCESS"
    echo ""

    # Create temporary directory for incomplete frames
    print_step "Step 2/4: Preparing incomplete frames for processing..."
    rm -rf temp_incomplete_frames
    mkdir -p temp_incomplete_frames

    # Delete all zero-byte swapped frames first
    print_info "Removing empty swapped frames..."
    find swapped_frames -type f -name "frame_*.png" -size 0 -delete

    # Copy frames that don't have a valid swapped version
    COPIED=0
    print_info "Copying frames that need processing..."
    for frame in frames/frame_*.png; do
        frame_name=$(basename "$frame")
        swapped_frame="swapped_frames/$frame_name"

        # If swapped frame doesn't exist or is empty, copy to temp
        if [ ! -f "$swapped_frame" ] || [ ! -s "$swapped_frame" ]; then
            cp "$frame" "temp_incomplete_frames/$frame_name" || true
            ((COPIED++))

            # Show progress every 10 frames
            if [ $((COPIED % 10)) -eq 0 ]; then
                echo -ne "\rCopied $COPIED frames..." >&2
            fi
        fi
    done
    echo -ne "\r" >&2

    print_success "Prepared $COPIED frames for processing"
    echo ""

    # Step 3: Process incomplete frames
    print_step "Step 3/4: Re-processing incomplete frames..."

    # Set up CUDA libraries
    NVIDIA_LIBS="$SCRIPT_DIR/faceswap_venv/lib/python3.13/site-packages/nvidia/cudnn/lib"
    NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/faceswap_venv/lib/python3.13/site-packages/nvidia/cublas/lib"
    NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/faceswap_venv/lib/python3.13/site-packages/nvidia/cufft/lib"
    NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/faceswap_venv/lib/python3.13/site-packages/nvidia/cusolver/lib"
    NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/faceswap_venv/lib/python3.13/site-packages/nvidia/cusparse/lib"
    NVIDIA_LIBS="$NVIDIA_LIBS:$SCRIPT_DIR/faceswap_venv/lib/python3.13/site-packages/nvidia/cuda_runtime/lib"
    export LD_LIBRARY_PATH="$NVIDIA_LIBS:/usr/local/cuda-13.0/lib64:/usr/local/lib/ollama/cuda_v12:$LD_LIBRARY_PATH"

    SWAP_CMD="$SCRIPT_DIR/faceswap_venv/bin/python3 $SCRIPT_DIR/faceswap_cli.py \
        --source \"$SOURCE_FACE\" \
        --target-dir temp_incomplete_frames/ \
        --output-dir swapped_frames/"

    if [ "$USE_CUDA" = true ]; then
        SWAP_CMD="$SWAP_CMD --use-cuda"
    fi

    if [ "$ADD_WATERMARK" = true ]; then
        SWAP_CMD="$SWAP_CMD --watermark"
    fi

    eval $SWAP_CMD

    # Cleanup temp directory
    rm -rf temp_incomplete_frames

    print_success "Re-processing complete"
    echo ""
fi

# Verify all frames are now complete
FINAL_COMPLETED=$(find swapped_frames -type f -name "frame_*.png" -size +0 2>/dev/null | wc -l)
FINAL_EMPTY=$(find swapped_frames -type f -name "frame_*.png" -size 0 2>/dev/null | wc -l)

if [ $FINAL_EMPTY -gt 0 ]; then
    print_error "Still have $FINAL_EMPTY empty frames after re-processing!"
    print_warning "There may be frames with no detectable faces."
    print_info "Removing empty frame files so ffmpeg can use available frames..."
    find swapped_frames -type f -name "frame_*.png" -size 0 -delete
fi

print_success "All frames ready: $FINAL_COMPLETED valid frames"
echo ""

# Step 4: Build final video
print_step "Step 4/4: Building final video..."

# Check if final video already exists
FINAL_VIDEO="$JOB_DIR/swapped_$(basename "$ORIGINAL_VIDEO")"
if [ -f "$FINAL_VIDEO" ]; then
    print_warning "Final video already exists, creating new version..."
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    FINAL_VIDEO="$JOB_DIR/swapped_${TIMESTAMP}.mp4"
fi

# Build video from swapped frames
print_info "Creating video from frames..."
ffmpeg -framerate "$FRAMERATE" -i swapped_frames/frame_%04d.png \
    -c:v libx264 -pix_fmt yuv420p \
    -loglevel error -stats \
    temp_video.mp4

print_success "Video rebuilt"

# Add original audio
print_info "Adding original audio..."
ffmpeg -i temp_video.mp4 -i "$ORIGINAL_VIDEO" \
    -c:v copy -c:a aac -map 0:v:0 -map 1:a:0? \
    -loglevel error -stats \
    "$FINAL_VIDEO"

# Cleanup temp video
rm -f temp_video.mp4

print_success "Audio added"
echo ""

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ${BLUE}✓ JOB COMPLETE${GREEN}                            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo "Final video: $FINAL_VIDEO"
echo "Size: $(du -h "$FINAL_VIDEO" | cut -f1)"
echo ""
