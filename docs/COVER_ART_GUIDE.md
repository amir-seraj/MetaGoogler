# 🎨 Cover Art Management Guide

## Overview

The MetaDataFixer application handles cover art in **two distinct ways**:

1. **Manual Embedding** - Users select a cover image file and embed it into ALL audio files
2. **Verification & Detection** - Checks if files already have embedded cover art

---

## Where Cover Art Comes From

### **Current Sources:**

#### 1. **User-Selected File (Manual Embedding)**
- **How it works:**
  - User clicks "Embed Cover Art" button in GUI
  - File dialog opens: `Select Cover Image`
  - User browses and selects: `*.jpg`, `*.jpeg`, or `*.png`
  - Selected image is embedded into all audio files in the folder

- **File path:** `/home/amir/Documents/Meta/music/`
- **GUI trigger:** Button "Embed Cover Art" (light yellow)
- **Code:** `app_gui.py` lines 368-410

#### 2. **Existing Embedded Art (Detection)**
- **How it works:**
  - Method: `has_cover_art(file_path)`
  - Checks if audio file already contains embedded art
  - Supported formats:
    * MP3: ID3 APIC frames (`APIC:Cover`, `APIC:Cover `, etc.)
    * M4A/MP4: `covr` atoms
    * FLAC: Picture metadata blocks
    * OGG: Vorbis comments

- **Detection code:** `song_metadata_fixer_v2.py` lines 391-422

---

## Current Audio Files

### Files in `/home/amir/Documents/Meta/music/`:

```
01 - OsamaSon - popstar.mp3          (4.3 MB) - HAS EXISTING COVER ART ✓
01. Tekir - uyudun mu_.m4a           (5.0 MB) - HAS EXISTING COVER ART ✓
10 - Young Thug - Danny Glover.mp3   (8.8 MB)
1_1 - I Love It - Kanye West.mp3     (5.0 MB)
A.A. Williams - Nights In White.mp3 (11  MB)
Aptune - Mage Mishe (1).mp3          (7.3 MB)
audio.m4a                             (3.6 MB)
CASHIN_AHT_Prod. [2190261591].mp3    (3.7 MB)
Future-Colossal.mp3                   (7.1 MB)
Nobody.m4a                            (2.1 MB)
Radiohead_-_Backdrifts_Live.mp3      (16  MB)
```

---

## How to Replace/Update Cover Art

### **Method 1: Using the GUI (Recommended for Users)**

```
1. Open MetaDataFixer GUI
2. Click "Browse Folder"
3. Select: /home/amir/Documents/Meta/music/
4. Click "Embed Cover Art" button (light yellow)
5. Select your new cover image (JPG or PNG)
6. Covers are embedded into ALL files in the folder
7. Check activity log for results
```

### **Method 2: Programmatically (For Developers)**

```python
from song_metadata_fixer_v2 import SongMetadataFixer
from pathlib import Path

fixer = SongMetadataFixer()

# Single file
result = fixer.embed_cover_art(
    Path('music/song.mp3'),
    Path('new_cover.jpg')
)

# Multiple files
for file in Path('music').glob('*.mp3'):
    result = fixer.embed_cover_art(file, Path('cover.jpg'))
    if result.success:
        print(f"✓ Updated: {file.name}")
```

### **Method 3: CLI (Command Line)**

```bash
# Fix metadata and validate covers
python song_metadata_fixer_v2.py music/ -v

# The -v flag validates existing cover art
```

---

## Cover Art Specifications

### **Accepted Formats:**
- ✅ JPEG (`.jpg`, `.jpeg`)
- ✅ PNG (`.png`)
- ❌ BMP, GIF, WEBP (not recommended)

### **Recommended Dimensions:**
- **Ideal:** 300x300 pixels (square)
- **Minimum:** 100x100 pixels
- **Maximum:** 3000x3000 pixels
- **Aspect ratio:** 1:1 (square preferred)

### **File Size:**
- **Maximum:** Configurable (default 500 KB)
- **Current limit:** See `config.json` → `max_cover_size_kb`

### **Quality:**
- Use high-quality album artwork (official releases)
- Avoid low-resolution or distorted images
- PNG for transparency, JPEG for smaller files

---

## Validation & Verification

### **Check if file has cover art:**

```python
fixer = SongMetadataFixer()
has_art = fixer.has_cover_art(Path('song.mp3'))
print(f"Has cover: {has_art}")
```

### **Validate cover art quality:**

