#!/usr/bin/env python3
"""
YouTube Shorts Downloader
Downloads YouTube Shorts videos by URL

Usage:
    python youtube_shorts_downloader.py <URL>
    python youtube_shorts_downloader.py https://youtube.com/shorts/abc123
"""

import sys
import os
import argparse
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("ERROR: yt-dlp not installed")
    print("Install with: pip install yt-dlp")
    sys.exit(1)


def download_short(url, output_dir=None):
    """
    Download a YouTube Short

    Args:
        url: YouTube Shorts URL
        output_dir: Directory to save the video (default: ~/Videos/YouTubeShorts)
    """
    # Default output directory
    if output_dir is None:
        output_dir = os.path.expanduser("~/Videos/YouTubeShorts")

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Output template (saves as: VideoTitle.mp4)
    output_template = os.path.join(output_dir, '%(title)s.%(ext)s')

    # yt-dlp options
    ydl_opts = {
        'format': 'best',  # Download best quality
        'outtmpl': output_template,
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [progress_hook],
    }

    try:
        print(f"Downloading from: {url}")
        print(f"Saving to: {output_dir}\n")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Get video info
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            duration = info.get('duration', 0)

            print(f"Title: {title}")
            print(f"Duration: {duration}s")
            print(f"Downloading...\n")

            # Download
            ydl.download([url])

            print(f"\n✓ Successfully downloaded: {title}")

    except Exception as e:
        print(f"\n✗ Error downloading video: {str(e)}")
        sys.exit(1)


def progress_hook(d):
    """Display download progress"""
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', 'N/A')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}", end='', flush=True)
    elif d['status'] == 'finished':
        print("\nProcessing video...")


def main():
    parser = argparse.ArgumentParser(
        description="Download YouTube Shorts videos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download a short
  python youtube_shorts_downloader.py https://youtube.com/shorts/abc123

  # Download to custom directory
  python youtube_shorts_downloader.py https://youtube.com/shorts/abc123 --output ~/Downloads

  # Download multiple shorts
  python youtube_shorts_downloader.py URL1 URL2 URL3
        """
    )

    parser.add_argument('urls', nargs='+', help='YouTube Shorts URL(s) to download')
    parser.add_argument('--output', '-o', help='Output directory (default: ~/Videos/YouTubeShorts)')

    args = parser.parse_args()

    # Download each URL
    for i, url in enumerate(args.urls, 1):
        if len(args.urls) > 1:
            print(f"\n{'='*60}")
            print(f"Downloading video {i}/{len(args.urls)}")
            print(f"{'='*60}\n")

        download_short(url, args.output)

    print(f"\n{'='*60}")
    print(f"All downloads complete! ({len(args.urls)} video(s))")
    print(f"{'='*60}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Usage: python youtube_shorts_downloader.py <URL>")
        print("Example: python youtube_shorts_downloader.py https://youtube.com/shorts/abc123")
        print("\nFor more options, use: python youtube_shorts_downloader.py --help")
        sys.exit(1)

    main()
