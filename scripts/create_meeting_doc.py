#!/usr/bin/env python3
"""
Create Hugo markdown documents for meeting transcripts.

This script generates properly formatted meeting documentation with
front matter, summary sections, and full transcripts.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


def format_date_for_title(date_str):
    """Convert YYYY-MM-DD to 'Month DD, YYYY' format."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%B %d, %Y")


def get_entity_config(entity):
    """
    Get configuration for each entity type.

    Returns:
        dict with 'path', 'filename', 'title', and 'entity_name'
    """
    configs = {
        "dlcd": {
            "path": "content/state/meetings",
            "filename": "{date}-dlcd.md",
            "title": "DLCD Meeting - {formatted_date}",
            "entity_name": "DLCD",
            "meeting_type": "dlcd"
        },
        "tualatin": {
            "path": "content/cities/tualatin/meetings",
            "filename": "{date}-planning-commission.md",
            "title": "Tualatin Planning Commission Meeting - {formatted_date}",
            "entity_name": "Tualatin Planning Commission",
            "meeting_type": "planning-commission"
        }
    }
    return configs.get(entity)


def create_meeting_document(date, entity, youtube_url, transcript_path):
    """
    Create a Hugo markdown document for a meeting.

    Args:
        date: Meeting date in YYYY-MM-DD format
        entity: Entity identifier (dlcd, tualatin, etc.)
        youtube_url: YouTube video URL
        transcript_path: Path to transcript file

    Returns:
        Path to created document
    """
    # Get entity configuration
    config = get_entity_config(entity)
    if not config:
        print(f"Error: Unknown entity '{entity}'", file=sys.stderr)
        sys.exit(1)

    # Read transcript
    transcript_path = Path(transcript_path)
    if not transcript_path.exists():
        print(f"Error: Transcript file not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    with open(transcript_path, 'r', encoding='utf-8') as f:
        transcript_content = f.read()

    # Strip the "# Meeting Transcript\n\n" header if present
    if transcript_content.startswith("# Meeting Transcript\n\n"):
        transcript_content = transcript_content[len("# Meeting Transcript\n\n"):]

    # Format date for title
    formatted_date = format_date_for_title(date)

    # Construct output path
    content_path = Path(config["path"])
    content_path.mkdir(parents=True, exist_ok=True)

    filename = config["filename"].format(date=date)
    output_path = content_path / filename

    # Check if file already exists
    if output_path.exists():
        print(f"Warning: Document already exists at {output_path}")
        response = input("Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Aborting.")
            sys.exit(0)

    # Generate front matter
    title = config["title"].format(formatted_date=formatted_date)

    # Create document content
    content = f"""+++
title = '{title}'
date = '{date}'
youtube_url = '{youtube_url}'
meeting_type = '{config["meeting_type"]}'
entity = '{config["entity_name"]}'
+++

## Summary

*This section requires manual curation. Add a brief summary of the meeting, key decisions, and action items.*

## Key Topics

*This section requires manual curation. List the main topics discussed with internal links to relevant legislation, people, and cities.*

## Full Transcript

{transcript_content}
"""

    # Write document
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\nMeeting document created: {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Create Hugo markdown documents for meeting transcripts"
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
    parser.add_argument(
        "--youtube-url",
        required=True,
        help="YouTube video URL"
    )
    parser.add_argument(
        "--transcript",
        required=True,
        help="Path to transcript file"
    )

    args = parser.parse_args()

    # Validate date format
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        print("Error: Date must be in YYYY-MM-DD format", file=sys.stderr)
        sys.exit(1)

    output_path = create_meeting_document(
        args.date,
        args.entity,
        args.youtube_url,
        args.transcript
    )

    print(f"\nNext steps:")
    print(f"1. Review and edit the document at {output_path}")
    print(f"2. Add a summary and key topics")
    print(f"3. Add internal links to related legislation, people, and cities")
    print(f"4. Run 'hugo server' to preview")


if __name__ == "__main__":
    main()
