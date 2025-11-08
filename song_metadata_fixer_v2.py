#!/usr/bin/env python3
"""
Song Metadata Fixer v2 - Refactored with Logging and Configuration
A command-line tool to fix and organize song metadata (ID3 tags) and cover art
Perfect for audiophiles managing music across multiple devices (DAP, phone, car stereo, etc.)

Phase 0 Refactoring:
- Configuration system (config.json)
- Centralized logging (fixer.log)
- AIManager for LLM operations
- Core methods return status instead of printing
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

# Import our new modular components
from logger_setup import get_logger
from config_manager import ConfigManager
from ai_manager import AIManager

try:
    from song_identifier import SongIdentifier, SongIdentification
    IDENTIFIER_AVAILABLE = True
except ImportError:
    IDENTIFIER_AVAILABLE = False
    SongIdentifier = None
    SongIdentification = None

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


class OperationResult:
    """Encapsulates the result of an operation for clean return values"""
    
    def __init__(self, success: bool, message: str = "", data: Dict = None):
        self.success = success
        self.message = message
        self.data = data or {}
    
    def __bool__(self):
        return self.success
    
    def __repr__(self):
        return f"OperationResult(success={self.success}, message='{self.message}')"


class SongMetadataFixer:
    """Fixes and organizes song metadata - Refactored for Phase 0"""
    
    def __init__(self, verbose: bool = False, config_path: Optional[Path] = None):
        """
        Initialize the metadata fixer.
        
        Args:
            verbose: Enable verbose logging
            config_path: Path to config.json (uses default if None)
        """
        self.logger = get_logger("SongMetadataFixer")
        self.config = ConfigManager(config_path)
        self.ai_manager = AIManager(config_path)
        self.identifier = SongIdentifier() if IDENTIFIER_AVAILABLE else None
        self.verbose = verbose
        
        # Statistics
        self.fixed_count = 0
        self.error_count = 0
        self.cover_fixed = 0
        self.validation_report = {
            'total': 0,
            'missing_metadata': [],
            'inconsistent_format': [],
            'valid': 0
        }
        
        # Load configuration
        self.supported_formats = set(self.config.get_supported_formats())
        self.required_fields = {'title', 'artist', 'album'}
        self.cover_formats = set(self.config.get_allowed_cover_formats())
        self.max_cover_size_kb = self.config.get_max_cover_size_kb()
        self.max_cover_dimensions = self.config.get_max_cover_dimensions()
        
        self.logger.info("SongMetadataFixer initialized")
        self.logger.debug(f"Supported formats: {self.supported_formats}")
    
    def is_supported_format(self, file_path: Path) -> bool:
        """Check if file is a supported audio format"""
        return file_path.suffix.lower() in self.supported_formats
    
    def _is_file_corrupted(self, file_path: Path) -> bool:
        """
        Check if file is corrupted or invalid.
        
        Returns:
            True if file is corrupted or invalid, False if it's a valid audio file
        """
        try:
            with open(file_path, 'rb') as f:
                header = f.read(20)
                # Check for common non-audio headers
                if header.startswith(b'<'):  # HTML/XML error page
                    self.logger.debug(f"File {file_path.name} detected as HTML/XML")
                    return True
                if header.startswith(b'PK'):  # ZIP file
                    self.logger.debug(f"File {file_path.name} detected as ZIP")
                    return True
                if header.startswith(b'%PDF'):  # PDF file
                    self.logger.debug(f"File {file_path.name} detected as PDF")
                    return True
                # Valid audio file indicators
                if any([
                    header.startswith(b'ID3'),      # ID3v2 (MP3)
                    header.startswith(b'\xff\xfb'),  # MP3 frame sync (MPEG1 Layer3)
                    header.startswith(b'\xff\xfa'),  # MP3 frame sync (MPEG2 Layer3)
                    b'ftyp' in header[:20],         # MP4/M4A (ftyp at offset 4)
                    header.startswith(b'fLaC'),      # FLAC
                    header.startswith(b'OggS'),      # Ogg/Vorbis
                    header.startswith(b'RIFF'),      # WAV
                    header.startswith(b'wvpk'),      # WavPack
                ]):
                    return False
                # No recognizable audio header
                self.logger.debug(f"File {file_path.name} has no recognizable audio header")
                return True
        except Exception as e:
            self.logger.debug(f"Exception checking file corruption: {e}")
            return True
        return False
    
    def get_metadata(self, file_path: Path) -> Optional[dict]:
        """
        Extract metadata from audio file.
        
        Returns:
            Dictionary of metadata or None if error
        """
        try:
            # Check for corrupted files first
            if self._is_file_corrupted(file_path):
                self.logger.warning(f"File appears corrupted: {file_path.name}")
                return None
            
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
                    self.logger.debug(f"MP4 read failed, trying ID3: {mp4_error}")
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
            self.logger.error(f"Error reading metadata from {file_path.name}: {e}")
            self.error_count += 1
            return None

    
    def validate_metadata(self, metadata: dict, filename: str = "") -> Tuple[bool, List[str]]:
        """
        Validate metadata completeness and correctness.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # === COMPLETENESS CHECKS ===
        # Check required fields
        for field in self.required_fields:
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
            if artist.lower() == 'unknown':
                issues.append("Artist marked as 'Unknown'")
        
        # Album checks
        album = metadata.get('album', '')
        if album:
            if album != album.strip():
                issues.append("Album has leading/trailing whitespace")
            if '  ' in album:
                issues.append("Album has excessive whitespace")
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
        
        self.logger.debug(f"Metadata validation: {len(issues)} issues found")
        return len(issues) == 0, issues
    
    def set_metadata(self, file_path: Path, metadata: dict) -> OperationResult:
        """
        Write metadata to audio file.
        
        Returns:
            OperationResult with success status
        """
        try:
            # Handle M4A/M4B/M4P/AAC files with MP4 handler
            if str(file_path).lower().endswith(('.m4a', '.m4b', '.m4p', '.aac')):
                try:
                    audio = MP4(str(file_path))
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
                    self.logger.info(f"Updated MP4 tags: {file_path.name}")
                    self.fixed_count += 1
                    return OperationResult(True, f"Updated: {file_path.name}")
                except Exception as mp4_error:
                    self.logger.debug(f"MP4 write failed, trying ID3: {mp4_error}")
                    pass
            
            # Handle ID3-based formats (MP3, etc.)
            audio = EasyID3(str(file_path))
            for key, value in metadata.items():
                if value and value != 'Unknown':
                    audio[key] = str(value)
            audio.save()
            self.logger.info(f"Updated ID3 tags: {file_path.name}")
            self.fixed_count += 1
            return OperationResult(True, f"Updated: {file_path.name}")
        except Exception as e:
            self.logger.error(f"Error writing metadata to {file_path.name}: {e}")
            self.error_count += 1
            return OperationResult(False, f"Error: {str(e)}")
    
    def identify_song(self, file_path: Path) -> Optional[Dict]:
        """
        Identify song using audio analysis and APIs.
        
        Attempts to identify missing metadata by:
        1. Querying audio fingerprint databases
        2. Searching Spotify API
        3. Using ACRCloud (if configured)
        
        Args:
            file_path: Path to audio file (or string path)
            
        Returns:
            Dictionary with identified metadata (title, artist, album, etc.)
            Returns None if identification fails
        """
        # Convert string to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        if not IDENTIFIER_AVAILABLE:
            self.logger.warning("Song identifier not available - install: pip install librosa")
            return None
        
        if not self.identifier:
            self.logger.warning("Song identifier not initialized")
            return None
        
        try:
            self.logger.info(f"Attempting to identify: {file_path.name}")
            
            # Attempt identification
            result = self.identifier.identify_song(file_path)
            
            if result:
                # Convert to metadata dict
                metadata = {
                    'title': result.title,
                    'artist': result.artist,
                    'album': result.album or 'Unknown',
                    'confidence': result.confidence,
                    'identification_source': result.source,
                }
                
                if result.isrc:
                    metadata['isrc'] = result.isrc
                
                self.logger.info(f"✓ Identified: {result.artist} - {result.title} "
                                f"(confidence: {result.confidence:.0%}, source: {result.source})")
                
                return metadata
            else:
                self.logger.warning(f"Could not identify: {file_path.name}")
                return None
        
        except Exception as e:
            self.logger.error(f"Error identifying song: {e}")
            return None
    
    def identify_and_fill_metadata(self, file_path: Path, overwrite_existing: bool = False) -> OperationResult:
        """
        Identify song and fill in missing metadata fields.
        
        Args:
            file_path: Path to audio file (or string path)
            overwrite_existing: If True, overwrite existing metadata with identified data
            
        Returns:
            OperationResult with success status
        """
        # Convert string to Path if needed
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        try:
            # Get current metadata
            current = self.get_metadata(file_path)
            
            if not current:
                return OperationResult(False, "Could not read current metadata")
            
            # Check if we need identification
            missing_fields = []
            for field in ['title', 'artist', 'album']:
                if not current.get(field) or current[field] == 'Unknown':
                    missing_fields.append(field)
            
            if not missing_fields and not overwrite_existing:
                self.logger.info(f"All metadata complete for: {file_path.name}")
                return OperationResult(True, "Metadata complete, no identification needed")
            
            # Attempt identification
            identified = self.identify_song(file_path)
            
            if not identified:
                return OperationResult(False, "Could not identify song")
            
            # Merge identified data with existing
            if overwrite_existing:
                # Replace all metadata with identified data
                new_metadata = {
                    'title': identified['title'],
                    'artist': identified['artist'],
                    'album': identified['album'],
                }
            else:
                # Fill only missing fields
                new_metadata = current.copy()
                for field in missing_fields:
                    if field in identified:
                        new_metadata[field] = identified[field]
            
            # Write updated metadata
            result = self.set_metadata(file_path, new_metadata)
            
            if result.success:
                self.logger.info(f"✓ Filled metadata: {file_path.name}")
                return OperationResult(True, f"Updated with identified metadata: {identified['title']}")
            else:
                return result
        
        except Exception as e:
            self.logger.error(f"Error in identify_and_fill_metadata: {e}")
            return OperationResult(False, f"Error: {str(e)}")
    
    def fix_file(self, file_path: Path) -> OperationResult:
        """
        Fix metadata for a single file.
        
        Returns:
            OperationResult with success status
        """
        if not self.is_supported_format(file_path):
            msg = f"Unsupported format: {file_path.suffix}"
            self.logger.debug(msg)
            return OperationResult(False, msg)
        
        metadata = self.get_metadata(file_path)
        if metadata is None:
            return OperationResult(False, f"Could not read metadata")
        
        # Basic cleaning - remove extra whitespace
        cleaned_metadata = {
            k: v.strip() if isinstance(v, str) else v 
            for k, v in metadata.items()
        }
        
        return self.set_metadata(file_path, cleaned_metadata)
    
    def fix_directory(self, directory: Path, recursive: bool = False) -> Dict:
        """
        Fix metadata for all songs in a directory.
        
        Returns:
            Dictionary with statistics
        """
        if not directory.exists():
            self.logger.error(f"Directory not found: {directory}")
            return {'total': 0, 'fixed': 0, 'errors': 0}
        
        pattern = '**/*' if recursive else '*'
        audio_files = [
            f for f in directory.glob(pattern)
            if f.is_file() and self.is_supported_format(f)
        ]
        
        if not audio_files:
            self.logger.warning("No audio files found")
            return {'total': 0, 'fixed': 0, 'errors': 0}
        
        self.logger.info(f"Found {len(audio_files)} audio file(s)")
        for audio_file in audio_files:
            self.logger.info(f"Processing: {audio_file.relative_to(directory)}")
            self.fix_file(audio_file)
        
        stats = {
            'total': len(audio_files),
            'fixed': self.fixed_count,
            'errors': self.error_count
        }
        self.logger.info(f"Fix directory complete: {stats}")
        return stats
    
    def has_cover_art(self, file_path: Path) -> bool:
        """Check if file has embedded cover art"""
        try:
            audio = File(str(file_path))
            if audio is None:
                return False
            
            # Check for ID3 APIC frames (MP3, ID3-based formats)
            if hasattr(audio, 'tags') and audio.tags:
                try:
                    for key in audio.tags:
                        if 'APIC' in str(key):
                            return True
                except Exception:
                    pass
            
            # Check for MP4/M4A covr atoms
            if isinstance(audio, MP4):
                return audio.tags is not None and 'covr' in audio.tags
            
            # Check for FLAC metadata blocks
            if isinstance(audio, FLAC):
                return len(audio.pictures) > 0
            
            # Check for Vorbis comments
            if hasattr(audio, 'pictures'):
                return len(audio.pictures) > 0
            
            return False
        except Exception as e:
            self.logger.debug(f"Error checking cover art in {file_path.name}: {e}")
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
            self.logger.error(f"Error validating cover art: {e}")
            return False, [str(e)]
    
    def _validate_image_specs(self, image_data: bytes, mime: str) -> List[str]:
        """Validate image specifications"""
        issues = []
        max_size_bytes = self.max_cover_size_kb * 1024
        
        # Check file size
        if len(image_data) > max_size_bytes:
            issues.append(f"Cover art too large ({len(image_data)/1024:.1f}KB, max {self.max_cover_size_kb}KB)")
        
        try:
            img = Image.open(BytesIO(image_data))
            width, height = img.size
            max_w, max_h = self.max_cover_dimensions
            
            # Check minimum size (100x100)
            if width < 100 or height < 100:
                issues.append(f"Cover too small ({width}x{height}px, min 100x100px)")
            
            # Check maximum size
            if width > max_w or height > max_h:
                issues.append(f"Cover too large ({width}x{height}px, max {max_w}x{max_h}px)")
            
            # Check aspect ratio (should be reasonable - allow up to 1.5:1 for some album artwork)
            ratio = max(width, height) / min(width, height)
            if ratio > 1.5:  # More than 50% deviation from square
                issues.append(f"Cover extreme aspect ratio (ratio {ratio:.2f}:1)")
            
            return issues
        except Exception as e:
            return [f"Invalid image format: {e}"]
    
    def download_cover_art_from_internet(self, artist: str, title: str) -> Optional[bytes]:
        """Download cover art from internet for given artist and title.
        
        Uses CoverArtFetcher to:
        1. Fetch candidate images from multiple sources (Spotify, Last.fm, MusicBrainz)
        2. Cluster by RGB histogram similarity
        3. Return bytes of image from largest cluster (consensus voting)
        
        Args:
            artist: Artist name
            title: Track title
            
        Returns:
            Image bytes if successful, None otherwise
        """
        try:
            from cover_art_fetcher import CoverArtFetcher
        except ImportError:
            self.logger.warning("CoverArtFetcher not available - cannot download from internet")
            return None
        
        try:
            fetcher = CoverArtFetcher()
            
            # Fetch best candidate from multiple sources with similarity clustering
            self.logger.debug(f"Fetching cover art for {artist} - {title}")
            best_candidate = fetcher.fetch_cover_art(artist, title)
            
            if best_candidate:
                self.logger.info(f"✓ Selected best cover for {artist} - {title} "
                                f"via consensus clustering (similarity: {best_candidate.similarity_score:.1%})")
                return best_candidate.image_data
            else:
                self.logger.warning(f"No cover art found for {artist} - {title}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error downloading cover art: {e}")
            return None
    
    def embed_cover_art(self, file_path: Path, cover_path: Path) -> OperationResult:
        """Embed cover art from image file into audio"""
        if not cover_path.exists():
            msg = f"Cover art file not found: {cover_path}"
            self.logger.error(msg)
            return OperationResult(False, msg)
        
        try:
            with open(cover_path, 'rb') as f:
                image_data = f.read()
            
            # Validate image
            issues = self._validate_image_specs(image_data, cover_path.suffix)
            if issues:
                msg = f"Cover art issues: {', '.join(issues)}"
                self.logger.warning(msg)
                return OperationResult(False, msg)
            
            audio = File(str(file_path))
            if audio is None:
                msg = f"Cannot read {file_path.name}"
                self.logger.error(msg)
                return OperationResult(False, msg)
            
            mime_type = f"image/{cover_path.suffix[1:].lower()}"
            embedded = False
            
            # Embed in MP4/M4A
            if isinstance(audio, MP4):
                try:
                    audio.tags['covr'] = [image_data]
                    audio.save()
                    embedded = True
                    self.logger.debug(f"Embedded MP4 cover art: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to embed MP4 cover: {e}")
                    return OperationResult(False, f"Error embedding MP4 cover: {str(e)}")
            
            # Embed in FLAC
            elif isinstance(audio, FLAC):
                try:
                    pic = FLAC.Picture()
                    pic.data = image_data
                    pic.mime = mime_type
                    audio.add_picture(pic)
                    audio.save()
                    embedded = True
                    self.logger.debug(f"Embedded FLAC cover art: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to embed FLAC cover: {e}")
                    return OperationResult(False, f"Error embedding FLAC cover: {str(e)}")
            
            # Embed in MP3 (ID3)
            elif hasattr(audio, 'tags') and audio.tags is not None:
                try:
                    apic = APIC(
                        encoding=3,
                        mime=mime_type,
                        type=3,  # type=3 means front cover
                        desc='Cover',
                        data=image_data
                    )
                    audio.tags['APIC'] = apic
                    audio.save()
                    embedded = True
                    self.logger.debug(f"Embedded MP3 cover art: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to embed MP3 cover: {e}")
                    return OperationResult(False, f"Error embedding MP3 cover: {str(e)}")
            
            else:
                msg = f"Cover art embedding not supported for {file_path.suffix}"
                self.logger.warning(msg)
                return OperationResult(False, msg)
            
            # Verify embedding was successful
            if embedded and self.has_cover_art(file_path):
                self.logger.info(f"✓ Embedded cover art: {file_path.name}")
                self.cover_fixed += 1
                return OperationResult(True, f"Embedded cover art: {file_path.name}")
            else:
                msg = f"Failed to verify cover art embedding in {file_path.name}"
                self.logger.error(msg)
                return OperationResult(False, msg)
        
        except Exception as e:
            self.logger.error(f"Error embedding cover art: {e}")
            return OperationResult(False, f"Error: {str(e)}")
    
    def embed_cover_art_bytes(self, file_path: Path, image_bytes: bytes, mime_type: str = "image/jpeg") -> OperationResult:
        """Embed cover art from raw bytes into audio file.
        
        Args:
            file_path: Path to audio file
            image_bytes: Image data as bytes
            mime_type: MIME type of image (default: image/jpeg)
            
        Returns:
            OperationResult with success status
        """
        if not image_bytes:
            msg = "No image data provided"
            self.logger.error(msg)
            return OperationResult(False, msg)
        
        try:
            # Validate image
            issues = self._validate_image_specs(image_bytes, ".jpg")
            if issues:
                msg = f"Cover art issues: {', '.join(issues)}"
                self.logger.warning(msg)
                return OperationResult(False, msg)
            
            audio = File(str(file_path))
            if audio is None:
                msg = f"Cannot read {file_path.name}"
                self.logger.error(msg)
                return OperationResult(False, msg)
            
            embedded = False
            
            # Embed in MP4/M4A
            if isinstance(audio, MP4):
                try:
                    audio.tags['covr'] = [image_bytes]
                    audio.save()
                    embedded = True
                    self.logger.debug(f"Embedded MP4 cover art: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to embed MP4 cover: {e}")
                    return OperationResult(False, f"Error embedding MP4 cover: {str(e)}")
            
            # Embed in FLAC
            elif isinstance(audio, FLAC):
                try:
                    pic = FLAC.Picture()
                    pic.data = image_bytes
                    pic.mime = mime_type
                    audio.add_picture(pic)
                    audio.save()
                    embedded = True
                    self.logger.debug(f"Embedded FLAC cover art: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to embed FLAC cover: {e}")
                    return OperationResult(False, f"Error embedding FLAC cover: {str(e)}")
            
            # Embed in MP3 (ID3)
            elif hasattr(audio, 'tags') and audio.tags is not None:
                try:
                    apic = APIC(
                        encoding=3,
                        mime=mime_type,
                        type=3,  # type=3 means front cover
                        desc='Cover',
                        data=image_bytes
                    )
                    audio.tags['APIC'] = apic
                    audio.save()
                    embedded = True
                    self.logger.debug(f"Embedded MP3 cover art: {file_path.name}")
                except Exception as e:
                    self.logger.error(f"Failed to embed MP3 cover: {e}")
                    return OperationResult(False, f"Error embedding MP3 cover: {str(e)}")
            
            else:
                msg = f"Cover art embedding not supported for {file_path.suffix}"
                self.logger.warning(msg)
                return OperationResult(False, msg)
            
            # Verify embedding was successful
            if embedded and self.has_cover_art(file_path):
                self.logger.info(f"✓ Embedded cover art: {file_path.name}")
                self.cover_fixed += 1
                return OperationResult(True, f"Embedded cover art: {file_path.name}")
            else:
                msg = f"Failed to verify cover art embedding in {file_path.name}"
                self.logger.error(msg)
                return OperationResult(False, msg)
        
        except Exception as e:
            self.logger.error(f"Error embedding cover art: {e}")
            return OperationResult(False, f"Error: {str(e)}")
    
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
        
        self.logger.info(f"Validation complete: {report['valid']}/{report['total']} valid")
        return report
    
    @staticmethod
    def _sanitize_path(name: str) -> str:
        """Remove invalid characters from folder/file names"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '')
        return name.strip() or 'Unknown'
    
    def organize_file(self, file_path: Path, output_dir: Path) -> OperationResult:
        """Organize file into Artist/Album/Track structure"""
        metadata = self.get_metadata(file_path)
        if metadata is None:
            return OperationResult(False, "Could not read metadata")
        
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
            self.logger.info(f"Organized: {file_path.name} → {target_file.relative_to(output_dir)}")
            return OperationResult(True, f"Organized: {file_path.name}")
        except Exception as e:
            self.logger.error(f"Error organizing {file_path.name}: {e}")
            return OperationResult(False, str(e))


def main():
    """Main entry point with argument parsing"""
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
  python song_metadata_fixer_v2.py fix ./downloads -r -v
  
  # Validate metadata quality before syncing to DAP
  python song_metadata_fixer_v2.py validate ./music --report
  
  # Organize music library for easy sync to devices
  python song_metadata_fixer_v2.py organize ./downloads -o ~/Music/Organized
  
  # View metadata without modifying
  python song_metadata_fixer_v2.py view song.mp3
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
    
    # Cover check command
    cover_check = subparsers.add_parser('cover-check', help='Check cover art in files')
    cover_check.add_argument('path', type=Path, help='File or directory path')
    cover_check.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Embed cover art command
    cover_embed = subparsers.add_parser('cover-embed', help='Embed cover art into files')
    cover_embed.add_argument('path', type=Path, help='Audio file')
    cover_embed.add_argument('-c', '--cover', type=Path, required=True, help='Cover image file')
    cover_embed.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # AI fix command (uses LLM to improve metadata)
    ai_fix = subparsers.add_parser('ai-fix', help='Use AI to improve metadata')
    ai_fix.add_argument('path', type=Path, help='File or directory path')
    ai_fix.add_argument('-r', '--recursive', action='store_true', help='Process subdirectories')
    ai_fix.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    # Formats command
    formats_parser = subparsers.add_parser('formats', help='Show supported audio formats')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    fixer = SongMetadataFixer(verbose=getattr(args, 'verbose', False))
    
    if args.command == 'fix':
        path = args.path.resolve()
        if path.is_file():
            fixer.logger.info(f"Fixing: {path.name}")
            result = fixer.fix_file(path)
            print(f"✓ Status: {result.message}")
        elif path.is_dir():
            stats = fixer.fix_directory(path, recursive=args.recursive)
            print(f"✓ Fixed: {stats['fixed']}, ✗ Errors: {stats['errors']}")
        else:
            print(f"Error: Invalid path: {path}")
    
    elif args.command == 'view':
        path = args.path.resolve()
        if not path.exists():
            print(f"Error: File not found: {path}")
            return
        
        metadata = fixer.get_metadata(path)
        if metadata:
            is_valid, issues = fixer.validate_metadata(metadata, path.name)
            status = "✓ VALID" if is_valid else "⚠ ISSUES"
            
            print(f"\nMetadata for: {path.name}")
            print("-" * 50)
            for key, value in metadata.items():
                print(f"{key.capitalize():15}: {value}")
            print("-" * 50)
            print(f"Status: {status}")
            if issues:
                print(f"\n{len(issues)} issue(s) found:")
                for issue in issues:
                    print(f"  ⚠ {issue}")
    
    elif args.command == 'validate':
        path = args.path.resolve()
        if not path.is_dir():
            print(f"Error: {path} is not a directory")
            return
        
        fixer.logger.info(f"Validating metadata in: {path}")
        report = fixer.validate_directory(path)
        
        print(f"\n{'='*50}")
        print(f"Validation Report")
        print(f"{'='*50}")
        print(f"Total files: {report['total']}")
        print(f"Valid: {report['valid']}")
        print(f"Issues found: {report['total'] - report['valid']}")
        
        if report['issues']:
            print(f"\nIssues:")
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
        organized = 0
        for f in audio_files:
            result = fixer.organize_file(f, output)
            if result.success:
                organized += 1
        
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
            fixer.logger.info(f"Checking cover art in: {path}")
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
        result = fixer.embed_cover_art(audio_file, cover_file)
        if result.success:
            print(f"✓ {result.message}")
        else:
            print(f"✗ {result.message}")
    
    elif args.command == 'ai-fix':
        # TODO: Use AIManager to improve metadata with LLM
        print("AI-powered metadata fixing coming in next phase!")
        path = args.path.resolve()
        print(f"Would fix metadata for: {path}")
    
    elif args.command == 'formats':
        supported_formats = fixer.config.get_supported_formats()
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
            supported = [f for f in formats if f in supported_formats]
            if supported:
                print(f"\n{category}:")
                for fmt in supported:
                    print(f"  • {fmt}")
        
        print(f"\nTotal: {len(supported_formats)} formats supported")
        
        print("\n" + "=" * 50)
        print("Cover Art Support: JPEG, PNG, GIF, BMP")
        print(f"Optimal size: 500x500 - 1500x1500 px")
        print(f"Max file size: {fixer.config.get_max_cover_size_kb()}KB")


if __name__ == '__main__':
    main()
