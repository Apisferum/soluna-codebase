"""
Manual smoke test for Chord AI and the Stem/Voice Separator.

Run this against a live server after starting the unified backend:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

This hits real endpoints (including a real Demucs separation), so it is
not part of the automated pytest suite in tests/ — run it by hand before
a deploy if you want an end-to-end sanity check with a real audio file.
"""

import requests
import sys
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_AUDIO = "test_audio.wav"  # Using the generated test file

def test_health():
    """Test if backend is running"""
    print("\n🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/health")
        if response.status_code == 200:
            print("✅ Backend is running")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to backend at {BACKEND_URL}")
        print("   Make sure you run: npm run dev:backend")
        return False

def test_chord_analysis():
    """Test the Chord AI feature (without vocal separation)"""
    print("\n🎸 Testing Chord AI (without vocal separation)...")
    
    if not Path(TEST_AUDIO).exists():
        print(f"⚠️  Test audio file not found: {TEST_AUDIO}")
        print("   Update TEST_AUDIO in this script with a valid audio file path")
        return False
    
    try:
        with open(TEST_AUDIO, "rb") as f:
            files = {"file": f}
            data = {"separate_vocals": "false"}
            response = requests.post(f"{BACKEND_URL}/api/audio/analyze", files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chord AI works!")
            print(f"   Tempo: {result.get('tempo')} BPM")
            print(f"   Key: {result.get('key')} {result.get('scale')}")
            print(f"   Chords detected: {len(result.get('chords', []))}")
            return True
        else:
            print(f"❌ Chord AI failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Chord AI error: {str(e)}")
        return False

def test_vocal_separation():
    """Test the Vocal Splitter feature"""
    print("\n🎤 Testing Vocal Splitter...")
    
    if not Path(TEST_AUDIO).exists():
        print(f"⚠️  Test audio file not found: {TEST_AUDIO}")
        return False
    
    try:
        with open(TEST_AUDIO, "rb") as f:
            files = {"file": f}
            data = {"format": "mp3"}
            print("   (This will take 1-3 minutes for Demucs processing...)")
            response = requests.post(
                f"{BACKEND_URL}/api/audio/separate", 
                files=files, 
                data=data,
                timeout=300  # 5 minute timeout
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Vocal Splitter works!")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Format: {result.get('format')}")
            print(f"   Vocals URL: {result.get('vocalsUrl')}")
            print(f"   Instrumental URL: {result.get('instrumentalUrl')}")
            
            # Test downloading one of the stems
            print("\n   Testing stem download...")
            vocals_url = f"{BACKEND_URL}{result.get('vocalsUrl')}"
            dl_response = requests.head(vocals_url)
            if dl_response.status_code == 200:
                print("   ✅ Stem downloads work!")
            else:
                print(f"   ⚠️  Stem download returned {dl_response.status_code}")
            
            return True
        else:
            print(f"❌ Vocal Splitter failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Vocal Splitter timed out (processing takes too long)")
        print("   This might be normal for large files")
        return False
    except Exception as e:
        print(f"❌ Vocal Splitter error: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("Soluna Backend Feature Test")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        sys.exit(1)
    
    # Test 2: Chord AI
    chord_works = test_chord_analysis()
    
    # Test 3: Vocal Splitter
    vocal_works = test_vocal_separation()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    print("✅ Backend Running: Yes")
    print(f"{'✅' if chord_works else '❌'} Chord AI: {'Working' if chord_works else 'Failed'}")
    print(f"{'✅' if vocal_works else '❌'} Vocal Splitter: {'Working' if vocal_works else 'Failed'}")
    print()
    
    if chord_works and vocal_works:
        print("🎉 All features are working! Safe to deploy.")
        sys.exit(0)
    elif chord_works:
        print("⚠️  Chord AI works but Vocal Splitter has issues.")
        print("   Your production deployment might have problems with vocal separation.")
        sys.exit(1)
    else:
        print("❌ Critical issues found. Do not deploy yet.")
        sys.exit(1)

if __name__ == "__main__":
    main()
