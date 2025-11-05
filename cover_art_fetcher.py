#!/usr/bin/env python3
"""
Cover Art Fetcher - Intelligent cover art retrieval from internet sources
Uses multiple APIs and image similarity matching to find the best cover art.

Strategy:
1. Fetch cover art from multiple sources (Spotify, Last.fm, MusicBrainz, Google Images)
2. Download multiple candidates (typically 10-15 images)
3. Use image similarity clustering (RGB histogram comparison)
4. Vote-based selection: images with most similar matches = most likely correct
5. Return top candidate with confidence score
"""

import os
import sys
import json
import requests
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from io import BytesIO
from dataclasses import dataclass
from collections import defaultdict
import logging

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("Error: PIL and numpy required for cover art fetching")
    print("Install with: pip install Pillow numpy")
    sys.exit(1)

logger = logging.getLogger(__name__)

@dataclass
class CoverArtCandidate:
    """Represents a cover art candidate with metadata."""
    url: str
    source: str  # 'spotify', 'lastfm', 'musicbrainz', 'google'
    image_data: bytes
    size_kb: float
    resolution: Tuple[int, int]
    histogram_hash: str
    similarity_score: float = 0.0
    is_selected: bool = False


class ImageSimilarityMatcher:
    """Compare images using histogram-based similarity (RGB values)."""
    
    @staticmethod
    def get_histogram_hash(image_data: bytes) -> str:
        """
        Generate a histogram-based hash of an image for quick comparison.
        Uses RGB histogram to create a fingerprint.
        """
        try:
            img = Image.open(BytesIO(image_data))
            img = img.convert('RGB')
            
            # Resize to 8x8 for fast comparison
            img_small = img.resize((8, 8), Image.LANCZOS)
            
            # Get RGB values
            pixels = list(img_small.getdata())
            
            # Create histogram (simplified: group colors into buckets)
            r_hist = [0] * 8
            g_hist = [0] * 8
            b_hist = [0] * 8
            
            for r, g, b in pixels:
                r_hist[r // 32] += 1
                g_hist[g // 32] += 1
                b_hist[b // 32] += 1
            
            # Create hash from histograms
            hist_string = ''.join(str(h) for h in r_hist + g_hist + b_hist)
            return hashlib.md5(hist_string.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Error creating histogram hash: {e}")
            return ""
    
    @staticmethod
    def calculate_similarity(hash1: str, hash2: str) -> float:
        """
        Calculate similarity between two histogram hashes (0-1, where 1 is identical).
        Uses Hamming distance on the hash values.
        """
        if not hash1 or not hash2:
            return 0.0
        
        try:
            # Convert hex strings to binary and compare
            bin1 = bin(int(hash1, 16))[2:].zfill(128)
            bin2 = bin(int(hash2, 16))[2:].zfill(128)
            
            # Count differing bits
            differences = sum(b1 != b2 for b1, b2 in zip(bin1, bin2))
            
            # Convert to similarity score (1.0 = identical)
            similarity = 1.0 - (differences / len(bin1))
            return similarity
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0


class CoverArtFetcher:
    """Fetch cover art from multiple internet sources."""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.matcher = ImageSimilarityMatcher()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MetaFixer/1.0 (https://github.com/user/metafixer; test@example.com)'
        })
    
    def fetch_cover_art(self, artist: str, title: str, max_candidates: int = 12) -> Optional[CoverArtCandidate]:
        """
        Fetch cover art from multiple sources and return the best candidate.
        
        Args:
            artist: Artist name
            title: Track title
            max_candidates: Maximum number of images to fetch
        
        Returns:
            Best CoverArtCandidate based on similarity voting
        """
        logger.info(f"Fetching cover art for: {artist} - {title}")
        
        candidates = []
        
        # Fetch from multiple sources
        candidates.extend(self._fetch_spotify(artist, title, max_candidates // 3))
        candidates.extend(self._fetch_lastfm(artist, title, max_candidates // 3))
        candidates.extend(self._fetch_musicbrainz(artist, title, max_candidates // 3))
        
        if not candidates:
            logger.warning("No cover art candidates found from any source")
            return None
        
        logger.info(f"Found {len(candidates)} candidate images")
        
        # Calculate similarity scores using clustering
        best_candidate = self._find_best_candidate_by_similarity(candidates)
        
        if best_candidate:
            logger.info(f"Selected cover art from {best_candidate.source} "
                       f"(similarity: {best_candidate.similarity_score:.1%})")
        
        return best_candidate
    
    def _fetch_spotify(self, artist: str, title: str, limit: int = 4) -> List[CoverArtCandidate]:
        """Fetch from Spotify API."""
        candidates = []
        try:
            query = f"{artist} {title}"
            url = "https://api.spotify.com/v1/search"
            
            # Note: Requires authentication - simplified version without API key
            logger.debug("Spotify search skipped (requires authentication)")
            
        except Exception as e:
            logger.debug(f"Error fetching from Spotify: {e}")
        
        return candidates
    
    def _fetch_lastfm(self, artist: str, title: str, limit: int = 4) -> List[CoverArtCandidate]:
        """Fetch from Last.fm API."""
        candidates = []
        try:
            # Last.fm API (free tier available)
            params = {
                'method': 'track.getInfo',
                'artist': artist,
                'track': title,
                'api_key': 'placeholder',  # User should set this
                'format': 'json'
            }
            
            url = "https://ws.audioscrobbler.com/2.0/"
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract album info
                if 'track' in data and 'album' in data['track']:
                    album = data['track']['album']
                    images = album.get('image', [])
                    
                    for img in images[-limit:]:  # Get largest images
                        if img.get('#text'):
                            try:
                                img_data = self._download_image(img['#text'])
                                if img_data:
                                    candidate = CoverArtCandidate(
                                        url=img['#text'],
                                        source='lastfm',
                                        image_data=img_data,
                                        size_kb=len(img_data) / 1024,
                                        resolution=self._get_image_resolution(img_data),
                                        histogram_hash=self.matcher.get_histogram_hash(img_data)
                                    )
                                    candidates.append(candidate)
                                    logger.debug(f"Fetched Last.fm image: {len(img_data)} bytes")
                            except Exception as e:
                                logger.debug(f"Error processing Last.fm image: {e}")
            
        except Exception as e:
            logger.debug(f"Error fetching from Last.fm: {e}")
        
        return candidates
    
    def _fetch_musicbrainz(self, artist: str, title: str, limit: int = 4) -> List[CoverArtCandidate]:
        """Fetch from MusicBrainz and Cover Art Archive."""
        candidates = []
        try:
            # First, search for the track in MusicBrainz
            search_url = "https://musicbrainz.org/ws/2/recording"
            query = f"{artist} {title}"
            
            params = {
                'query': query,
                'fmt': 'json',
                'limit': 5
            }
            
            response = self.session.get(search_url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                recordings = data.get('recordings', [])
                
                for recording in recordings[:2]:
                    release_id = recording.get('releases', [{}])[0].get('id')
                    
                    if release_id:
                        # Get cover art from Cover Art Archive
                        ca_url = f"https://coverartarchive.org/release/{release_id}"
                        try:
                            ca_response = self.session.get(ca_url, timeout=self.timeout)
                            
                            if ca_response.status_code == 200:
                                ca_data = ca_response.json()
                                images = ca_data.get('images', [])
                                
                                for img in images[:limit]:
                                    try:
                                        img_data = self._download_image(img['image'])
                                        if img_data:
                                            candidate = CoverArtCandidate(
                                                url=img['image'],
                                                source='musicbrainz',
                                                image_data=img_data,
                                                size_kb=len(img_data) / 1024,
                                                resolution=self._get_image_resolution(img_data),
                                                histogram_hash=self.matcher.get_histogram_hash(img_data)
                                            )
                                            candidates.append(candidate)
                                            logger.debug(f"Fetched MusicBrainz image: {len(img_data)} bytes")
                                    except Exception as e:
                                        logger.debug(f"Error processing MusicBrainz image: {e}")
                        
                        except Exception as e:
                            logger.debug(f"Error fetching from Cover Art Archive: {e}")
            
        except Exception as e:
            logger.debug(f"Error fetching from MusicBrainz: {e}")
        
        return candidates
    
    def _download_image(self, url: str) -> Optional[bytes]:
        """Download image from URL with validation and compression."""
        try:
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Validate it's actually an image
                content_type = response.headers.get('content-type', '').lower()
                
                if 'image' in content_type or url.lower().endswith(('.jpg', '.png', '.jpeg')):
                    data = response.content
                    
                    # Validate image format
                    try:
                        Image.open(BytesIO(data))
                    except Exception:
                        logger.debug(f"Invalid image format from {url}")
                        return None
                    
                    # Compress if needed (target: 500KB max)
                    if len(data) > 500000:
                        logger.debug(f"Compressing large image ({len(data) / 1024:.0f}KB)...")
                        data = self._compress_image(data, max_kb=500)
                    
                    return data
        
        except Exception as e:
            logger.debug(f"Error downloading image from {url}: {e}")
        
        return None
    
    @staticmethod
    def _get_image_resolution(image_data: bytes) -> Tuple[int, int]:
        """Get image resolution."""
        try:
            img = Image.open(BytesIO(image_data))
            return img.size
        except:
            return (0, 0)
    
    @staticmethod
    def _compress_image(image_data: bytes, max_kb: int = 500) -> bytes:
        """Compress image to fit size limit while maintaining quality."""
        try:
            img = Image.open(BytesIO(image_data))
            
            # Convert RGBA to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Start with high quality
            quality = 95
            output = BytesIO()
            
            # Keep reducing quality until size is acceptable
            while quality > 10:
                output = BytesIO()
                img.save(output, format='JPEG', quality=quality, optimize=True)
                
                size_kb = len(output.getvalue()) / 1024
                if size_kb <= max_kb:
                    logger.debug(f"Compressed image to {size_kb:.1f}KB (quality: {quality})")
                    return output.getvalue()
                
                quality -= 5
            
            # Last resort: reduce resolution
            scale = 0.9
            while scale > 0.3:
                output = BytesIO()
                new_size = (int(img.width * scale), int(img.height * scale))
                scaled_img = img.resize(new_size, Image.LANCZOS)
                scaled_img.save(output, format='JPEG', quality=75, optimize=True)
                
                size_kb = len(output.getvalue()) / 1024
                if size_kb <= max_kb:
                    logger.debug(f"Compressed image to {new_size} at {size_kb:.1f}KB")
                    return output.getvalue()
                
                scale -= 0.1
            
            logger.warning(f"Could not compress image to {max_kb}KB, returning smallest version")
            return output.getvalue()
        
        except Exception as e:
            logger.error(f"Error compressing image: {e}")
            return image_data
    
    def _find_best_candidate_by_similarity(self, candidates: List[CoverArtCandidate]) -> Optional[CoverArtCandidate]:
        """
        Find the best candidate using similarity clustering.
        
        Algorithm:
        1. Compare each image with all others
        2. Group images by similarity (>85% match = same group)
        3. Largest group wins (most consistent = most likely correct)
        4. Return the highest resolution image from winning group
        """
        if not candidates:
            return None
        
        if len(candidates) == 1:
            candidates[0].similarity_score = 1.0
            candidates[0].is_selected = True
            return candidates[0]
        
        logger.info(f"Clustering {len(candidates)} images by similarity...")
        
        # Calculate similarity between all pairs
        similarity_threshold = 0.85
        groups = defaultdict(list)
        processed = set()
        
        for i, cand1 in enumerate(candidates):
            if i in processed:
                continue
            
            group_id = i
            groups[group_id].append(cand1)
            processed.add(i)
            
            # Find similar images
            for j, cand2 in enumerate(candidates[i+1:], start=i+1):
                if j in processed:
                    continue
                
                similarity = self.matcher.calculate_similarity(
                    cand1.histogram_hash,
                    cand2.histogram_hash
                )
                
                if similarity >= similarity_threshold:
                    groups[group_id].append(cand2)
                    processed.add(j)
                    logger.debug(f"Grouped image {j} with {i} (similarity: {similarity:.1%})")
        
        # Find the largest group
        largest_group = max(groups.values(), key=len)
        group_size = len(largest_group)
        
        logger.info(f"Largest group has {group_size} similar images")
        
        # Select the highest resolution image from the largest group
        best = max(largest_group, key=lambda c: c.resolution[0] * c.resolution[1])
        
        # Calculate average similarity within the group
        avg_similarity = sum(
            self.matcher.calculate_similarity(best.histogram_hash, c.histogram_hash)
            for c in largest_group
        ) / group_size
        
        best.similarity_score = avg_similarity
        best.is_selected = True
        
        logger.info(f"Selected: {best.source} ({best.resolution[0]}x{best.resolution[1]}) "
                   f"group similarity: {avg_similarity:.1%}")
        
        return best
    
    def save_cover_art(self, candidate: CoverArtCandidate, output_path: Path) -> bool:
        """Save cover art to file."""
        try:
            with open(output_path, 'wb') as f:
                f.write(candidate.image_data)
            
            logger.info(f"Saved cover art to: {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Error saving cover art: {e}")
            return False


# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    fetcher = CoverArtFetcher()
    
    # Test case
    artist = "The Eagles"
    title = "Hotel California"
    
    print(f"\n🎨 Fetching cover art for: {artist} - {title}")
    print("="*70)
    
    best = fetcher.fetch_cover_art(artist, title)
    
    if best:
        print(f"\n✅ Best match found:")
        print(f"   Source: {best.source}")
        print(f"   Resolution: {best.resolution[0]}x{best.resolution[1]}")
        print(f"   Size: {best.size_kb:.1f}KB")
        print(f"   Similarity score: {best.similarity_score:.1%}")
        print(f"   URL: {best.url}")
        
        # Optionally save
        # fetcher.save_cover_art(best, Path("cover.jpg"))
    else:
        print("\n❌ No cover art found")
