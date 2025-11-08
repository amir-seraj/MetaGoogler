#!/usr/bin/env python3
"""
Batch Music Library Processor
Identify, fill metadata, download cover art, and apply AI refinements
"""

import sys
from pathlib import Path
from song_metadata_fixer_v2 import SongMetadataFixer
from typing import List, Dict, Tuple
import argparse
from datetime import datetime

class BatchProcessor:
    """Process entire music library with identification + AI + cover art"""
    
    def __init__(self, music_dir: Path = None, dry_run: bool = False):
        self.fixer = SongMetadataFixer()
        self.music_dir = music_dir or Path.cwd()
        self.dry_run = dry_run
        
        self.stats = {
            'total': 0,
            'identified': 0,
            'metadata_filled': 0,
            'cover_embedded': 0,
            'ai_applied': 0,
            'failed': 0,
            'skipped': 0,
        }
    
    def find_audio_files(self) -> List[Path]:
        """Find all audio files in music directory"""
        
        audio_extensions = ('*.mp3', '*.m4a', '*.flac', '*.wav', '*.ogg')
        files = []
        
        print(f"🔍 Scanning for audio files in: {self.music_dir}")
        
        for ext in audio_extensions:
            files.extend(self.music_dir.glob(f"**/{ext}"))
        
        print(f"   Found {len(files)} audio files\n")
        return sorted(files)
    
    def process_file(self, file_path: Path, with_ai: bool = True, 
                     with_cover: bool = True) -> Dict:
        """Process single file with full workflow"""
        
        result = {
            'file': file_path.name,
            'identified': False,
            'metadata_filled': False,
            'cover_embedded': False,
            'ai_applied': False,
            'errors': []
        }
        
        try:
            # Step 1: Identify song
            print(f"  → Identifying: {file_path.name}")
            identified = self.fixer.identify_song(file_path)
            
            if identified:
                result['identified'] = True
                self.stats['identified'] += 1
                print(f"    ✓ Found: {identified.get('artist')} - {identified.get('title')}")
            
            # Step 2: Fill missing metadata
            print(f"  → Filling metadata...")
            fill_result = self.fixer.identify_and_fill_metadata(
                file_path,
                overwrite_existing=False
            )
            
            if fill_result.success:
                result['metadata_filled'] = True
                self.stats['metadata_filled'] += 1
                print(f"    ✓ Metadata updated")
            
            # Get current metadata
            metadata = self.fixer.get_metadata(file_path)
            
            # Step 3: Apply AI refinements
            if with_ai and metadata:
                try:
                    print(f"  → Getting AI suggestions...")
                    suggestions = self.fixer.ai_manager.get_ai_suggestions(
                        file_path.name,
                        metadata
                    )
                    
                    if suggestions:
                        result['ai_applied'] = True
                        self.stats['ai_applied'] += 1
                        print(f"    ✓ AI suggestions: {suggestions.get('genre', 'N/A')}")
                        
                        # Apply suggestions if not in dry_run
                        if not self.dry_run:
                            # Valid metadata fields only
                            valid_fields = {'title', 'artist', 'album', 'date', 'genre', 'tracknumber'}
                            
                            # Merge suggestions into metadata
                            for key, value in suggestions.items():
                                # Only apply valid fields, skip AI-specific fields
                                if key in valid_fields and value:
                                    if metadata.get(key) in ('Unknown', 'N/A', '', None):
                                        metadata[key] = str(value)
                            
                            # Save updated metadata
                            self.fixer.set_metadata(file_path, metadata)
                except ImportError:
                    print(f"    → Ollama not available (skipping AI)")
                except Exception as e:
                    result['errors'].append(f"AI error: {str(e)}")
            
            # Step 4: Download and embed cover art
            if with_cover and metadata:
                try:
                    print(f"  → Downloading cover art...")
                    artist = metadata.get('artist', 'Unknown')
                    title = metadata.get('title', 'Unknown')
                    
                    cover_bytes = self.fixer.download_cover_art_from_internet(
                        artist, title
                    )
                    
                    if cover_bytes and not self.dry_run:
                        embed_result = self.fixer.embed_cover_art_bytes(
                            file_path,
                            cover_bytes
                        )
                        
                        if embed_result.success:
                            result['cover_embedded'] = True
                            self.stats['cover_embedded'] += 1
                            print(f"    ✓ Cover art embedded ({len(cover_bytes)//1024}KB)")
                    elif cover_bytes:
                        result['cover_embedded'] = True
                        print(f"    ✓ Cover art ready (dry-run, not writing)")
                
                except Exception as e:
                    result['errors'].append(f"Cover error: {str(e)}")
            
            print(f"  ✓ {file_path.name}\n")
            
        except Exception as e:
            result['errors'].append(str(e))
            print(f"  ✗ Error: {str(e)}\n")
            self.stats['failed'] += 1
        
        return result
    
    def process_batch(self, files: List[Path], with_ai: bool = True,
                     with_cover: bool = True, max_files: int = None) -> None:
        """Process multiple files"""
        
        if max_files:
            files = files[:max_files]
        
        self.stats['total'] = len(files)
        
        print(f"\n{'='*80}")
        print(f"BATCH PROCESSING: {len(files)} files")
        print(f"{'='*80}\n")
        
        if self.dry_run:
            print("⚠️  DRY-RUN MODE - No files will be modified\n")
        
        results = []
        
        for idx, file_path in enumerate(files, 1):
            print(f"[{idx}/{len(files)}] Processing: {file_path.name}")
            result = self.process_file(file_path, with_ai=with_ai, 
                                      with_cover=with_cover)
            results.append(result)
        
        # Print summary
        self.print_summary()
        
        return results
    
    def print_summary(self) -> None:
        """Print processing summary"""
        
        print(f"\n{'='*80}")
        print(f"PROCESSING COMPLETE")
        print(f"{'='*80}\n")
        
        print(f"📊 Summary:")
        print(f"  Total files:        {self.stats['total']}")
        print(f"  ✓ Identified:       {self.stats['identified']} "
              f"({self.stats['identified']/max(self.stats['total'], 1)*100:.0f}%)")
        print(f"  ✓ Metadata filled:  {self.stats['metadata_filled']}")
        print(f"  ✓ Cover embedded:   {self.stats['cover_embedded']}")
        print(f"  ✓ AI applied:       {self.stats['ai_applied']}")
        print(f"  ✗ Failed:           {self.stats['failed']}")
        
        print(f"\n💾 Next Steps:")
        print(f"  1. Review updated metadata in files")
        print(f"  2. Check cover art embeddings")
        print(f"  3. Verify AI suggestions")
        print(f"  4. Use GUI to manually review/adjust")


def main():
    """Command-line interface for batch processor"""
    
    parser = argparse.ArgumentParser(
        description="Batch process music library with identification + AI + cover art"
    )
    
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path.cwd(),
        help="Music directory to process (default: current directory)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )
    
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Maximum number of files to process"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Skip AI refinement step"
    )
    
    parser.add_argument(
        "--no-cover",
        action="store_true",
        help="Skip cover art downloading"
    )
    
    args = parser.parse_args()
    
    # Create processor
    processor = BatchProcessor(
        music_dir=args.dir,
        dry_run=args.dry_run
    )
    
    # Find files
    files = processor.find_audio_files()
    
    if not files:
        print("❌ No audio files found!")
        sys.exit(1)
    
    # Process batch
    processor.process_batch(
        files,
        with_ai=not args.no_ai,
        with_cover=not args.no_cover,
        max_files=args.max_files
    )


if __name__ == "__main__":
    main()