```python
is_valid, issues = fixer.validate_cover_art(Path('song.mp3'))
if is_valid:
    print("✓ Cover art looks good")
else:
    for issue in issues:
        print(f"⚠️  {issue}")
    # Possible issues:
    # - Too large (> 500KB)
    # - Too small (< 100x100px)
    # - Wrong aspect ratio
    # - Invalid format
```

---

## Current Status of Test Files

### MP3 Files:
- ✅ **01 - OsamaSon - popstar.mp3** - Has cover art (verified embedded)
- ❓ **10 - Young Thug - Danny Glover.mp3** - Check status
- ❓ **1_1 - I Love It - Kanye West.mp3** - Check status
- ❓ **A.A. Williams - Nights In White.mp3** - Check status
- ❓ **Aptune - Mage Mishe (1).mp3** - Check status
- ⚠️  **Future-Colossal.mp3** - Legacy ID3v2.0 (may have issues)
- ❓ **Radiohead_-_Backdrifts_Live.mp3** - Recently updated with AI suggestions

### M4A/MP4 Files:
- ✅ **01. Tekir - uyudun mu_.m4a** - Has cover art (verified embedded)
- ❓ **audio.m4a** - Check status
- ❓ **Nobody.m4a** - Check status

---

## Workflow to Update All Covers

### **Step 1: Prepare Cover Image**
```bash
# Create or download a cover image
# Place it in accessible location
# Example: ~/cover.jpg
```

### **Step 2: Run GUI**
```bash
python app_gui.py
```

### **Step 3: Select Folder**
- Browse to: `/home/amir/Documents/Meta/music/`
- Click "Load Folder"

### **Step 4: Embed Cover**
- Click "Embed Cover Art"
- Select: `~/cover.jpg`
- Wait for processing

### **Step 5: Verify**
- Check activity log for ✓ marks
- All files should show: "✓ Cover embedded: filename"

### **Step 6: Validate Quality**
```bash
python -c "
from song_metadata_fixer_v2 import SongMetadataFixer
from pathlib import Path

fixer = SongMetadataFixer()
for f in Path('music').glob('*.mp3'):
    is_valid, issues = fixer.validate_cover_art(f)
    if is_valid:
        print(f'✓ {f.name}')
    else:
        print(f'✗ {f.name}: {issues}')
"
```

---

## Advanced: Custom Cover Per Album

For different covers per album, you need to manually process each album:

```python
from pathlib import Path
from song_metadata_fixer_v2 import SongMetadataFixer

fixer = SongMetadataFixer()

# Album 1 - Eagles
eagles_cover = Path('covers/eagles_album.jpg')
for file in Path('music').glob('*Eagles*'):
    fixer.embed_cover_art(file, eagles_cover)

# Album 2 - Radiohead
radiohead_cover = Path('covers/radiohead_album.jpg')
for file in Path('music').glob('*Radiohead*'):
    fixer.embed_cover_art(file, radiohead_cover)
```

---

## Configuration

### **config.json Settings for Cover Art:**

```json
{
  "cover_art": {
    "enabled": true,
    "formats": ["jpg", "jpeg", "png"],
    "max_size_kb": 500,
    "max_dimensions": [3000, 3000],
    "min_dimensions": [100, 100]
  }
}
```

### **Modify settings:**
```python
from config_manager import ConfigManager

config = ConfigManager()
config.set('cover_art', {
    'max_size_kb': 1000,  # Allow larger covers
    'formats': ['jpg', 'jpeg', 'png', 'webp']
})
config.save()
```

---

## Troubleshooting

### **Issue: "Cover art too large"**
- **Cause:** Image file > 500 KB
- **Solution:** Compress image or increase `max_cover_size_kb` in config

### **Issue: "Cover not square"**
- **Cause:** Image aspect ratio not 1:1
- **Solution:** Crop or resize image to square (e.g., 300x300px)

### **Issue: "Cover too small"**
- **Cause:** Image < 100x100 pixels
- **Solution:** Use higher resolution image

### **Issue: "Format not supported"**
- **Cause:** Using BMP, GIF, WEBP instead of JPG/PNG
- **Solution:** Convert to JPEG or PNG first

### **Issue: Files not reading after embedding**
- **Cause:** Corrupted ID3 tags
- **Solution:** Use `--fix-tags` option to repair

---

## Summary

**Current Cover Art Sources:**
1. ✅ User-selected files (via "Embed Cover Art" button)
2. ✅ Existing embedded art (auto-detected)
3. ❌ Online sources (MusicBrainz API) - Future feature

**To Replace Covers:**
- Use GUI "Embed Cover Art" button → Select image → Apply to all files
- Or: Use `embed_cover_art()` method programmatically

**Files needing covers:** Check with `has_cover_art()` method
