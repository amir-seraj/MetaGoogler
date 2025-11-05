#!/usr/bin/env python3
"""
Song Metadata Fixer
A command-line tool to fix and organize song metadata (ID3 tags) and cover art
Perfect for audiophiles managing music across multiple devices (DAP, phone, car stereo, etc.)
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime
import argparse
from io import BytesIO

try:
    from mutagen import File
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC
    from mutagen.flac import FLAC
    from mutagen.oggvorbis import OggVorbis
    from mutagen.wave import WAVE
    from mutagen.mp4 import MP4
    try:
        from mutagen.oggflac import OggFlac
    except ImportError:
        OggFlac = None
    try:
        from mutagen.oggopus import OggOpus
    except ImportError:
        OggOpus = None
    from PIL import Image
except ImportError as e:
    print(f"Error: Required library not found: {e}")
    print("Install with: pip install mutagen pillow")
    sys.exit(1)


class SongMetadataFixer:
    """Fixes and organizes song metadata"""
    
    # Comprehensive format support
    SUPPORTED_FORMATS = {
        # MP3 and ID3
        '.mp3', '.mp2',
        # MPEG-4 Audio
        '.m4a', '.m4b', '.m4p', '.aac',
        # FLAC
        '.flac', '.fla',
        # Ogg Vorbis
        '.ogg', '.oga',
        # Ogg Opus
        '.opus',
        # Ogg FLAC
        '.oggflac',
        # WMA
        '.wma',
        # WAV
        '.wav',
        # Apple Lossless
        '.alac',
        # DSF (DSD)
        '.dsf',
        # DFF (DSD)
        '.dff',
    }
    
    REQUIRED_FIELDS = {'title', 'artist', 'album'}
    COVER_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
    MIN_COVER_SIZE = (100, 100)
    MAX_COVER_SIZE = (3000, 3000)
    MAX_COVER_FILE_SIZE = 1024 * 1024  # 1MB
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.fixed_count = 0
        self.error_count = 0
        self.cover_fixed = 0
        self.validation_report = {
            'total': 0,
            'missing_metadata': [],
            'inconsistent_format': [],
            'valid': 0
        }
    
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
            # Try with MP4 handler first (M4A, M4B, etc.)
            if str(file_path).lower().endswith(('.m4a', '.m4b', '.m4p', '.aac')):
                try:
                    audio = MP4(str(file_path))
                    return {
                        'title': audio.tags.get('©nam', ['Unknown'])[0] if audio.tags else 'Unknown',
                        'artist': audio.tags.get('©ART', ['Unknown'])[0] if audio.tags else 'Unknown',
                        'album': audio.tags.get('©alb', ['Unknown'])[0] if audio.tags else 'Unknown',
                        'date': audio.tags.get('©day', ['Unknown'])[0] if audio.tags else 'Unknown',
                        'genre': audio.tags.get('©gen', ['Unknown'])[0] if audio.tags else 'Unknown',
                        'tracknumber': str(audio.tags.get('trkn', [(0, 0)])[0][0]) if audio.tags else '0',
                    }
                except Exception as mp4_error:
                    # Fall back to EasyID3 if MP4 fails
                    pass
            
            # Try with EasyID3 for ID3-based formats (MP3, etc.)
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
    
    def validate_metadata(self, metadata: dict, filename: str = "") -> Tuple[bool, List[str]]:
        """Validate metadata completeness and correctness"""
        issues = []
        
        # === COMPLETENESS CHECKS ===
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if metadata.get(field) == 'Unknown' or not metadata.get(field):
                issues.append(f"Missing {field}")
        
        # === CONSISTENCY CHECKS ===
        # Title checks
        title = metadata.get('title', '')
        if title:
            if len(title.strip()) < 2:
                issues.append("Title too short (< 2 chars)")
            if title != title.strip():
                issues.append("Title has leading/trailing whitespace")
            if '  ' in title:
                issues.append("Title has excessive whitespace")
        
        # Artist checks
        artist = metadata.get('artist', '')
        if artist:
            if artist != artist.strip():
                issues.append("Artist has leading/trailing whitespace")
            if '  ' in artist:
                issues.append("Artist has excessive whitespace")
            # Check for suspicious patterns
            if artist.lower() == 'unknown':
                issues.append("Artist marked as 'Unknown'")
        
        # Album checks
        album = metadata.get('album', '')
        if album:
            if album != album.strip():
                issues.append("Album has leading/trailing whitespace")
            if '  ' in album:
                issues.append("Album has excessive whitespace")
            # Check if album name matches filename (poor metadata)
            if filename and album.lower() == filename.lower().replace('.mp3', '').replace('.m4a', '').replace('.flac', ''):
                issues.append("Album seems to be copy of filename")
        
        # Genre checks
        genre = metadata.get('genre', '')
        if genre == 'Unknown' or not genre:
            issues.append("Missing or unknown genre")
        elif '  ' in genre:
            issues.append("Genre has excessive whitespace")
        
        # Date/Year checks
        date = metadata.get('date', '')
        if date == 'Unknown' or date == '0' or not date:
            issues.append("Missing date/year")
        elif date != 'Unknown':
            try:
                year = int(date.split('-')[0] if '-' in date else date)
                if year < 1900 or year > 2030:
                    issues.append(f"Date seems incorrect: {date}")
            except:
                issues.append(f"Date format invalid: {date}")
        
        # Track number checks
        track = metadata.get('tracknumber', '')
        if track and track != '0':
            # Check if track number looks valid
            if '/' in track:
                try:
                    current, total = map(int, track.split('/'))
                    if current > total:
                        issues.append(f"Track number {current} > total {total}")
                except:
                    issues.append(f"Invalid track format: {track}")
            else:
                try:
                    tn = int(track)
                    if tn < 0 or tn > 500:
                        issues.append(f"Track number out of range: {tn}")
                except:
                    issues.append(f"Track number not numeric: {track}")
        
        return len(issues) == 0, issues
    
    def set_metadata(self, file_path: Path, metadata: dict) -> bool:
        """Write metadata to audio file"""
        try:
            # Handle M4A/M4B/M4P/AAC files with MP4 handler
            if str(file_path).lower().endswith(('.m4a', '.m4b', '.m4p', '.aac')):
                try:
                    audio = MP4(str(file_path))
                    # Map metadata to MP4 tag names
                    if audio.tags is None:
                        audio.tags = {}
                    
                    if metadata.get('title') and metadata['title'] != 'Unknown':
                        audio.tags['©nam'] = [metadata['title']]
                    if metadata.get('artist') and metadata['artist'] != 'Unknown':
                        audio.tags['©ART'] = [metadata['artist']]
                    if metadata.get('album') and metadata['album'] != 'Unknown':
                        audio.tags['©alb'] = [metadata['album']]
                    if metadata.get('date') and metadata['date'] != 'Unknown':
                        audio.tags['©day'] = [metadata['date']]
                    if metadata.get('genre') and metadata['genre'] != 'Unknown':
                        audio.tags['©gen'] = [metadata['genre']]
                    if metadata.get('tracknumber') and metadata['tracknumber'] != '0':
                        try:
                            track_num = int(metadata['tracknumber'].split('/')[0])
                            audio.tags['trkn'] = [(track_num, 0)]
                        except (ValueError, IndexError):
                            pass
                    
                    audio.save()
                    self.log(f"Updated: {file_path.name}")
                    self.fixed_count += 1
                    return True
                except Exception as mp4_error:
                    # Fall back to EasyID3 if MP4 fails
                    pass
            
            # Handle ID3-based formats (MP3, etc.)
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
        
        is_valid, issues = self.validate_metadata(metadata, file_path.name)
        status = "✓ VALID" if is_valid else "⚠ ISSUES"
        
        print(f"\nMetadata for: {file_path.name}")
        print("-" * 50)
        for key, value in metadata.items():
            print(f"{key.capitalize():15}: {value}")
        print("-" * 50)
        print(f"Status: {status}")
        if issues:
            print(f"\n{len(issues)} issue(s) found:")
            for issue in issues:
                print(f"  ⚠ {issue}")
    
    def organize_file(self, file_path: Path, output_dir: Path) -> bool:
        """Organize file into Artist/Album/Track structure"""
        metadata = self.get_metadata(file_path)
        if metadata is None:
            return False
        
        # Create organized path: Artist/Album/Track.ext
        artist = metadata.get('artist', 'Unknown Artist')
        album = metadata.get('album', 'Unknown Album')
        title = metadata.get('title', 'Unknown Track')
        
        # Sanitize folder names
        artist = self._sanitize_path(artist)
        album = self._sanitize_path(album)
        title = self._sanitize_path(title)
        
        # Create target directory
        target_dir = output_dir / artist / album
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Create target file path
        target_file = target_dir / f"{title}{file_path.suffix}"
        
        try:
            shutil.copy2(file_path, target_file)
            self.log(f"Organized: {file_path.name} → {target_file.relative_to(output_dir)}")
            return True
        except Exception as e:
            print(f"Error organizing {file_path.name}: {e}")
            return False
    
    @staticmethod
    def _sanitize_path(name: str) -> str:
        """Remove invalid characters from folder/file names"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')
        return name.strip() or 'Unknown'
    
    def has_cover_art(self, file_path: Path) -> bool:
        """Check if file has embedded cover art"""
        try:
            audio = File(str(file_path))
            if audio is None:
                return False
            
            # Check for ID3 APIC frames (MP3, ID3-based formats)
            if hasattr(audio, 'tags') and audio.tags:
                try:
                    # Works for both dict and ID3 objects
                    for key in audio.tags:
                        if 'APIC' in str(key):
                            return True
                except Exception:
                    pass
            
            # Check for FLAC metadata blocks
            if isinstance(audio, FLAC):
                return len(audio.pictures) > 0
            
            # Check for Vorbis comments
            if hasattr(audio, 'pictures'):
                return len(audio.pictures) > 0
            
            return False
        except Exception as e:
            self.log(f"Error checking cover art in {file_path.name}: {e}")
            return False
    
    def validate_cover_art(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate cover art quality and specifications"""
        issues = []
        
        try:
            audio = File(str(file_path))
            if audio is None:
                issues.append("Cannot read file format")
                return False, issues
            
            has_cover = False
            
            # Check FLAC pictures
            if isinstance(audio, FLAC):
                if audio.pictures:
                    has_cover = True
                    for pic in audio.pictures:
                        issues.extend(self._validate_image_specs(pic.data, pic.mime))
            
            # Check ID3 APIC frames
            elif hasattr(audio, 'tags') and audio.tags:
                for frame in audio.tags.values():
                    if isinstance(frame, APIC):
                        has_cover = True
                        issues.extend(self._validate_image_specs(frame.data, frame.mime))
            
            if not has_cover:
                issues.append("No cover art found")
            
            return len(issues) == 0, issues
        
        except Exception as e:
            self.log(f"Error validating cover art: {e}")
            return False, [str(e)]
    
    @staticmethod
    def _validate_image_specs(image_data: bytes, mime: str) -> List[str]:
        """Validate image specifications"""
        issues = []
        
        # Check file size
        if len(image_data) > SongMetadataFixer.MAX_COVER_FILE_SIZE:
            issues.append(f"Cover art too large ({len(image_data)/1024:.1f}KB, max 1MB)")
        
        try:
            img = Image.open(BytesIO(image_data))
            width, height = img.size
            
            # Check minimum size
            if width < SongMetadataFixer.MIN_COVER_SIZE[0] or height < SongMetadataFixer.MIN_COVER_SIZE[1]:
                issues.append(f"Cover too small ({width}x{height}px, min {SongMetadataFixer.MIN_COVER_SIZE[0]}x{SongMetadataFixer.MIN_COVER_SIZE[1]}px)")
            
            # Check maximum size
            if width > SongMetadataFixer.MAX_COVER_SIZE[0] or height > SongMetadataFixer.MAX_COVER_SIZE[1]:
                issues.append(f"Cover too large ({width}x{height}px, max {SongMetadataFixer.MAX_COVER_SIZE[0]}x{SongMetadataFixer.MAX_COVER_SIZE[1]}px)")
            
            # Check aspect ratio (should be square or close)
            ratio = max(width, height) / min(width, height)
            if ratio > 1.1:  # More than 10% deviation from square
                issues.append(f"Cover not square (ratio {ratio:.2f}:1)")
            
            return issues
        except Exception as e:
            return [f"Invalid image format: {e}"]
    
    def embed_cover_art(self, file_path: Path, cover_path: Path) -> bool:
        """Embed cover art from image file into audio"""
        if not cover_path.exists():
            print(f"Error: Cover art file not found: {cover_path}")
            return False
        
        try:
            with open(cover_path, 'rb') as f:
                image_data = f.read()
            
            # Validate image
            issues = self._validate_image_specs(image_data, cover_path.suffix)
            if issues:
                print(f"Cover art issues: {', '.join(issues)}")
                return False
            
            audio = File(str(file_path))
            if audio is None:
                print(f"Error: Cannot read {file_path.name}")
                return False
            
            # Embed in FLAC
            if isinstance(audio, FLAC):
                pic = FLAC.Picture()
                pic.data = image_data
                pic.mime = f"image/{cover_path.suffix[1:].lower()}"
                audio.add_picture(pic)
                audio.save()
            
            # Embed in MP3
            elif hasattr(audio, 'tags') and audio.tags:
                audio.tags['APIC'] = APIC(
                    encoding=3,
                    mime=f"image/{cover_path.suffix[1:].lower()}",
                    type=3,
                    desc='Cover',
                    data=image_data
                )
                audio.save()
            
            else:
                print(f"Cover art embedding not supported for {file_path.suffix}")
                return False
            
            self.log(f"Embedded cover art: {file_path.name}")
            self.cover_fixed += 1
            return True
        
        except Exception as e:
            print(f"Error embedding cover art: {e}")
            return False
    
    def validate_directory(self, directory: Path) -> Dict:
        """Validate metadata for all files in directory"""
        report = {
            'total': 0,
            'valid': 0,
            'issues': [],
            'timestamp': datetime.now().isoformat()
        }
        
        audio_files = [f for f in directory.glob('*') 
                       if f.is_file() and self.is_supported_format(f)]
        
        for audio_file in audio_files:
            report['total'] += 1
            metadata = self.get_metadata(audio_file)
            if metadata:
                is_valid, issues = self.validate_metadata(metadata, audio_file.name)
                if is_valid:
                    report['valid'] += 1
                else:
                    report['issues'].append({
                        'file': audio_file.name,
                        'problems': issues
                    })
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description='Fix, validate, and organize song metadata for audiophiles managing multiple devices',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WORKFLOW FOR AUDIOPHILE:
  1. Fix metadata: python song_metadata_fixer.py fix ./downloads
  2. Validate before sync: python song_metadata_fixer.py validate ./downloads
  3. Organize by artist/album: python song_metadata_fixer.py organize ./downloads -o ./organized
  4. View details: python song_metadata_fixer.py view song.mp3

Examples:
  # Fix all downloaded songs recursively
  python song_metadata_fixer.py fix ./downloads -r -v
  
  # Validate metadata quality before syncing to DAP
  python song_metadata_fixer.py validate ./music --report
  
  # Organize music library for easy sync to devices
  python song_metadata_fixer.py organize ./downloads -o ~/Music/Organized
  
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
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate metadata quality')
    validate_parser.add_argument('path', type=Path, help='Directory path')
    validate_parser.add_argument('--report', action='store_true',
                                help='Save validation report as JSON')
    validate_parser.add_argument('-v', '--verbose', action='store_true',
                               help='Verbose output')
    
    # Organize command
    org_parser = subparsers.add_parser('organize', help='Organize files by Artist/Album')
    org_parser.add_argument('path', type=Path, help='Source directory')
    org_parser.add_argument('-o', '--output', type=Path, required=True,
                           help='Output directory for organized files')
    org_parser.add_argument('-v', '--verbose', action='store_true',
                           help='Verbose output')
    
    # Check cover art command
    cover_check = subparsers.add_parser('cover-check', help='Check cover art in files')
    cover_check.add_argument('path', type=Path, help='File or directory path')
    cover_check.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Embed cover art command
    cover_embed = subparsers.add_parser('cover-embed', help='Embed cover art into files')
    cover_embed.add_argument('path', type=Path, help='Audio file')
    cover_embed.add_argument('-c', '--cover', type=Path, required=True, help='Cover image file')
    cover_embed.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Supported formats command
    formats_parser = subparsers.add_parser('formats', help='Show supported audio formats')
    
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
    
    elif args.command == 'validate':
        path = args.path.resolve()
        if not path.is_dir():
            print(f"Error: {path} is not a directory")
            return
        
        print(f"Validating metadata in: {path}")
        report = fixer.validate_directory(path)
        
        print(f"\n{'='*50}")
        print(f"Validation Report")
        print(f"{'='*50}")
        print(f"Total files: {report['total']}")
        print(f"Valid: {report['valid']}")
        print(f"Issues found: {report['total'] - report['valid']}")
        
        if report['issues']:
            print(f"\n{'Issues:'}")
            for item in report['issues'][:10]:  # Show first 10
                print(f"  {item['file']}")
                for problem in item['problems']:
                    print(f"    - {problem}")
            if len(report['issues']) > 10:
                print(f"  ... and {len(report['issues']) - 10} more")
        
        if args.report:
            report_file = path / 'metadata_report.json'
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\n✓ Report saved to: {report_file}")
    
    elif args.command == 'organize':
        path = args.path.resolve()
        output = args.output.resolve()
        
        if not path.is_dir():
            print(f"Error: {path} is not a directory")
            return
        
        output.mkdir(parents=True, exist_ok=True)
        
        audio_files = [f for f in path.glob('*')
                      if f.is_file() and fixer.is_supported_format(f)]
        
        print(f"Organizing {len(audio_files)} files...")
        organized = sum(1 for f in audio_files if fixer.organize_file(f, output))
        
        print(f"\n✓ Organized: {organized}/{len(audio_files)}")
        print(f"Output directory: {output}")
    
    elif args.command == 'cover-check':
        path = args.path.resolve()
        
        if path.is_file():
            has_cover = fixer.has_cover_art(path)
            is_valid, issues = fixer.validate_cover_art(path)
            
            print(f"\nCover art check: {path.name}")
            print("-" * 50)
            print(f"Has cover art: {'✓ Yes' if has_cover else '✗ No'}")
            
            if issues:
                print(f"Issues ({len(issues)}):")
                for issue in issues:
                    print(f"  ⚠ {issue}")
            else:
                print("✓ Cover art is valid")
        
        elif path.is_dir():
            print(f"Checking cover art in: {path}")
            audio_files = [f for f in path.glob('*') 
                          if f.is_file() and fixer.is_supported_format(f)]
            
            with_cover = 0
            without_cover = 0
            
            for audio_file in audio_files:
                if fixer.has_cover_art(audio_file):
                    with_cover += 1
                else:
                    without_cover += 1
            
            print(f"\nCover Art Summary")
            print("-" * 50)
            print(f"Total files: {len(audio_files)}")
            print(f"With cover: {with_cover}")
            print(f"Without cover: {without_cover}")
            print(f"Coverage: {(with_cover/len(audio_files)*100):.1f}%" if audio_files else "N/A")
    
    elif args.command == 'cover-embed':
        audio_file = args.path.resolve()
        cover_file = args.cover.resolve()
        
        if not audio_file.exists():
            print(f"Error: Audio file not found: {audio_file}")
            return
        
        print(f"Embedding cover art...")
        if fixer.embed_cover_art(audio_file, cover_file):
            print(f"✓ Successfully embedded cover art into {audio_file.name}")
        else:
            print(f"✗ Failed to embed cover art")
    
    elif args.command == 'formats':
        print("\nSupported Audio Formats")
        print("=" * 50)
        
        formats_by_type = {
            'MP3 & ID3': ['.mp3', '.mp2'],
            'MPEG-4 Audio': ['.m4a', '.m4b', '.m4p', '.aac'],
            'FLAC': ['.flac', '.fla'],
            'Ogg Codecs': ['.ogg', '.oga', '.opus', '.oggflac'],
            'WMA': ['.wma'],
            'WAV': ['.wav'],
            'Lossless': ['.alac'],
            'DSD': ['.dsf', '.dff'],
        }
        
        for category, formats in formats_by_type.items():
            supported = [f for f in formats if f in SongMetadataFixer.SUPPORTED_FORMATS]
            if supported:
                print(f"\n{category}:")
                for fmt in supported:
                    print(f"  • {fmt}")
        
        print(f"\nTotal: {len(SongMetadataFixer.SUPPORTED_FORMATS)} formats supported")
        
        print("\n" + "=" * 50)
        print("Cover Art Support: JPEG, PNG, GIF, BMP")
        print(f"Optimal size: 500x500 - 1500x1500 px")
        print(f"Max file size: 1 MB")


if __name__ == '__main__':
    main()
