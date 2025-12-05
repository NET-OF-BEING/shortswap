#!/home/panda/Documents/PythonScripts/faceswap_venv/bin/python3
"""
Face Swap CLI - Command-line interface for batch face swapping
Extracted from face_swap_gui_LATEST_FEATURES_V2.py

Usage:
    python faceswap_cli.py --source face.jpg --target scene.jpg --output result.jpg
    python faceswap_cli.py --source face.jpg --target-dir frames/ --output-dir swapped/
"""

import os
import sys
import argparse
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import insightface
from insightface.app import FaceAnalysis

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, "models", "inswapper_128.onnx")


def add_watermark(pil_img, text="AI face-swap (consented)"):
    """Add a watermark to the image"""
    draw = ImageDraw.Draw(pil_img, "RGBA")
    W, H = pil_img.size
    margin = int(min(W, H) * 0.02)
    font_size = max(14, int(min(W, H) * 0.035))
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = W - text_w - margin
    y = H - text_h - margin
    draw.rectangle([x - 6, y - 4, x + text_w + 6, y + text_h + 4], fill=(0, 0, 0, 90))
    draw.text((x, y), text, fill=(255, 255, 255, 210), font=font)
    return pil_img


class FaceSwapper:
    """Core face swapping engine using InsightFace"""

    def __init__(self, providers=None):
        print("Initializing face analysis model...")
        self.app = FaceAnalysis(name="buffalo_l")
        self.app.prepare(ctx_id=0, det_size=(640, 640))

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Missing swapper model: {MODEL_PATH}\n"
                "Download inswapper_128.onnx and place it under models/"
            )

        print("Loading face swapper model...")
        self.swapper = insightface.model_zoo.get_model(
            MODEL_PATH, download=False,
            providers=providers or ["CPUExecutionProvider"]
        )
        print("Model loaded successfully!")

    def load_img(self, path):
        """Load image from path"""
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Failed to read image: {path}")
        return img

    def detect_faces(self, img):
        """Detect all faces in image"""
        return self.app.get(img)

    def pick_largest_face(self, faces):
        """Pick the largest face from detected faces"""
        if not faces:
            return None
        areas = [(f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]) for f in faces]
        return faces[int(np.argmax(areas))]

    def filter_faces_by_gender(self, faces, target_gender):
        """
        Filter faces by gender

        Args:
            faces: List of detected faces
            target_gender: 'male' or 'female' or None (for all faces)

        Returns:
            List of faces matching the target gender
        """
        if not target_gender or target_gender.lower() == 'all':
            return faces

        filtered = []
        for face in faces:
            # InsightFace gender: 0 = female, 1 = male
            if hasattr(face, 'gender'):
                if target_gender.lower() == 'male' and face.gender == 1:
                    filtered.append(face)
                elif target_gender.lower() == 'female' and face.gender == 0:
                    filtered.append(face)

        return filtered

    def find_most_similar_face(self, faces, reference_embedding, threshold=0.3):
        """
        Find the face most similar to a reference embedding

        Args:
            faces: List of detected faces
            reference_embedding: Face embedding from reference image
            threshold: Minimum similarity threshold (0-1, higher = more strict)

        Returns:
            Most similar face, or None if no match above threshold
        """
        if not faces or reference_embedding is None:
            return None

        best_face = None
        best_similarity = -1

        for face in faces:
            if hasattr(face, 'embedding'):
                # Compute cosine similarity
                similarity = np.dot(face.embedding, reference_embedding) / (
                    np.linalg.norm(face.embedding) * np.linalg.norm(reference_embedding)
                )

                if similarity > best_similarity and similarity > threshold:
                    best_similarity = similarity
                    best_face = face

        return best_face

    def swap_once(self, target_bgr, target_face, source_face, paste_back=True):
        """Perform a single face swap"""
        return self.swapper.get(target_bgr, target_face, source_face, paste_back=paste_back)


