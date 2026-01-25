#!/bin/bash
#
# Process a meeting: download, transcribe, and create documentation.
#
# This orchestrator script runs all three processing steps in sequence
# with proper error handling and optional cleanup.

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
CLEANUP=false

# Function to print usage
usage() {
    cat << EOF
Usage: $0 --url <youtube-url> --date <YYYY-MM-DD> --entity <entity> [--cleanup]

Process a meeting video: download, transcribe, and create documentation.

Required arguments:
  --url         YouTube video URL
  --date        Meeting date in YYYY-MM-DD format
  --entity      Entity identifier (dlcd or tualatin)

Optional arguments:
  --cleanup     Delete video file after successful processing
  --model       Whisper model size (tiny, base, small, medium, large)
                Default: medium
  -h, --help    Show this help message

Example:
  $0 --url "https://www.youtube.com/watch?v=abc123" \\
     --date "2024-12-05" \\
     --entity "dlcd" \\
     --cleanup
EOF
    exit 1
}

# Parse arguments
YOUTUBE_URL=""
DATE=""
ENTITY=""
MODEL="medium"

while [[ $# -gt 0 ]]; do
    case $1 in
        --url)
            YOUTUBE_URL="$2"
            shift 2
            ;;
        --date)
            DATE="$2"
            shift 2
            ;;
        --entity)
            ENTITY="$2"
            shift 2
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo -e "${RED}Error: Unknown argument: $1${NC}"
            usage
            ;;
    esac
done

# Validate required arguments
if [[ -z "$YOUTUBE_URL" || -z "$DATE" || -z "$ENTITY" ]]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    usage
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Use virtual environment Python if available
if [ -f "$PROJECT_DIR/venv/bin/python3" ]; then
    PYTHON="$PROJECT_DIR/venv/bin/python3"
else
    PYTHON="python3"
fi

# Construct file paths
VIDEO_PATH="/tmp/oregon-housing-meetings/${DATE}-${ENTITY}.mp4"
TRANSCRIPT_PATH="/tmp/oregon-housing-meetings/${DATE}-${ENTITY}-transcript.txt"

echo -e "${GREEN}=== Processing Meeting ===${NC}"
echo "URL: $YOUTUBE_URL"
echo "Date: $DATE"
echo "Entity: $ENTITY"
echo "Model: $MODEL"
echo "Cleanup: $CLEANUP"
echo ""

# Step 1: Download
echo -e "${GREEN}Step 1/3: Downloading video...${NC}"
if ! "$PYTHON" "$SCRIPT_DIR/download_meeting.py" \
    --url "$YOUTUBE_URL" \
    --date "$DATE" \
    --entity "$ENTITY"; then
    echo -e "${RED}Error: Download failed${NC}"
    exit 1
fi
echo ""

# Step 2: Transcribe
echo -e "${GREEN}Step 2/3: Transcribing video...${NC}"
if ! "$PYTHON" "$SCRIPT_DIR/transcribe_meeting.py" \
    --video "$VIDEO_PATH" \
    --model "$MODEL"; then
    echo -e "${RED}Error: Transcription failed${NC}"
    exit 1
fi
echo ""

# Step 3: Create document
echo -e "${GREEN}Step 3/3: Creating meeting document...${NC}"
if ! "$PYTHON" "$SCRIPT_DIR/create_meeting_doc.py" \
    --date "$DATE" \
    --entity "$ENTITY" \
    --youtube-url "$YOUTUBE_URL" \
    --transcript "$TRANSCRIPT_PATH"; then
    echo -e "${RED}Error: Document creation failed${NC}"
    exit 1
fi
echo ""

# Cleanup if requested
if [ "$CLEANUP" = true ]; then
    echo -e "${YELLOW}Cleaning up video file...${NC}"
    rm -f "$VIDEO_PATH"
    echo "Video file deleted: $VIDEO_PATH"
    echo ""
fi

echo -e "${GREEN}=== Processing Complete ===${NC}"
echo "Video: $VIDEO_PATH"
echo "Transcript: $TRANSCRIPT_PATH"
echo ""
echo "Next steps:"
echo "1. Review and edit the generated meeting document"
echo "2. Add summary and key topics"
echo "3. Add internal links to related content"
echo "4. Run 'hugo server' to preview"
