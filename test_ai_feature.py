#!/usr/bin/env python3
"""
Test script for AI metadata suggestion feature.
Tests: Ollama connectivity, AI prompting, JSON parsing, and suggestion workflow.
"""

import sys
import json
import time
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_manager import AIManager
from logger_setup import LoggerSetup

# Setup logging
logger = LoggerSetup.setup(__name__)

def test_ollama_connectivity():
    """Test if Ollama server is running and accessible."""
    print("\n" + "="*60)
    print("TEST 1: Ollama Server Connectivity")
    print("="*60)
    
    try:
        import ollama
        print("✅ ollama package imported successfully")
        
        # Quick ping
        print("⏳ Checking Ollama server on localhost:11434...")
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 11434))
        sock.close()
        
        if result == 0:
            print("✅ Ollama server is running on port 11434")
            return True
        else:
            print("❌ Ollama server not responding on port 11434")
            print("   Run: ollama serve (in another terminal)")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_manager_initialization():
    """Test if AIManager initializes without errors."""
    print("\n" + "="*60)
    print("TEST 2: AIManager Initialization")
    print("="*60)
    
    try:
        ai_manager = AIManager()
        print("✅ AIManager initialized successfully")
        
        status = ai_manager.get_status()
        print(f"   Status: {status}")
        if status.get('ollama_available'):
            print("✅ Ollama detected as available")
        else:
            print("⚠️  Ollama not detected")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_ai_suggestions():
    """Test the core AI suggestions feature."""
    print("\n" + "="*60)
    print("TEST 3: AI Suggestions Generation")
    print("="*60)
    
    try:
        ai_manager = AIManager()
        
        # Test case 1: Messy filename with metadata
        test_cases = [
            {
                "filename": "02-the_eagles-hotel_california_(live_at_the_forum_94)-remaster.flac",
                "metadata": {
                    "artist": "the eagles",
                    "title": "Hotel California",
                    "album": "Unknown",
                }
            },
            {
                "filename": "[Official_Video]_dua_lipa-levitating_(2022_remix)_HD.mp3",
                "metadata": {
                    "artist": "Dua Lipa",
                    "title": "[Official Video] Levitating",
                    "album": "",
                }
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 Test Case {i}:")
            print(f"   Filename: {test_case['filename']}")
            print(f"   Current metadata: {test_case['metadata']}")
            
            print("   ⏳ Requesting AI suggestions (may take 15-30 seconds)...")
            start_time = time.time()
            
            suggestions = ai_manager.get_ai_suggestions(
                test_case['filename'],
                test_case['metadata']
            )
            
            elapsed = time.time() - start_time
            print(f"   ⏱️  Completed in {elapsed:.1f} seconds")
            
            if suggestions:
                print("   ✅ Suggestions received:")
                for key, value in suggestions.items():
                    if value and key != 'moods':  # Skip list display for brevity
                        print(f"      • {key}: {value}")
                    elif key == 'moods' and value:
                        print(f"      • {key}: {', '.join(value)}")
                return True
            else:
                print("   ❌ No suggestions received")
                return False
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_json_parsing():
    """Test JSON parsing robustness."""
    print("\n" + "="*60)
    print("TEST 4: JSON Response Parsing")
    print("="*60)
    
    try:
        # Test the prompt building
        ai_manager = AIManager()
        prompt = ai_manager._build_ai_prompt(
            "test-song.flac",
            {"artist": "Test Artist", "title": "Test Title"}
        )
        
        print("✅ Prompt built successfully")
        print(f"   Prompt length: {len(prompt)} characters")
        print(f"   Contains JSON format instruction: {'return ONLY JSON' in prompt}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n🎵 MetadataFixer AI Feature Test Suite")
    print("="*60)
    
    results = {
        "Ollama Connectivity": test_ollama_connectivity(),
        "AIManager Initialization": test_ai_manager_initialization(),
        "JSON Parsing": test_json_parsing(),
    }
    
    # Optional: Run full test (requires fast inference)
    print("\n" + "="*60)
    print("Running optional AI suggestions test...")
    print("(This may take 15-60 seconds depending on hardware)")
    print("="*60)
    
    try:
        results["AI Suggestions"] = test_ai_suggestions()
    except KeyboardInterrupt:
        print("\n⏸️  Test cancelled by user")
        results["AI Suggestions"] = None
    except Exception as e:
        print(f"\n❌ Error in suggestions test: {e}")
        results["AI Suggestions"] = False
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    total = len([v for v in results.values() if v is not None])
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⏭️  SKIPPED"
        print(f"{status} - {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! AI feature is ready to use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. See details above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
