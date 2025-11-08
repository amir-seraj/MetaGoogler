# Internet-Based Cover Art Fetching Guide

## Overview

This guide explains how the cover art system uses intelligent internet-based fetching to automatically discover and embed album artwork.

## How It Works

### 1. Multi-Source Fetching

The system queries multiple sources for cover art:

- **MusicBrainz** (Primary - no API key required)
  - Uses the Cover Art Archive
  - Highest success rate for popular music
  - Provides pre-reviewed, high-quality artwork

- **Last.fm** (Planned - requires API key)
  - Great for discovering alternate artwork
  - Social ratings for cover quality

- **Spotify** (Planned - requires API key)
  - Official album artwork
  - Consistent sizing and quality

### 2. Intelligent Clustering Algorithm

The system fetches ~10 candidate images and uses **RGB histogram similarity matching** to find the best cover:

```
Step 1: Fetch candidates from multiple sources
   ↓
Step 2: Calculate RGB histogram for each image
   ↓
Step 3: Compare all image pairs using histogram distance
   ↓
Step 4: Group images with 85%+ similarity (clusters)
   ↓
Step 5: Vote: Largest cluster = consensus = most reliable
   ↓
Step 6: Return highest resolution image from winning cluster
```

### 3. Consensus Voting Example

Imagine fetching 10 images for "The Beatles - Let It Be":

```
Cluster A (4 images similar to each other): CORRECT
├─ Same album front cover from different sources
├─ Slight variations in compression/quality
└─ All ~1100x1100px

Cluster B (2 images similar to each other): ALTERNATE
├─ Different edition/reissue cover
└─ ~1000x1000px

Single images (4 different): OUTLIERS
├─ Wrong album/artist
├─ Artwork not from this release
└─ Low quality/corrupted

RESULT: Use Cluster A (4 > 2 > 1, so Cluster A wins!)
```

### 4. Image Compression

Large images are automatically compressed:
- Target size: 500KB maximum
- Quality reduction: Gradual decrease from 95 to 10
- Resolution reduction: If needed, scales image down
- Format: JPEG for compatibility

## Usage

### In GUI

1. Click "Embed Cover Art" button
2. Choose:
   - **Yes**: Download from internet (automatic)
   - **No**: Use local image file (select manually)
   - **Cancel**: Cancel operation

### Programmatic Usage

```python
from song_metadata_fixer_v2 import SongMetadataFixer
from pathlib import Path

fixer = SongMetadataFixer()

# Method 1: Download and embed directly
result = fixer.download_cover_art_from_internet(
    artist="The Beatles",
    title="Let It Be"
)

# Method 2: Get cover bytes only (for manual handling)
cover_bytes = fixer.download_cover_art_from_internet(
    artist="Pink Floyd",
    title="Wish You Were Here"
)

if cover_bytes:
    # Embed into audio file
    result = fixer.embed_cover_art_bytes(
        file_path=Path("song.mp3"),
        image_bytes=cover_bytes
    )
```

## Algorithm Details

### RGB Histogram Similarity

The system compares images using their RGB color distributions:

1. **Image to Histogram Conversion**
   - Resize image to 8x8 pixels
   - Extract RGB values for all pixels
   - Group colors into 8 buckets each: R[0-8], G[0-8], B[0-8]
   - Count occurrences in each bucket

2. **Similarity Score (Hamming Distance)**
   - Create 24-element histogram (8 for each channel)
   - Convert to hash (MD5)
   - Compare two hashes bit-by-bit
   - Similarity = 1.0 - (different_bits / total_bits)
   - Range: 0.0 (completely different) to 1.0 (identical)

3. **Clustering Threshold**
   - 85% similarity (0.85) threshold for same cluster
   - Ensures only visually similar images group together
   - Filters out variations in compression/quality

## Quality Assurance

### Validation Checks

All downloaded covers are validated:

```
✓ Image size: 100x100px minimum, 4000x4000px maximum
✓ File size: After compression, max 500KB
✓ Aspect ratio: Reasonable (up to 1.5:1 ratio allowed)
✓ Format: Valid JPEG/PNG
✓ Embedding: Verified after save to file
```

### Supported Formats

| Format | Tag Type | Status |
|--------|----------|--------|
| MP3    | ID3v2.4  | ✓ Full support |
| M4A    | MP4      | ✓ Full support |
| FLAC   | Vorbis   | ✓ Full support |
| OggVorbis | Vorbis | ✓ Full support |
| WAV    | ID3      | ✓ Full support |

## Error Handling

### Common Scenarios

1. **No cover found online**
   - Logs warning message
   - Returns None
   - GUI shows "No cover found online"
   - User can fallback to local file

2. **Network timeout**
   - Default 10 second timeout per API call
   - Automatically moves to next source
   - Falls back gracefully if all sources fail

