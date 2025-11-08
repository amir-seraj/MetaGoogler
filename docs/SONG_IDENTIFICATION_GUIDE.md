# Song Identification Feature Guide

## Overview

The Song Identification feature automatically identifies songs and fills in missing metadata using free online APIs and audio analysis techniques. This is perfect for managing music files that lack proper metadata.

## How It Works

### Identification Methods

The system attempts identification through multiple methods in order of reliability:

#### 1. **MusicBrainz Acoustic Fingerprinting** (Most Reliable)
- Uses audio fingerprinting via AcoustID service
- Requires: `Chromaprint` library (optional)
- Coverage: Millions of tracks in MusicBrainz database
- Speed: Fast lookup after fingerprint generation
- Accuracy: Very high for commercial releases

#### 2. **ACRCloud API** (Recommended)
- Shazam-like technology
- Free tier: 1,000 requests/month
- Coverage: Excellent for popular music
- Accuracy: Very high
- Setup: Requires free account at acr cloud.com

#### 3. **Spotify Search API** (Good for Popular Music)
- Searches Spotify's vast catalog
- Free tier: Unlimited (no authentication required for basic search)
- Coverage: Excellent for modern music
- Accuracy: High when partial metadata available
- Speed: Very fast

### Audio Analysis Process

When librosa is available, the system extracts:

```
Audio File (minimum 15 seconds needed)
    ↓
Load first 15 seconds at 22.05 kHz
    ↓
Extract features:
├─ Chromagram (color of the music)
├─ Spectral Centroid (brightness)
└─ MFCCs (vocal/instrument characteristics)
    ↓
Create fingerprint hash from features
    ↓
Query databases with fingerprint
```

## Usage

### Via GUI

1. Click **"Identify Songs"** button
2. Choose:
   - **Single file**: Select a file from list, click button
   - **All files**: Click button without selection
3. Wait for identification to complete
4. Review log for results:
   - ✓ = Successfully identified & metadata filled
   - → = No identification needed (metadata complete)
   - ✗ = Identification failed

### Via Command Line

```python
from song_metadata_fixer_v2 import SongMetadataFixer
from pathlib import Path

fixer = SongMetadataFixer()

# Identify and fill missing metadata for one file
result = fixer.identify_and_fill_metadata(
    file_path=Path("unknown_song.mp3"),
    overwrite_existing=False  # Only fill empty fields
)

if result.success:
    print(f"✓ {result.message}")
else:
    print(f"✗ {result.message}")

# Get identification only (don't write to file)
metadata = fixer.identify_song(Path("unknown_song.mp3"))

if metadata:
    print(f"Song: {metadata['artist']} - {metadata['title']}")
    print(f"Album: {metadata['album']}")
    print(f"Confidence: {metadata['confidence']:.0%}")
```

### Batch Processing

```python
# Identify all songs in a folder
from pathlib import Path
from song_metadata_fixer_v2 import SongMetadataFixer

fixer = SongMetadataFixer()

# Get all audio files
audio_files = list(Path("./music").glob("**/*.mp3"))
audio_files += list(Path("./music").glob("**/*.m4a"))

# Process each file
for audio_file in audio_files:
    result = fixer.identify_and_fill_metadata(audio_file)
    print(f"{audio_file.name}: {'✓' if result.success else '✗'}")
```

## Identification Sources

### MusicBrainz + Cover Art Archive

**Source**: https://musicbrainz.org

- **Coverage**: Millions of tracks from all genres
- **Accuracy**: Very high for commercial releases
- **Cost**: Free
- **API Key**: Not required
- **Rate Limit**: Reasonable (recommend user agent)
- **Best For**: All music types

### ACRCloud

**Source**: https://www.acrcloud.com

- **Coverage**: Excellent, especially for popular music
- **Accuracy**: Very high (Shazam technology)
- **Cost**: Free tier with 1,000 requests/month
- **API Key**: Required (sign up free)
- **Speed**: Very fast
- **Best For**: Modern popular music

