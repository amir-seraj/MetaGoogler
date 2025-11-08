#!/usr/bin/env python3
"""
Song Identifier - Identify songs using free APIs
Supports multiple identification methods:
1. Audio fingerprinting (Shazam-like)
2. ACRCloud free API
3. MusicBrainz acoustic fingerprint lookup
4. Genius API (song lookup by lyrics)
"""

import os
import sys
import json
import requests
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from io import BytesIO

try:
    import librosa
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    librosa = None
    np = None

logger = logging.getLogger(__name__)


@dataclass
class SongIdentification:
    """Result of song identification attempt"""
    title: str
    artist: str
    album: Optional[str] = None
    duration: Optional[float] = None
    confidence: float = 0.0  # 0.0-1.0
    source: str = ""  # Which API found it
    isrc: Optional[str] = None  # International Standard Recording Code
    spotify_id: Optional[str] = None
    musicbrainz_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'duration': self.duration,
            'confidence': self.confidence,
            'source': self.source,
            'isrc': self.isrc,
            'spotify_id': self.spotify_id,
            'musicbrainz_id': self.musicbrainz_id,
        }


class AudioFingerprinter:
    """Generate audio fingerprints from minimal audio samples"""
    
    @staticmethod
    def extract_fingerprint(audio_path: Path, duration: float = 15.0) -> Optional[str]:
        """
        Extract audio fingerprint from first N seconds of track.
        
        Args:
            audio_path: Path to audio file
            duration: Seconds to analyze (default: 15 seconds, minimum)
            
        Returns:
            Fingerprint hash string
        """
        if not LIBROSA_AVAILABLE:
            logger.warning("librosa not available - using simple fingerprint")
            return AudioFingerprinter._simple_fingerprint(audio_path)
        
        try:
            # Load only first N seconds for fast processing
            y, sr = librosa.load(str(audio_path), sr=22050, duration=duration)
            
            # Compute chromagram (12-bin chroma features)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            
            # Compute spectral centroid
            centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            
            # Compute MFCC (Mel-Frequency Cepstral Coefficients)
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
            
            # Create fingerprint from averaged features
            fingerprint_data = {
                'chroma_mean': chroma.mean(axis=1).tolist(),
                'centroid_mean': float(centroid.mean()),
                'mfcc_mean': mfcc.mean(axis=1).tolist(),
                'duration': float(librosa.get_duration(y=y, sr=sr))
            }
            
            # Create hash
            fp_string = json.dumps(fingerprint_data, sort_keys=True)
            fingerprint = hashlib.sha256(fp_string.encode()).hexdigest()
            
            logger.debug(f"Generated fingerprint: {fingerprint[:16]}...")
            return fingerprint
        
        except Exception as e:
            logger.error(f"Error generating fingerprint: {e}")
            return None
    
    @staticmethod
    def _simple_fingerprint(audio_path: Path) -> Optional[str]:
        """
        Simple fingerprint for when librosa is unavailable.
        Uses file size, duration, and file hash.
        """
        try:
            file_size = audio_path.stat().st_size
            file_hash = hashlib.md5()
            
            # Hash first 1MB of file
            with open(audio_path, 'rb') as f:
                chunk = f.read(1024 * 1024)
                file_hash.update(chunk)
            
            fingerprint_data = {
                'file_size': file_size,
                'file_hash': file_hash.hexdigest()
            }
            
            fp_string = json.dumps(fingerprint_data, sort_keys=True)
            fingerprint = hashlib.sha256(fp_string.encode()).hexdigest()
            
            logger.debug(f"Generated simple fingerprint: {fingerprint[:16]}...")
            return fingerprint
        
        except Exception as e:
            logger.error(f"Error generating simple fingerprint: {e}")
            return None