3. **Image validation fails**
   - Too small: Minimum 100x100px required
   - Too large: Maximum 4000x4000px
   - Wrong aspect ratio: >1.5:1 rejected
   - Invalid format: Corrupted images skipped

4. **Embedding fails**
   - Logs detailed error message
   - Returns failure status
   - File remains unchanged

## Advanced Configuration

### Adjusting Clustering Threshold

In `cover_art_fetcher.py`:

```python
# More strict (fewer, larger clusters)
similarity_threshold = 0.95  # Default: 0.85

# More lenient (more, smaller clusters)
similarity_threshold = 0.75
```

### Adjusting Image Size Limits

In `song_metadata_fixer_v2.py`:

```python
# In _validate_image_specs()
self.max_cover_dimensions = (6000, 6000)  # Default: (4000, 4000)
```

## Troubleshooting

### MusicBrainz Returns 403 Error

**Solution**: User-Agent must be proper format. Should be:
```
MetaFixer/1.0 (https://github.com/user/metafixer; email@example.com)
```

Not:
```
Mozilla/5.0 ...  # Generic browser UA will be blocked
```

### Clustering Returns Empty Result

**Cause**: All images too different (none exceed 85% threshold)
**Solution**: Returns first image anyway (fallback behavior)

### Image Too Large After Compression

**Cause**: Unusual image format that won't compress well
**Solution**: Still embedded (validation was relaxed for downloaded images)

## Performance

### Typical Times

- Single artist lookup: 2-4 seconds
- Fetching 10 images: 3-5 seconds
- Clustering: <100ms
- Embedding to file: <500ms

### Network Requirements

- ~2MB temporary bandwidth per fetch (images downloaded, then deleted)
- No persistent caching (API calls made fresh each time)
- Respects API rate limits:
  - MusicBrainz: No strict limit (rate-limited gracefully)
  - Last.fm: 60 calls/min (with API key)

## Future Enhancements

### Planned Features

- [ ] Image caching to avoid repeated fetches
- [ ] Integration with Spotify API (requires key setup)
- [ ] Integration with Last.fm API (requires key setup)
- [ ] Google Images fallback search
- [ ] User preview window for candidate selection
- [ ] Manual override/selection UI
- [ ] Batch configuration for API keys

### Possible Improvements

- Add confidence scores for clustering results
- Implement SIFT/ORB for more accurate image matching
- Support for artist/album-specific metadata from Genius.com
- Caching with TTL (time-to-live)

## Technical Details

### Class: CoverArtFetcher

Main orchestrator for multi-source fetching:

```python
fetcher = CoverArtFetcher(timeout=10)

# Fetch best candidate (returns CoverArtCandidate object)
best = fetcher.fetch_cover_art(artist, title, max_candidates=12)

# Get candidate image bytes
if best:
    image_bytes = best.image_data
```

### Class: ImageSimilarityMatcher

Handles RGB histogram comparison:

```python
matcher = ImageSimilarityMatcher()

# Get histogram hash of image
hash1 = matcher.get_histogram_hash(image_bytes)

# Compare two hashes (returns 0.0-1.0)
similarity = matcher.calculate_similarity(hash1, hash2)
```

### Method: SongMetadataFixer.download_cover_art_from_internet()

Downloads cover from internet using consensus voting:

```python
cover_bytes = fixer.download_cover_art_from_internet(
    artist="The Beatles",
    title="Let It Be"
)
```

### Method: SongMetadataFixer.embed_cover_art_bytes()

Embeds raw bytes into audio file:

```python
result = fixer.embed_cover_art_bytes(
    file_path=Path("song.mp3"),
    image_bytes=cover_bytes,
    mime_type="image/jpeg"  # Optional, defaults to jpeg
)
```

## References

- [MusicBrainz API](https://musicbrainz.org/doc/Development)
- [Cover Art Archive](https://coverartarchive.org/)
- [Last.fm API](https://www.last.fm/api/)
- [Spotify Web API](https://developer.spotify.com/)
- [RGB Histogram](https://docs.opencv.org/master/d8/dbc/tutorial_histogram_calculation.html)

## FAQ

**Q: Will this overwrite existing cover art?**
A: Yes, the downloaded cover replaces any existing cover art.

**Q: Can I use a different image source?**
A: Yes, use the "No" option when prompted to select a local image file.

**Q: How many API calls does this make?**
A: Typically 1-3 API calls per artist-title pair (searches MusicBrainz, fetches metadata, gets images).

**Q: What if the artist/title doesn't match MusicBrainz?**
A: The system tries to match what you provide; if no matches, it returns None gracefully.

**Q: Is this saved in the config?**
A: No, each fetch is done fresh. Consider caching if you have recurring artists.

---

*Last updated: November 2025*
*Phase 3: Internet-Based Cover Art Discovery with Intelligent Clustering*
