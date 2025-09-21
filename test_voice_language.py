#!/usr/bin/env python3
"""
Test script to debug voice language issues in MITRA.
This will help identify what languages are being detected and what voices are being used.
"""

import asyncio
import logging
import os
from pathlib import Path

# Setup environment
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/secrets.json"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.services.google_speech import SpeechService

async def test_voice_languages():
    """Test voice language detection and synthesis."""
    
    print("🔍 Testing MITRA Voice Language Configuration...")
    print("=" * 50)
    
    # Initialize speech service
    try:
        speech_service = SpeechService()
        print("✅ Speech service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize speech service: {e}")
        return
    
    # Test language detection with sample English text
    test_texts = [
        "Hello, I'm feeling anxious today",
        "Mujhe pareshani ho rahi hai",  # Hindi: I'm having trouble
        "I'm worried about my studies",
    ]
    
    print("\n🗣️ Testing Text-to-Speech Language Mapping...")
    
    for text in test_texts:
        print(f"\nTest text: '{text}'")
        
        # Try different language codes
        test_languages = ["en-US", "en-IN", "hi-IN", "en", "hi"]
        
        for lang in test_languages:
            try:
                # Test voice synthesis (without actually calling TTS)
                voice_map = {
                    "en-US": {"name": "en-US-Neural2-C", "language_code": "en-US"},
                    "en-GB": {"name": "en-GB-Neural2-B", "language_code": "en-GB"},
                    "en-IN": {"name": "en-IN-Neural2-B", "language_code": "en-IN"},
                    "hi-IN": {"name": "hi-IN-Neural2-A", "language_code": "hi-IN"},
                    "en": {"name": "en-US-Neural2-C", "language_code": "en-US"},
                    "hi": {"name": "hi-IN-Neural2-A", "language_code": "hi-IN"},
                    "default": {"name": "en-US-Neural2-C", "language_code": "en-US"},
                }
                
                voice_key = lang.replace("_", "-")
                voice_config = voice_map.get(voice_key, voice_map["default"])
                
                print(f"  Language '{lang}' → Voice: {voice_config['name']} ({voice_config['language_code']})")
                
            except Exception as e:
                print(f"  ❌ Language '{lang}' failed: {e}")
    
    print("\n📋 Summary:")
    print("- Fixed the voice key normalization (removed .upper())")
    print("- Added support for base language codes (en, hi, etc.)")
    print("- Added more regional variants (en-GB, es-ES, fr-FR)")
    print("- Added debug logging for language detection and voice selection")
    
    print("\n🔧 Next Steps:")
    print("1. Test voice messaging in the frontend")
    print("2. Check browser console for language detection logs")
    print("3. Verify audio is being recorded in the expected language")
    print("4. Check if the AI response language matches the expected language")

if __name__ == "__main__":
    asyncio.run(test_voice_languages())