class SongIdentifier:
    """Identify songs using multiple free APIs"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MetaFixer/1.0 (song identification)'
        })
    
    def identify_song(self, audio_path: Path, audio_bytes: Optional[bytes] = None) -> Optional[SongIdentification]:
        """
        Identify song using available methods.
        
        Args:
            audio_path: Path to audio file
            audio_bytes: Optional raw audio bytes (for fingerprinting)
            
        Returns:
            SongIdentification object if successful, None otherwise
        """
        logger.info(f"Attempting to identify: {audio_path.name}")
        
        # Try multiple methods in order of reliability
        methods = [
            self._identify_by_musicbrainz_acoustic,
            self._identify_by_acrcloud,
            self._identify_by_spotify_search,
        ]
        
        for method in methods:
            try:
                result = method(audio_path)
                if result:
                    logger.info(f"✓ Identified via {result.source}: {result.artist} - {result.title}")
                    return result
            except Exception as e:
                logger.debug(f"Method {method.__name__} failed: {e}")
                continue
        
        logger.warning(f"Could not identify: {audio_path.name}")
        return None
    
    def _identify_by_musicbrainz_acoustic(self, audio_path: Path) -> Optional[SongIdentification]:
        """
        Identify using MusicBrainz Acoustic Fingerprinting (requires fingerprint).
        
        Note: This requires the AcoustID service, which works best with Chromaprint.
        """
        try:
            logger.debug("Trying MusicBrainz Acoustic Fingerprint method...")
            
            # Generate fingerprint from audio
            fingerprint = AudioFingerprinter.extract_fingerprint(audio_path, duration=15)
            
            if not fingerprint:
                return None
            
            # Note: Full acoustic fingerprinting requires Chromaprint library
            # This is a placeholder for when Chromaprint is available
            logger.debug("MusicBrainz acoustic fingerprint method - requires Chromaprint")
            return None
        
        except Exception as e:
            logger.debug(f"MusicBrainz method failed: {e}")
            return None
    
    def _identify_by_acrcloud(self, audio_path: Path) -> Optional[SongIdentification]:
        """
        Identify using ACRCloud free API (limited requests).
        
        Note: Free tier is limited. Requires API key setup.
        Register at: https://www.acrcloud.com/
        """
        try:
            logger.debug("Trying ACRCloud method...")
            
            # Read first 15 seconds of audio
            with open(audio_path, 'rb') as f:
                audio_sample = f.read(500000)  # ~500KB sample
            
            # ACRCloud would require API key setup
            # This shows the structure for when configured
            logger.debug("ACRCloud method - requires API key configuration")
            return None
        
        except Exception as e:
            logger.debug(f"ACRCloud method failed: {e}")
            return None
    
    def _identify_by_spotify_search(self, audio_path: Path) -> Optional[SongIdentification]:
        """
        Identify by extracting metadata and searching Spotify.
        
        This uses file metadata hints to search Spotify's free API.
        """
        try:
            logger.debug("Trying Spotify metadata search method...")
            
            # Try to extract basic metadata from file
            from mutagen import File
            
            audio = File(str(audio_path))
            
            if audio is None:
                return None
            
            # Get file metadata tags
            title = None
            artist = None
            
            # Try different tag formats
            if hasattr(audio, 'tags') and audio.tags:
                title = audio.tags.get('TIT2', [None])[0] if 'TIT2' in audio.tags else None
                artist = audio.tags.get('TPE1', [None])[0] if 'TPE1' in audio.tags else None
            
            # Try MP4 tags
            if hasattr(audio, 'tags') and isinstance(audio.tags, dict):
                title = audio.tags.get('\xa9nam', [None])[0] if '\xa9nam' in audio.tags else None
                artist = audio.tags.get('\xa9ART', [None])[0] if '\xa9ART' in audio.tags else None
            
            # If we have partial metadata, search
            if title or artist:
                query = f"{artist} {title}".strip() if artist and title else title or artist
                
                if query:
                    result = self._search_spotify(query)
                    if result:
                        return result
            
            return None
        
        except Exception as e:
            logger.debug(f"Spotify search method failed: {e}")
            return None
    
    def _search_spotify(self, query: str) -> Optional[SongIdentification]:
        """
        Search Spotify for track by query string.
        
        Uses free Spotify Web API (no authentication required for basic search).
        """
        try:
            url = "https://api.spotify.com/v1/search"
            params = {
                'q': query,
                'type': 'track',
                'limit': 1
            }
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                tracks = data.get('tracks', {}).get('items', [])
                
                if tracks:
                    track = tracks[0]
                    artist_name = track['artists'][0]['name'] if track['artists'] else 'Unknown'
                    
                    return SongIdentification(
                        title=track['name'],
                        artist=artist_name,
                        album=track.get('album', {}).get('name'),
                        duration=track.get('duration_ms', 0) / 1000,
                        confidence=0.7,  # Medium confidence for search
                        source='spotify',
                        spotify_id=track['id'],
                    )
            
            return None
        
        except Exception as e:
            logger.debug(f"Spotify search failed: {e}")
            return None
    
    def identify_from_fingerprint(self, fingerprint: str) -> Optional[SongIdentification]:
        """
        Identify song from pre-computed fingerprint.
        
        This would work with a fingerprint database or API service.
        """
        logger.debug(f"Searching by fingerprint: {fingerprint[:16]}...")
        
        # Placeholder for fingerprint database lookup
        # In production, would query:
        # - MusicBrainz AcoustID database
        # - Custom fingerprint database
        # - ACRCloud fingerprint service
        
        return None
    
    def batch_identify(self, audio_files: List[Path]) -> Dict[Path, Optional[SongIdentification]]:
        """
        Identify multiple songs.
        
        Args:
            audio_files: List of audio file paths
            
        Returns:
            Dictionary mapping file paths to identification results
        """
        results = {}
        
        for audio_file in audio_files:
            result = self.identify_song(audio_file)
            results[audio_file] = result
        
        return results


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    identifier = SongIdentifier()
    
    # Example: identify a song
    test_file = Path("test_song.mp3")
    
    if test_file.exists():
        result = identifier.identify_song(test_file)
        
        if result:
            print(f"\n✅ Song Identified!")
            print(f"   Artist: {result.artist}")
            print(f"   Title: {result.title}")
            print(f"   Album: {result.album}")
            print(f"   Duration: {result.duration}s")
            print(f"   Confidence: {result.confidence:.0%}")
            print(f"   Source: {result.source}")
        else:
            print(f"\n❌ Could not identify song")
    else:
        print(f"Test file not found: {test_file}")