def swap_faces(swapper, src_path, tgt_path, add_watermark_flag=False, target_gender=None, target_person_embedding=None):
    """
    Swap faces from source to target image

    Args:
        swapper: FaceSwapper instance
        src_path: Path to source image (face to copy FROM)
        tgt_path: Path to target image (image to apply face ONTO)
        add_watermark_flag: Whether to add watermark
        target_gender: Gender filter ('male', 'female', or None for all)
        target_person_embedding: Face embedding from target person reference (optional)

    Returns:
        PIL Image with swapped face, or None if failed
    """
    try:
        # Load images
        src_bgr = swapper.load_img(src_path)
        tgt_bgr = swapper.load_img(tgt_path)

        # Detect source face
        src_faces = swapper.detect_faces(src_bgr)
        if not src_faces:
            print(f"ERROR: No face detected in source image: {src_path}")
            return None
        src_face = swapper.pick_largest_face(src_faces)

        # Detect target faces
        tgt_faces = swapper.detect_faces(tgt_bgr)
        if not tgt_faces:
            # No face detected - return original image unchanged
            rgb = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2RGB)
            pil = Image.fromarray(rgb)
            if add_watermark_flag:
                pil = add_watermark(pil)
            return pil

        # If target person embedding provided, find most similar face
        if target_person_embedding is not None:
            matched_face = swapper.find_most_similar_face(tgt_faces, target_person_embedding)
            if matched_face:
                tgt_faces = [matched_face]
            else:
                # No similar face found - return original image
                rgb = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2RGB)
                return Image.fromarray(rgb)
        # Otherwise filter by gender if specified
        elif target_gender:
            filtered_faces = swapper.filter_faces_by_gender(tgt_faces, target_gender)
            if not filtered_faces:
                # No faces matching gender filter - return original image
                rgb = cv2.cvtColor(tgt_bgr, cv2.COLOR_BGR2RGB)
                return Image.fromarray(rgb)
            tgt_faces = filtered_faces

        # Swap all matching faces (or just matched face if using similarity)
        result = tgt_bgr.copy()
        for face in tgt_faces:
            result = swapper.swap_once(result, face, src_face, paste_back=True)

        # Convert to PIL Image
        rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        pil = Image.fromarray(rgb)

        # Add watermark if requested
        if add_watermark_flag:
            pil = add_watermark(pil)

        return pil

    except Exception as e:
        print(f"ERROR processing {tgt_path}: {str(e)}")
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Face Swap CLI - Swap faces in images",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single image swap
  python faceswap_cli.py --source my_face.jpg --target scene.jpg --output result.jpg

  # Batch process directory
  python faceswap_cli.py --source my_face.jpg --target-dir frames/ --output-dir swapped/

  # With watermark
  python faceswap_cli.py --source face.jpg --target scene.jpg --output result.jpg --watermark
        """
    )

    # Source face (required)
    parser.add_argument('--source', '-s', required=True,
                        help='Source image with the face to copy FROM')

    # Target options (single file OR directory)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--target', '-t',
                       help='Single target image to apply face ONTO')
    group.add_argument('--target-dir', '-td',
                       help='Directory containing target images to process')

    # Output options
    parser.add_argument('--output', '-o',
                        help='Output path for single image swap')
    parser.add_argument('--output-dir', '-od',
                        help='Output directory for batch processing')

    # Options
    parser.add_argument('--watermark', '-w', action='store_true',
                        help='Add watermark to output images')
    parser.add_argument('--use-cuda', action='store_true',
                        help='Use CUDA if available (default: CPU)')
    parser.add_argument('--gender', '-g', choices=['male', 'female', 'all'], default='all',
                        help='Target gender to swap (male, female, or all). Default: all')
    parser.add_argument('--target-person', '-tp',
                        help='Reference image of specific person to target (for selective swapping)')

    args = parser.parse_args()

    # Validate arguments
    if args.target and not args.output:
        parser.error("--output is required when using --target")
    if args.target_dir and not args.output_dir:
        parser.error("--output-dir is required when using --target-dir")

    # Check source file exists
    if not os.path.exists(args.source):
        print(f"ERROR: Source file not found: {args.source}")
        sys.exit(1)

    # Initialize face swapper
    providers = ["CUDAExecutionProvider"] if args.use_cuda else ["CPUExecutionProvider"]
    swapper = FaceSwapper(providers=providers)

    # Extract target person embedding if provided
    target_person_embedding = None
    if args.target_person:
        if not os.path.exists(args.target_person):
            print(f"ERROR: Target person file not found: {args.target_person}")
            sys.exit(1)

        print(f"Extracting face embedding from target person: {args.target_person}")
        tp_bgr = swapper.load_img(args.target_person)
        tp_faces = swapper.detect_faces(tp_bgr)
        if not tp_faces:
            print(f"ERROR: No face detected in target person image: {args.target_person}")
            sys.exit(1)
        tp_face = swapper.pick_largest_face(tp_faces)
        target_person_embedding = tp_face.embedding
        print(f"✓ Target person embedding extracted")

    # Determine gender filter
    gender_filter = None if args.gender == 'all' else args.gender

    # Process single image
    if args.target:
        if not os.path.exists(args.target):
            print(f"ERROR: Target file not found: {args.target}")
            sys.exit(1)

        print(f"\nSwapping faces:")
        print(f"  Source: {args.source}")
        print(f"  Target: {args.target}")
        print(f"  Output: {args.output}")
        if gender_filter:
            print(f"  Gender filter: {gender_filter}")
        if target_person_embedding is not None:
            print(f"  Target person: Using similarity matching")

        result = swap_faces(swapper, args.source, args.target, args.watermark, gender_filter, target_person_embedding)
        if result:
            os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
            result.save(args.output)
            print(f"✓ Success! Saved to {args.output}")
        else:
            print("✗ Failed to swap faces")
            sys.exit(1)

    # Process directory
    elif args.target_dir:
        if not os.path.isdir(args.target_dir):
            print(f"ERROR: Target directory not found: {args.target_dir}")
            sys.exit(1)

        # Create output directory
        os.makedirs(args.output_dir, exist_ok=True)

        # Get all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        target_files = [
            f for f in os.listdir(args.target_dir)
            if os.path.splitext(f.lower())[1] in image_extensions
        ]

        if not target_files:
            print(f"ERROR: No image files found in {args.target_dir}")
            sys.exit(1)

        print(f"\nBatch processing {len(target_files)} images:")
        print(f"  Source: {args.source}")
        print(f"  Target dir: {args.target_dir}")
        print(f"  Output dir: {args.output_dir}")
        if gender_filter:
            print(f"  Gender filter: {gender_filter}")
        if target_person_embedding is not None:
            print(f"  Target person: Using similarity matching")
        print()

        success_count = 0
        for i, filename in enumerate(target_files, 1):
            target_path = os.path.join(args.target_dir, filename)
            output_path = os.path.join(args.output_dir, filename)

            print(f"[{i}/{len(target_files)}] Processing {filename}...", end=' ')

            result = swap_faces(swapper, args.source, target_path, args.watermark, gender_filter, target_person_embedding)
            if result:
                result.save(output_path)
                print("✓")
                success_count += 1
            else:
                print("✗ (processing error)")

        print(f"\nCompleted: {success_count}/{len(target_files)} images successfully processed")
        if success_count < len(target_files):
            sys.exit(1)


if __name__ == "__main__":
    main()