### Spotify Web API

**Source**: https://developer.spotify.com

- **Coverage**: Excellent for modern music
- **Accuracy**: High when title/artist partial match available
- **Cost**: Free (basic search)
- **API Key**: Not required for search
- **Rate Limit**: Generous
- **Best For**: Quick searches with partial metadata

## Audio Requirements

### Minimum Audio Length

- **Required**: Minimum 15 seconds of audio
- **Recommended**: 30+ seconds for better fingerprinting
- **Best**: Full track (most reliable results)

### Supported Formats

| Format | Sample Rate | Status |
|--------|------------|--------|
| MP3    | Any        | ✓ Full support |
| M4A    | Any        | ✓ Full support |
| FLAC   | Any        | ✓ Full support |
| WAV    | Any        | ✓ Full support |
| OggVorbis | Any    | ✓ Full support |

## Installation & Setup

### Basic Installation

```bash
# Install core dependencies
pip install requests mutagen

# Optional: For better audio analysis
pip install librosa
```

### Advanced Setup (with all APIs)

```bash
# Install everything
pip install requests mutagen librosa librosa numpy scipy

# Optional: For ACRCloud integration
# 1. Sign up free at: https://www.acrcloud.com/
# 2. Get API credentials
# 3. Add to config.json:
```

**config.json**:
```json
{
  "acrcloud": {
    "enabled": false,
    "access_key": "YOUR_ACCESS_KEY",
    "access_secret": "YOUR_ACCESS_SECRET"
  }
}
```

## Metadata Matching

### What Gets Matched

When identification succeeds, the following metadata fields are populated:

| Field | Source | Notes |
|-------|--------|-------|
| title | Identified | Song name |
| artist | Identified | Primary artist |
| album | Identified | Album name |
| isrc | MusicBrainz | International Standard Recording Code |
| duration | Various | Song duration in seconds |
| source | System | Which API found it |

### Merge Strategy

**Default Behavior (overwrite_existing=False)**:
- Preserves existing metadata
- Only fills **empty** fields
- Skips "Unknown" values
- Safe for files with partial metadata

**Overwrite Mode (overwrite_existing=True)**:
- Replaces all metadata with identified data
- Use cautiously
- Useful for completely empty files

## Confidence Scores

Each identification includes a confidence score (0.0-1.0):

| Score | Meaning | Action |
|-------|---------|--------|
| 0.95-1.0 | Certain match | Use directly |
| 0.85-0.95 | Very likely | Use with review |
| 0.70-0.85 | Probably correct | Manual review recommended |
| <0.70 | Uncertain | Do not use automatically |

## Error Handling

### Common Issues & Solutions

**"Librosa not available"**
- **Cause**: Optional audio analysis library not installed
- **Impact**: Uses simpler fingerprinting fallback
- **Solution**: `pip install librosa` (optional but recommended)

**"Song not found in any database"**
- **Cause**: Obscure track or poor audio quality
- **Solution**: Manually enter metadata or try different methods

**"Partial metadata conflicts"**
- **Cause**: File has some fields filled, some empty
- **Solution**: By default, only empty fields filled (safe mode)

**"Network timeout"**
- **Cause**: API server not responding
- **Solution**: Automatic 10-second timeout, will skip and continue

**"Rate limit exceeded"**
- **Cause**: Too many requests to API
- **Solution**: Wait a bit, try again later, or use different API

## Performance

### Typical Processing Times

| Operation | Time | Notes |
|-----------|------|-------|
| Fingerprint generation | 1-3 sec | First 15 seconds of audio |
| Database lookup | 1-2 sec | Query MusicBrainz/Spotify |
| Metadata write | <500 ms | Write to file |
| **Single file total** | **2-5 sec** | Varies by method |
| **Batch (100 files)** | **3-8 min** | Parallel processing |

## Advanced Configuration

### Custom Fingerprint Duration

