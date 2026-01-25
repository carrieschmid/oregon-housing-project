#!/usr/bin/env python3
"""
Transcribe meeting videos using OpenAI Whisper.

This script processes video files and generates timestamped transcripts.
"""

import argparse
import os
import sys
from pathlib import Path

try:
    import whisper
except ImportError:
    print("Error: openai-whisper is not installed. Install with: pip install -r scripts/requirements.txt")
    sys.exit(1)


def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def transcribe_meeting(video_path, model_size="medium"):
    """
    Transcribe a meeting video using Whisper.

    Args:
        video_path: Path to video file
        model_size: Whisper model size (tiny, base, small, medium, large)

    Returns:
        Path to transcript file
    """
    video_path = Path(video_path)

    if not video_path.exists():
        print(f"Error: Video file not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    # Construct output filename
    # Extract date and entity from video filename (YYYY-MM-DD-entity.mp4)
    video_stem = video_path.stem
    transcript_filename = f"{video_stem}-transcript.txt"
    transcript_path = video_path.parent / transcript_filename

    # Skip if transcript already exists
    if transcript_path.exists():
        print(f"Transcript already exists at {transcript_path}")
        print("Skipping transcription.")
        return transcript_path

    print(f"Loading Whisper model: {model_size}")
    print("This may take a moment on first run...")

    try:
        model = whisper.load_model(model_size)
    except Exception as e:
        print(f"Error loading Whisper model: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"\nTranscribing video: {video_path}")
    print("This may take several minutes depending on video length...")

    try:
        # Transcribe with word-level timestamps
        result = model.transcribe(
            str(video_path),
            verbose=True,
            word_timestamps=False
        )

        # Write transcript with timestamps
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write("# Meeting Transcript\n\n")

            for segment in result['segments']:
                timestamp = format_timestamp(segment['start'])
                text = segment['text'].strip()
                f.write(f"[{timestamp}] {text}\n\n")

        print(f"\nTranscription complete: {transcript_path}")
        return transcript_path

    except Exception as e:
        print(f"Error during transcription: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Transcribe meeting videos using OpenAI Whisper"
    )
    parser.add_argument(
        "--video",
        required=True,
        help="Path to video file"
    )
    parser.add_argument(
        "--model",
        default="medium",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: medium)"
    )

    args = parser.parse_args()

    transcript_path = transcribe_meeting(args.video, args.model)
    print(f"\nTranscript saved to: {transcript_path}")


if __name__ == "__main__":
    main()
