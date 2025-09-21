#!/usr/bin/env python3
"""
Test voice pipeline with debug logging to see what's happening.
"""

import requests
import json

def test_voice_pipeline_debug():
    """Test voice pipeline with minimal data to see debug output."""
    
    print("🧪 Testing Voice Pipeline with Debug Logging...")
    print("=" * 50)
    
    # Create a minimal test audio file (empty for now - just to trigger the pipeline)
    test_data = {
        'duration': '1.0',
        'sessionId': 'debug_test_session',
        'conversationId': 'debug_test_conversation',
        'culturalContext': json.dumps({
            'language': 'en-US',
            'familyContext': 'individual'
        })
    }
    
    # Create a tiny fake audio file
    fake_audio = b'fake_audio_data_for_testing'
    
    files = {
        'audio': ('test.webm', fake_audio, 'audio/webm')
    }
    
    try:
        print("📤 Sending request to voice pipeline...")
        print(f"Data: {test_data}")
        
        response = requests.post(
            'http://localhost:8000/api/v1/voice/pipeline/audio',
            files=files,
            data=test_data,
            timeout=30
        )
        
        print(f"📥 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success! Response received:")
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Error Response: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure backend is running on localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_voice_pipeline_debug()