```python
from song_identifier import AudioFingerprinter

# Use shorter duration for faster processing
fingerprint = AudioFingerprinter.extract_fingerprint(
    audio_path,
    duration=10.0  # 10 seconds instead of 15
)
```

### Batch with Custom Settings

```python
from song_metadata_fixer_v2 import SongMetadataFixer
from pathlib import Path

fixer = SongMetadataFixer()

# Process with logging
for file in Path("./music").glob("*.mp3"):
    result = fixer.identify_and_fill_metadata(
        file,
        overwrite_existing=False
    )
    
    if result.success:
        print(f"✓ {file.name}")
    else:
        print(f"✗ {file.name}: {result.message}")
```

## Troubleshooting

### Identification Always Fails

1. **Check audio length**:
   - Minimum 15 seconds required
   - Corrupt files won't fingerprint

2. **Verify network**:
   - Test: `ping musicbrainz.org`
   - Check firewall settings

3. **Check logs**:
   - Location: `fixer.log`
   - Search for "identify" errors

4. **Try with librosa**:
   - `pip install librosa`
   - Improves fingerprint accuracy

### Metadata Not Updating

1. **File permissions**:
   - Check write permissions
   - Try: `chmod 644 filename.mp3`

2. **File format**:
   - Not all formats support all tags
   - MP3 (ID3v2.4) most compatible

3. **Metadata conflicts**:
   - Run with `overwrite_existing=True`
   - Be careful with manual edits

### Slow Performance

1. **Reduce batch size**:
   - Process 50 files at a time
   - Leave system resources

2. **Shorter fingerprint**:
   - Use 10 second duration instead of 15
   - Slightly less accurate but faster

3. **Network issues**:
   - Run during off-peak hours
   - Check internet connection

## Integration with Other Features

### With AI Suggestions

Combine identification with AI refinement:

```python
fixer = SongMetadataFixer()

# Step 1: Identify missing metadata
result = fixer.identify_and_fill_metadata(file)

# Step 2: Get AI suggestions for refinement
ai_suggestions = fixer.ai_manager.get_ai_suggestions(
    file.name,
    fixer.get_metadata(file)
)

# Step 3: Apply suggestions if approved by user
```

### With Cover Art Downloading

After identification, get cover art:

```python
# Step 1: Identify song
result = fixer.identify_and_fill_metadata(file)

# Step 2: Get metadata
metadata = fixer.get_metadata(file)

# Step 3: Download cover art
cover_bytes = fixer.download_cover_art_from_internet(
    metadata['artist'],
    metadata['title']
)

# Step 4: Embed cover
fixer.embed_cover_art_bytes(file, cover_bytes)
```

## Future Enhancements

### Planned Features

- [ ] Fingerprint caching (avoid repeated analysis)
- [ ] Genius.com lyrics integration
- [ ] YouTube Music API support
- [ ] Local fingerprint database
- [ ] Manual correction UI
- [ ] Batch confidence filtering

### Possible Improvements

- SIFT/ORB visual matching for album art
- Machine learning confidence scoring
- Distributed batch processing
- Advanced audio preprocessing
- Genre/style matching

## FAQ

**Q: Do I need to install Librosa?**
A: No, it's optional. Without it, uses simpler fingerprinting (still works).

**Q: What if a song has no metadata at all?**
A: All three methods are attempted. Most modern songs will be identified.

**Q: How accurate is the identification?**
A: Generally 85-95% for commercial releases, lower for obscure/remix tracks.

**Q: Can I identify songs offline?**
A: No, all methods require internet connection to query databases.

**Q: Will this overwrite my existing metadata?**
A: By default, no - only fills empty fields. Use `overwrite_existing=True` to replace.

**Q: How many songs can I identify per day?**
A: Unlimited with MusicBrainz and Spotify. ACRCloud free tier: 1,000/month.

**Q: Does it work with non-English songs?**
A: Yes, all methods support international music.

---

*Song Identification Feature Guide*  
*Version: 1.0*  
*Last Updated: November 2025*
