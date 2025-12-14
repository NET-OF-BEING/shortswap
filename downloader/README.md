# YouTube Shorts Downloader

Download YouTube Shorts videos easily from the command line.

## Location
- **Python Script:** `/home/panda/Documents/PythonScripts/youtube_shorts_downloader.py`
- **Bash Wrapper:** `/home/panda/Documents/PythonScripts/download_short.sh`

## Requirements

- Python 3.x
- yt-dlp (already installed on your system)

If yt-dlp is not installed:
```bash
pip install yt-dlp
```

## Usage

### Quick Start

```bash
# Using the bash wrapper (easiest)
/home/panda/Documents/PythonScripts/download_short.sh https://youtube.com/shorts/abc123

# Or directly with Python
python3 /home/panda/Documents/PythonScripts/youtube_shorts_downloader.py https://youtube.com/shorts/abc123
```

### Download to Default Location

Videos are saved to `~/Videos/YouTubeShorts/` by default:

```bash
./download_short.sh https://youtube.com/shorts/abc123
```

### Download to Custom Directory

```bash
./download_short.sh https://youtube.com/shorts/abc123 --output ~/Downloads
```

### Download Multiple Shorts

```bash
./download_short.sh \
  https://youtube.com/shorts/abc123 \
  https://youtube.com/shorts/def456 \
  https://youtube.com/shorts/ghi789
```

## Features

- Downloads best available quality
- Shows download progress (percentage, speed, ETA)
- Displays video title and duration
- Creates output directory automatically
- Supports batch downloads
- Works with YouTube Shorts URLs

## Examples

### Example 1: Single Short
```bash
./download_short.sh https://youtube.com/shorts/dQw4w9WgXcQ
```

Output:
```
Downloading from: https://youtube.com/shorts/dQw4w9WgXcQ
Saving to: /home/panda/Videos/YouTubeShorts

Title: Amazing Dance Move
Duration: 45s
Downloading...

Progress: 100% | Speed: 2.5MB/s | ETA: 00:00
Processing video...

✓ Successfully downloaded: Amazing Dance Move
```

### Example 2: Custom Output Directory
```bash
./download_short.sh https://youtube.com/shorts/abc123 -o ~/Desktop
```

### Example 3: Multiple Downloads
```bash
./download_short.sh \
  https://youtube.com/shorts/abc123 \
  https://youtube.com/shorts/def456
```

## Command-Line Options

```
positional arguments:
  urls                  YouTube Shorts URL(s) to download

options:
  -h, --help            Show help message
  -o, --output DIR      Output directory (default: ~/Videos/YouTubeShorts)
```

## File Naming

Downloaded files are saved with the video title as filename:
```
~/Videos/YouTubeShorts/
  Amazing Dance Move.mp4
  Funny Cat Compilation.mp4
  Quick Recipe Tutorial.mp4
```

## Supported URL Formats

- `https://youtube.com/shorts/abc123`
- `https://www.youtube.com/shorts/abc123`
- `https://youtu.be/abc123` (also works)
- `https://m.youtube.com/shorts/abc123`

## Troubleshooting

### "yt-dlp not installed" Error
```bash
pip install yt-dlp
```

### Permission Denied
```bash
chmod +x /home/panda/Documents/PythonScripts/download_short.sh
```

### Download Fails
- Check internet connection
- Verify the URL is correct
- Some videos may be region-restricted
- Age-restricted videos might not download

### Slow Download Speed
- yt-dlp downloads at your maximum internet speed
- YouTube may throttle downloads during peak hours

## Tips

### Create an Alias
Add to your `~/.bashrc`:
```bash
alias dlshort='/home/panda/Documents/PythonScripts/download_short.sh'
```

Then reload:
```bash
source ~/.bashrc
```

Now you can just type:
```bash
dlshort https://youtube.com/shorts/abc123
```

### Download from Clipboard
```bash
dlshort "$(xclip -o)"
```

## Advanced Usage

### Download Audio Only
Modify the script's `ydl_opts` to include:
```python
'format': 'bestaudio/best',
```

### Download Specific Quality
```python
'format': 'best[height<=720]',  # Max 720p
```

## Notes

- Downloads respect YouTube's terms of service
- Only download videos you have permission to download
- Downloaded videos are for personal use only
- Some videos may have copyright restrictions
