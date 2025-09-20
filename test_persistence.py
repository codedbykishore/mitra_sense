#!/usr/bin/env python3
"""
Quick test script to verify chat persistence is working.
"""
import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from app.services.firestore import FirestoreService
from datetime import datetime, timezone
import uuid


async def test_persistence():
    """Test that conversation and message persistence works."""
    
    print("🧪 Testing Chat Persistence...")
    
    try:
        # Initialize FirestoreService
        firestore_service = FirestoreService()
        print("✅ FirestoreService initialized successfully")
        
        # Test 1: Create a conversation
        test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
        conversation_id = await firestore_service.create_or_update_conversation(test_user_id)
        print(f"✅ Created conversation: {conversation_id}")
        
        # Test 2: Save a user message
        user_message_data = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "sender_id": test_user_id,
            "text": "Mann nahi lag raha padhai mein",
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "user",
                "language": "hi",
                "embedding_id": None,
                "emotion_score": "{}"
            }
        }
        
        await firestore_service.save_message(conversation_id, user_message_data)
        print("✅ Saved user message to Firestore")
        
        # Test 3: Save an AI message
        ai_message_data = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "sender_id": "ai", 
            "text": "मैं समझ सकता हूं कि आपका मन पढ़ाई में नहीं लग रहा।",
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "ai",
                "language": "hi",
                "embedding_id": None,
                "emotion_score": "{}"
            }
        }
        
        await firestore_service.save_message(conversation_id, ai_message_data)
        print("✅ Saved AI message to Firestore")
        
        print(f"\n🎉 Chat persistence test PASSED!")
        print(f"   Conversation ID: {conversation_id}")
        print(f"   User ID: {test_user_id}")
        print(f"   Messages saved: 2 (user + AI)")
        
        return True
        
    except Exception as e:
        print(f"❌ Chat persistence test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    result = asyncio.run(test_persistence())
    sys.exit(0 if result else 1)
