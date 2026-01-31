#!/usr/bin/env python3
"""
Download meeting videos from YouTube using yt-dlp.

This script downloads videos to a temporary directory for transcription.
Videos are never committed to the repository.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("Error: yt-dlp is not installed. Install with: pip install -r scripts/requirements.txt")
    sys.exit(1)


def download_meeting(youtube_url, date, entity):
    """
    Download a meeting video from YouTube.

    Args:
        youtube_url: YouTube video URL
        date: Meeting date in YYYY-MM-DD format
        entity: Entity identifier (dlcd, tualatin, etc.)

    Returns:
        Path to downloaded video file
    """
    # Create temp directory if it doesn't exist
    temp_dir = Path("/tmp/oregon-housing-meetings")
    temp_dir.mkdir(parents=True, exist_ok=True)

    # Construct output filename
    output_filename = f"{date}-{entity}.mp4"
    output_path = temp_dir / output_filename

    # Skip if file already exists
    if output_path.exists():
        print(f"Video already exists at {output_path}")
        print("Skipping download.")
        return output_path

    # Configure yt-dlp options
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': str(output_path),
        'quiet': False,
        'no_warnings': False,
    }

    try:
        print(f"Downloading video from {youtube_url}")
        print(f"Output: {output_path}")

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

        print(f"\nDownload complete: {output_path}")
        return output_path

    except yt_dlp.utils.DownloadError as e:
        print(f"Error downloading video: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Download meeting videos from YouTube"
    )
    parser.add_argument(
        "--url",
        required=True,
        help="YouTube video URL"
    )
    parser.add_argument(
        "--date",
        required=True,
        help="Meeting date in YYYY-MM-DD format"
    )
    parser.add_argument(
        "--entity",
        required=True,
        choices=["dlcd", "tualatin"],
        help="Entity identifier (dlcd or tualatin)"
    )

    args = parser.parse_args()

    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format", file=sys.stderr)
        sys.exit(1)

    output_path = download_meeting(args.url, args.date, args.entity)
    print(f"\nVideo saved to: {output_path}")


if __name__ == "__main__":
    main()
