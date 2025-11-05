# Song Metadata Fixer

A powerful command-line tool to fix, validate, and organize song metadata (ID3 tags) for audio files. **Perfect for audiophiles managing music across multiple devices** (DAP, phone, car stereo, desktop players, etc.).

## Features

- **🔧 Fix Metadata**: Clean and standardize metadata for single files or entire directories
- **✓ Validate Quality**: Check metadata completeness before syncing to devices
- **📁 Organize Library**: Auto-organize files into Artist/Album folder structure
- **👀 View Metadata**: Display current metadata with validation status
- **🔄 Batch Processing**: Fix multiple files at once
- **🌳 Recursive Support**: Process subdirectories automatically
- **🎵 Multiple Formats**: Support for MP3, M4A, FLAC, OGG, and WMA files
- **📊 Detailed Reporting**: Save validation reports as JSON

## The Audiophile Workflow

```
Downloaded Music
    ↓
[Fix] - Clean metadata and formatting
    ↓
[Validate] - Check quality before sync
    ↓
[Organize] - Sort into Artist/Album structure
    ↓
Sync to: DAP | Phone | Car Stereo | Desktop Player
```

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

### 1. Fix Metadata for Downloaded Music
Fix all metadata issues in your downloads folder:
```bash
# Single file
python song_metadata_fixer.py fix song.mp3

# All songs in directory
python song_metadata_fixer.py fix ./downloads

# Recursively fix all songs in subdirectories
python song_metadata_fixer.py fix ./downloads -r

# Verbose mode for detailed logging
python song_metadata_fixer.py fix ./downloads -r -v
```

### 2. Validate Metadata Quality
Before syncing to your device, validate that all metadata is complete:
```bash
# Quick validation
python song_metadata_fixer.py validate ./music

# Save detailed report
python song_metadata_fixer.py validate ./music --report
```

**Validation checks for:**
- ✓ Title, Artist, Album present
- ✓ Genre tagged
- ✓ Year/Date filled
- ✓ Proper formatting

### 3. Organize Music Library
Auto-organize files into a clean Artist/Album structure for easy navigation:
```bash
python song_metadata_fixer.py organize ./downloads -o ~/Music/Organized
```

**Results in structure:**
```
Organized/
├── Artist Name/
│   ├── Album 1/
│   │   ├── Track 1.mp3
│   │   ├── Track 2.mp3
│   │   └── Track 3.mp3
│   └── Album 2/
│       └── Track 1.mp3
└── Another Artist/
    └── Album/
        └── Track.mp3
```

### 4. View Metadata Details
Display current metadata with validation status:
```bash
python song_metadata_fixer.py view song.mp3
```

Output shows:
- Title, Artist, Album
- Genre, Date, Track Number
- ✓ Validation status with issues found

## Supported Audio Formats
- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)
- OGG Vorbis (.ogg)
- WMA (.wma)

## What Gets Fixed

The tool standardizes:
- Extra whitespace in metadata fields
- ID3 tag consistency
- Formatting across all files
- File organization by metadata

## Use Cases

### For DAP (Digital Audio Player) Users
```bash
# Before syncing to Astell&Kern, Sony Walkman, etc.
python song_metadata_fixer.py fix ~/downloads -r
python song_metadata_fixer.py validate ~/downloads --report
```

### For Car Stereo Compatibility
```bash
# Ensure all metadata is properly formatted
python song_metadata_fixer.py fix ~/music -r -v
```

### For Phone Syncing
```bash
# Organize and validate before transfer
python song_metadata_fixer.py organize ~/downloads -o ~/Music/ToSync
python song_metadata_fixer.py validate ~/Music/ToSync
```

## Device-Specific Tips

| Device | Best Practice |
|--------|---------------|
| **DAP** | Fix → Validate → Check album art → Organize |
| **Phone** | Fix → Organize → Sync via iTunes/MTP |
| **Car Stereo** | Validate all required fields filled |
| **Desktop** | Use for library management & tagging |

## Future Enhancements

- 🎨 Album art extraction and embedding
- 🔍 Automatic metadata fetching from online databases (MusicBrainz, Discogs)
- 🏷️ Custom tagging rules and templates
- 📊 Advanced metadata comparison and deduplication
- 🔗 Playlist generation from metadata
- ⚙️ Device-specific metadata profiles

## Dependencies

- **mutagen**: Python library for reading and writing audio metadata

## License

MIT

## Contributing

Feel free to fork this project and submit pull requests!
