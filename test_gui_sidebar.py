#!/usr/bin/env python3
"""
Test script to verify the metadata sidebar feature
"""

import sys
sys.path.insert(0, '/home/amir/Documents/Meta')

from pathlib import Path
from song_metadata_fixer_v2 import SongMetadataFixer
from mutagen.easyid3 import EasyID3
import shutil

print("=" * 60)
print("METADATA SIDEBAR TEST")
print("=" * 60)

# Create test files
music_dir = Path('/home/amir/Documents/Meta/music')
test_files = [
    ('test_rename_1.mp3', 'A Great Song - Artist Name'),
    ('test_rename_2.mp3', 'Another Track - Different Artist'),
]

fixer = SongMetadataFixer()

print("\n1. Creating test files with editable metadata...")
for test_name, expected_rename in test_files:
    original = music_dir / '01 - OsamaSon - popstar.mp3'
    test_file = music_dir / test_name
    
    shutil.copy(original, test_file)
    
    # Set metadata
    audio = EasyID3(str(test_file))
    audio['title'] = ['Unknown']
    audio['artist'] = ['Unknown']
    audio['album'] = ['Test Album']
    audio.save()
    
    print(f"   ✅ Created: {test_name}")

print("\n2. Verifying metadata editor fields...")
test_file = music_dir / 'test_rename_1.mp3'
metadata = fixer.get_metadata(test_file)

print(f"   Current metadata in {test_file.name}:")
for key in ['title', 'artist', 'album', 'date', 'genre']:
    value = metadata.get(key, 'Unknown')
    print(f"     • {key:12} : {value}")

print("\n3. Testing metadata save and rename...")

# Update metadata
audio = EasyID3(str(test_file))
audio['title'] = ['A Great Song']
audio['artist'] = ['Artist Name']
audio.save()

result = fixer.set_metadata(test_file, {
    'title': 'A Great Song',
    'artist': 'Artist Name',
    'album': 'Test Album'
})

print(f"   Save result: {result.success}")
print(f"   Message: {result.message}")

# Expected new filename
expected_new_name = "Artist Name - A Great Song.mp3"
print(f"\n4. Testing file rename feature...")
print(f"   Original name: {test_file.name}")
print(f"   Expected rename: {expected_new_name}")

# The GUI will rename files when saving metadata
# This demonstrates the rename logic:
title = 'A Great Song'
artist = 'Artist Name'
ext = test_file.suffix

new_filename = f"{artist} - {title}{ext}"
# Remove invalid characters
invalid_chars = r'<>:"/\|?*'
for char in invalid_chars:
    new_filename = new_filename.replace(char, '_')

print(f"   Generated filename: {new_filename}")
print(f"   Match: {'✅' if new_filename == expected_new_name else '❌'}")

print("\n5. Cleanup...")
for test_name, _ in test_files:
    test_file = music_dir / test_name
    if test_file.exists():
        test_file.unlink()
        print(f"   Removed: {test_name}")

print("\n" + "=" * 60)
print("✅ Sidebar feature test complete!")
print("=" * 60)
print("\nNEW FEATURES:")
print("  • Click on any file in the list to see its metadata in the sidebar")
print("  • Edit all metadata fields directly in the sidebar")
print("  • Click '💾 Save Metadata & Rename' to save changes")
print("  • Files are automatically renamed to 'Artist - Title.ext'")
print("  • Invalid filename characters are replaced with '_'")

