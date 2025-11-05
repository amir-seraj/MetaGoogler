# Song Metadata Fixer

A powerful command-line tool to fix and organize song metadata (ID3 tags) for audio files.

## Features

- **Fix Metadata**: Clean and standardize metadata for single files or entire directories
- **View Metadata**: Display current metadata without modifying files
- **Batch Processing**: Fix multiple files at once
- **Recursive Support**: Process subdirectories automatically
- **Multiple Formats**: Support for MP3, M4A, FLAC, OGG, and WMA files
- **Verbose Mode**: Detailed logging of operations

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Fix Metadata for a Single File
```bash
python song_metadata_fixer.py fix song.mp3
```

### Fix All Songs in a Directory
```bash
python song_metadata_fixer.py fix ./music
```

### Recursively Fix Songs in Subdirectories
```bash
python song_metadata_fixer.py fix ./music -r
```

### View Metadata Without Modifying
```bash
python song_metadata_fixer.py view song.mp3
```

### Enable Verbose Output
```bash
python song_metadata_fixer.py fix ./music -v
```

## Supported Audio Formats
- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)
- OGG Vorbis (.ogg)
- WMA (.wma)

## What Gets Fixed

The tool cleans up:
- Extra whitespace in all metadata fields
- Standard ID3 tags (title, artist, album, date, genre, track number)
- Consistency across all files

## Dependencies

- **mutagen**: Python library for reading and writing audio metadata

## Future Enhancements

- Interactive metadata editor
- Custom metadata rules/templates
- Album art extraction and embedding
- Automatic metadata fetching from online databases
- Batch rename files based on metadata
- Metadata validation and reporting

## License

MIT

## Contributing

Feel free to fork this project and submit pull requests!
