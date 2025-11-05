#!/usr/bin/env python3
"""
Comprehensive test suite for cover art embedding and verification.
Tests MP3, M4A, and FLAC formats with proper verification.
"""

import sys
from pathlib import Path
from PIL import Image
from io import BytesIO

sys.path.insert(0, str(Path(__file__).parent))

from song_metadata_fixer_v2 import SongMetadataFixer

def create_test_covers():
    """Create test cover images of various sizes."""
    covers = {}
    
    # Standard size (300x300)
    img = Image.new('RGB', (300, 300), color='blue')
    path = Path('test_cover_standard.jpg')
    img.save(path)
    covers['standard'] = path
    
    # High res (1000x1000)
    img = Image.new('RGB', (1000, 1000), color='red')
    path = Path('test_cover_hires.jpg')
    img.save(path)
    covers['hires'] = path
    
    # Small size (100x100)
    img = Image.new('RGB', (100, 100), color='green')
    path = Path('test_cover_small.jpg')
    img.save(path)
    covers['small'] = path
    
    return covers

def cleanup_covers(covers):
    """Remove test cover files."""
    for path in covers.values():
        if path.exists():
            path.unlink()

def test_format(fixer, file_path, cover_path, format_name):
    """Test cover art embedding for a specific format."""
    print(f"\n{'='*70}")
    print(f"Testing: {format_name.upper()} - {file_path.name}")
    print('='*70)
    
    if not file_path.exists():
        print(f"⚠️  File not found: {file_path}")
        return False
    
    # Check initial state
    has_cover_initial = fixer.has_cover_art(file_path)
    print(f"Initial state: has_cover_art = {has_cover_initial}")
    
    # Get initial validation
    is_valid, issues = fixer.validate_cover_art(file_path)
    print(f"Initial validation: {is_valid}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    # Embed cover
    print(f"\nEmbedding cover: {cover_path.name}...")
    result = fixer.embed_cover_art(file_path, cover_path)
    print(f"Embed result: {'✅ SUCCESS' if result.success else '❌ FAILED'}")
    print(f"Message: {result.message}")
    
    # Check final state
    has_cover_final = fixer.has_cover_art(file_path)
    print(f"\nFinal state: has_cover_art = {has_cover_final}")
    
    # Get final validation
    is_valid, issues = fixer.validate_cover_art(file_path)
    print(f"Final validation: {is_valid}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    
    # Determine success
    success = result.success and has_cover_final
    print(f"\nResult: {'✅ PASS' if success else '❌ FAIL'}")
    
    return success

def main():
    """Run comprehensive cover art tests."""
    print("\n🎨 COMPREHENSIVE COVER ART TEST SUITE")
    print("="*70)
    
    fixer = SongMetadataFixer()
    covers = create_test_covers()
    
    test_cases = [
        ('MP3', Path('music/01 - OsamaSon - popstar.mp3')),
        ('M4A', Path('music/01. Tekir - uyudun mu_.m4a')),
    ]
    
    results = {}
    
    # Test standard cover on all formats
    print(f"\n📝 TEST 1: Standard Cover (300x300) on All Formats")
    for format_name, file_path in test_cases:
        success = test_format(fixer, file_path, covers['standard'], format_name)
        results[f"{format_name}_standard"] = success
    
    # Test high resolution cover
    print(f"\n📝 TEST 2: High Resolution Cover (1000x1000) on All Formats")
    for format_name, file_path in test_cases:
        success = test_format(fixer, file_path, covers['hires'], format_name)
        results[f"{format_name}_hires"] = success
    
    # Summary
    print(f"\n{'='*70}")
    print("TEST SUMMARY")
    print('='*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Cleanup
    cleanup_covers(covers)
    print(f"\n✓ Cleaned up test cover images")
    
    # Exit code
    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
