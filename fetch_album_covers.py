#!/usr/bin/env python3
"""
Fetch real album covers from online sources and apply to music files
Supports: Spotify, MusicBrainz, Last.fm, and other sources
"""

import requests
import json
from pathlib import Path
from typing import Optional, Tuple
from io import BytesIO
from PIL import Image
import time

class AlbumCoverFetcher:
    """Fetches album covers from various sources"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def log(self, msg: str):
        if self.verbose:
            print(f"[COVER] {msg}")
    
    def fetch_from_musicbrainz(self, artist: str, album: str) -> Optional[bytes]:
        """Fetch album cover from MusicBrainz API"""
        try:
            # Search for release
            search_url = "https://musicbrainz.org/ws/2/release"
            params = {
                'query': f'artist:"{artist}" release:"{album}"',
                'fmt': 'json'
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('releases'):
                self.log(f"No MusicBrainz result for {artist} - {album}")
                return None
            
            # Get first release
            release = data['releases'][0]
            release_id = release['id']
            
            # Fetch cover art from Cover Art Archive
            cover_url = f"https://coverartarchive.org/release/{release_id}/front-250.jpg"
            response = self.session.get(cover_url, timeout=5)
            
            if response.status_code == 200:
                self.log(f"✓ Found cover on MusicBrainz: {artist} - {album}")
                return response.content
            
            return None
        except Exception as e:
            self.log(f"MusicBrainz error for {artist} - {album}: {e}")
            return None
    
    def fetch_from_spotify(self, artist: str, album: str) -> Optional[bytes]:
        """Fetch album cover from Spotify API"""
        try:
            # Search for album
            search_url = "https://api.spotify.com/v1/search"
            params = {
                'q': f'artist:{artist} album:{album}',
                'type': 'album',
                'limit': 1
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            items = data.get('albums', {}).get('items', [])
            if not items:
                self.log(f"No Spotify result for {artist} - {album}")
                return None
            
            album_data = items[0]
            images = album_data.get('images', [])
            
            if not images:
                return None
            
            # Get highest resolution image
            image_url = images[0]['url']
            response = self.session.get(image_url, timeout=5)
            
            if response.status_code == 200:
                self.log(f"✓ Found cover on Spotify: {artist} - {album}")
                return response.content
            
            return None
        except Exception as e:
            self.log(f"Spotify error for {artist} - {album}: {e}")
            return None
    
    def fetch_from_lastfm(self, artist: str, album: str, api_key: str = None) -> Optional[bytes]:
        """Fetch album cover from Last.fm API"""
        try:
            # Use a public Last.fm method (no API key needed for basic info)
            search_url = "https://www.last.fm/music/search"
            params = {
                'q': f'{artist} {album}'
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            
            # Parse for image URLs
            import re
            img_pattern = r'https://[^\s"<>]+?\.(?:jpg|png)'
            matches = re.findall(img_pattern, response.text)
            
            if not matches:
                self.log(f"No Last.fm images for {artist} - {album}")
                return None
            
            # Try to fetch the image
            for img_url in matches:
                if any(x in img_url for x in ['avatar', 'user', 'placeholder']):
                    continue
                try:
                    img_response = self.session.get(img_url, timeout=5)
                    if img_response.status_code == 200:
                        self.log(f"✓ Found cover on Last.fm: {artist} - {album}")
                        return img_response.content
                except:
                    continue
            
            return None
        except Exception as e:
            self.log(f"Last.fm error for {artist} - {album}: {e}")
            return None
    
    def fetch_from_itunes(self, artist: str, album: str) -> Optional[bytes]:
        """Fetch album cover from iTunes API"""
        try:
            search_url = "https://itunes.apple.com/search"
            params = {
                'term': f'{artist} {album}',
                'entity': 'album',
                'limit': 1
            }
            
            response = self.session.get(search_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('results', [])
            if not results:
                self.log(f"No iTunes result for {artist} - {album}")
                return None
            
            album_data = results[0]
            artwork_url = album_data.get('artworkUrl600') or album_data.get('artworkUrl100')
            
            if not artwork_url:
                return None
            
            response = self.session.get(artwork_url, timeout=5)
            if response.status_code == 200:
                self.log(f"✓ Found cover on iTunes: {artist} - {album}")
                return response.content
            
            return None
        except Exception as e:
            self.log(f"iTunes error for {artist} - {album}: {e}")
            return None
    
    def fetch_cover(self, artist: str, album: str) -> Optional[bytes]:
        """Fetch album cover from multiple sources in order of preference"""
        if not artist or not album:
            self.log(f"Missing artist or album: {artist} - {album}")
            return None
        
        # Try sources in order
        sources = [
            ('MusicBrainz', self.fetch_from_musicbrainz),
            ('iTunes', self.fetch_from_itunes),
            ('Spotify', self.fetch_from_spotify),
            ('Last.fm', self.fetch_from_lastfm),
        ]
        
        for source_name, fetch_func in sources:
            cover_data = fetch_func(artist, album)
            if cover_data:
                return cover_data
            time.sleep(0.5)  # Rate limiting
        
        self.log(f"✗ Could not find cover for {artist} - {album}")
        return None
    
    def validate_cover(self, cover_data: bytes) -> Tuple[bool, Optional[str]]:
        """Validate cover image"""
        try:
            img = Image.open(BytesIO(cover_data))
            
            # Check format
            if img.format not in ['JPEG', 'PNG', 'GIF', 'BMP']:
                return False, f"Invalid format: {img.format}"
            
            # Check size
            if img.size[0] < 200 or img.size[1] < 200:
                return False, f"Too small: {img.size}"
            
            if img.size[0] > 3000 or img.size[1] > 3000:
                return False, f"Too large: {img.size}"
            
            # Check file size
            if len(cover_data) > 5 * 1024 * 1024:  # 5MB
                return False, "File too large"
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    def fetch_and_validate(self, artist: str, album: str) -> Optional[bytes]:
        """Fetch cover and validate it"""
        cover_data = self.fetch_cover(artist, album)
        if not cover_data:
            return None
        
        is_valid, error = self.validate_cover(cover_data)
        if not is_valid:
            self.log(f"Invalid cover for {artist} - {album}: {error}")
            return None
        
        return cover_data


def apply_covers_to_music(music_dir: str = "music"):
    """Apply fetched covers to all music files"""
    from song_metadata_fixer import SongMetadataFixer
    
    print("="*70)
    print("FETCHING & APPLYING REAL ALBUM COVERS")
    print("="*70)
    
    fetcher = AlbumCoverFetcher(verbose=True)
    fixer = SongMetadataFixer(verbose=False)
    
    music_path = Path(music_dir)
    success_count = 0
    fail_count = 0
    
    for file in sorted(music_path.glob("*")):
        if not file.is_file() or not fixer.is_supported_format(file):
            continue
        
        if fixer._is_file_corrupted(file):
            print(f"⚠️  Skipping corrupted: {file.name}")
            continue
        
        metadata = fixer.get_metadata(file)
        if not metadata:
            print(f"✗ Cannot read metadata: {file.name}")
            fail_count += 1
            continue
        
        artist = metadata.get('artist', 'Unknown')
        album = metadata.get('album', 'Unknown')
        title = metadata.get('title', file.stem)
        
        print(f"\n📀 {title}")
        print(f"   {artist} - {album}")
        
        # Fetch cover
        cover_data = fetcher.fetch_and_validate(artist, album)
        if not cover_data:
            print(f"   ✗ Could not fetch cover")
            fail_count += 1
            continue
        
        # Save temp cover file
        temp_cover = Path("/tmp/cover_art_temp.jpg")
        temp_cover.write_bytes(cover_data)
        
        # Apply to music file
        if fixer.embed_cover_art(file, temp_cover):
            print(f"   ✓ Cover applied!")
            success_count += 1
        else:
            print(f"   ✗ Failed to apply cover")
            fail_count += 1
        
        temp_cover.unlink()
        time.sleep(1)  # Respectful rate limiting
    
    print("\n" + "="*70)
    print(f"✓ Success: {success_count} files")
    print(f"✗ Failed:  {fail_count} files")
    print("="*70)


if __name__ == "__main__":
    apply_covers_to_music()
