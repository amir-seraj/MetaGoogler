#!/usr/bin/env python3
"""
Song Metadata Fixer
A command-line tool to fix and organize song metadata (ID3 tags)
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import argparse

try:
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3
except ImportError:
    print("Error: mutagen library not found. Install with: pip install mutagen")
    sys.exit(1)


class SongMetadataFixer:
    """Fixes and organizes song metadata"""
    
    SUPPORTED_FORMATS = {'.mp3', '.m4a', '.flac', '.ogg', '.wma'}
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.fixed_count = 0
        self.error_count = 0
    
    def log(self, message: str):
        """Print verbose log message"""
        if self.verbose:
            print(f"[INFO] {message}")
    
    def is_supported_format(self, file_path: Path) -> bool:
        """Check if file is a supported audio format"""
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def get_metadata(self, file_path: Path) -> Optional[dict]:
        """Extract metadata from audio file"""
        try:
            audio = EasyID3(str(file_path))
            return {
                'title': audio.get('title', ['Unknown'])[0],
                'artist': audio.get('artist', ['Unknown'])[0],
                'album': audio.get('album', ['Unknown'])[0],
                'date': audio.get('date', ['Unknown'])[0],
                'genre': audio.get('genre', ['Unknown'])[0],
                'tracknumber': audio.get('tracknumber', ['0'])[0],
            }
        except Exception as e:
            print(f"Error reading {file_path.name}: {e}")
            self.error_count += 1
            return None
    
    def set_metadata(self, file_path: Path, metadata: dict) -> bool:
        """Write metadata to audio file"""
        try:
            audio = EasyID3(str(file_path))
            for key, value in metadata.items():
                if value and value != 'Unknown':
                    audio[key] = str(value)
            audio.save()
            self.log(f"Updated: {file_path.name}")
            self.fixed_count += 1
            return True
        except Exception as e:
            print(f"Error writing to {file_path.name}: {e}")
            self.error_count += 1
            return False
    
    def fix_file(self, file_path: Path) -> bool:
        """Fix metadata for a single file"""
        if not self.is_supported_format(file_path):
            return False
        
        metadata = self.get_metadata(file_path)
        if metadata is None:
            return False
        
        # Basic cleaning - remove extra whitespace
        cleaned_metadata = {
            k: v.strip() if isinstance(v, str) else v 
            for k, v in metadata.items()
        }
        
        return self.set_metadata(file_path, cleaned_metadata)
    
    def fix_directory(self, directory: Path, recursive: bool = False) -> None:
        """Fix metadata for all songs in a directory"""
        if not directory.exists():
            print(f"Error: Directory not found: {directory}")
            return
        
        pattern = '**/*' if recursive else '*'
        audio_files = [
            f for f in directory.glob(pattern)
            if f.is_file() and self.is_supported_format(f)
        ]
        
        if not audio_files:
            print("No audio files found.")
            return
        
        print(f"Found {len(audio_files)} audio file(s)")
        for audio_file in audio_files:
            print(f"Processing: {audio_file.relative_to(directory)}")
            self.fix_file(audio_file)
        
        print(f"\n✓ Fixed: {self.fixed_count}")
        print(f"✗ Errors: {self.error_count}")
    
    def print_metadata(self, file_path: Path) -> None:
        """Display metadata for a file"""
        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return
        
        metadata = self.get_metadata(file_path)
        if metadata is None:
            return
        
        print(f"\nMetadata for: {file_path.name}")
        print("-" * 40)
        for key, value in metadata.items():
            print(f"{key.capitalize():15}: {value}")


def main():
    parser = argparse.ArgumentParser(
        description='Fix and organize song metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fix metadata for a single file
  python song_metadata_fixer.py fix song.mp3
  
  # Fix all songs in a directory
  python song_metadata_fixer.py fix ./music
  
  # Recursively fix all songs in subdirectories
  python song_metadata_fixer.py fix ./music -r
  
  # View metadata without modifying
  python song_metadata_fixer.py view song.mp3
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Fix command
    fix_parser = subparsers.add_parser('fix', help='Fix song metadata')
    fix_parser.add_argument('path', type=Path, help='File or directory path')
    fix_parser.add_argument('-r', '--recursive', action='store_true',
                           help='Process subdirectories recursively')
    fix_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Verbose output')
    
    # View command
    view_parser = subparsers.add_parser('view', help='View song metadata')
    view_parser.add_argument('path', type=Path, help='File path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    fixer = SongMetadataFixer(verbose=getattr(args, 'verbose', False))
    
    if args.command == 'fix':
        path = args.path.resolve()
        if path.is_file():
            print(f"Fixing: {path.name}")
            fixer.fix_file(path)
            print(f"✓ Fixed: {fixer.fixed_count}, ✗ Errors: {fixer.error_count}")
        elif path.is_dir():
            fixer.fix_directory(path, recursive=args.recursive)
        else:
            print(f"Error: Invalid path: {path}")
    
    elif args.command == 'view':
        path = args.path.resolve()
        fixer.print_metadata(path)


if __name__ == '__main__':
    main()
