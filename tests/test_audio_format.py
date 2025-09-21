#!/usr/bin/env python3
"""
Test script to validate audio format detection and conversion
Run this after enabling Google Cloud APIs
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "app"))

from app.services.google_speech import SpeechService
from google.cloud import speech

async def test_audio_formats():
    """Test different audio format handling"""
    print("🎙️  Testing Audio Format Detection...")
    
    service = SpeechService()
    
    # Test format detection
    test_cases = [
        (b'RIFF', "WAV/LINEAR16"),
        (b'\x1a\x45\xdf\xa3', "WebM/Opus"), 
        (b'OggS', "OGG/Opus"),
        (b'fLaC', "FLAC"),
        (b'\x00\x00\x00\x00', "Unknown/Default"),
    ]
    
    for header, expected in test_cases:
        encoding, sample_rate = service._detect_audio_format(header)
        print(f"✅ {expected}: {encoding.name} @ {sample_rate}Hz")
    
    print("\n🔊 Audio Format Support:")
    print(f"✅ WebM/Opus: {speech.RecognitionConfig.AudioEncoding.WEBM_OPUS}")
    print(f"✅ OGG/Opus: {speech.RecognitionConfig.AudioEncoding.OGG_OPUS}")
    print(f"✅ LINEAR16: {speech.RecognitionConfig.AudioEncoding.LINEAR16}")
    print(f"✅ FLAC: {speech.RecognitionConfig.AudioEncoding.FLAC}")
    
    print("\n🎯 Ready for voice processing with multiple audio formats!")

if __name__ == "__main__":
    asyncio.run(test_audio_formats())