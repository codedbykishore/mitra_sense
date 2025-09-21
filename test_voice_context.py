#!/usr/bin/env python3
"""
Test script to verify voice chat context integration with text chat.
This will help verify that voice messages now maintain conversation context.
"""

import asyncio
import logging
import os
import json

# Setup environment
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "secrets/secrets.json"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_voice_context_integration():
    """Test that voice chat now maintains conversation context like text chat."""
    
    print("🔍 Testing MITRA Voice Context Integration...")
    print("=" * 60)
    
    try:
        from app.services.conversation_service import ConversationService
        from app.services.firestore import FirestoreService
        
        conversation_service = ConversationService()
        firestore_service = FirestoreService()
        
        print("✅ Services initialized successfully")
        
        # Test 1: Create a test conversation
        test_user_id = "test_voice_context_user"
        conversation_id = await firestore_service.create_or_update_conversation(
            test_user_id, force_new=True
        )
        print(f"📝 Created test conversation: {conversation_id}")
        
        # Test 2: Add some context messages
        import uuid
        from datetime import datetime, timezone
        
        # Add a text message first
        text_message = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "sender_id": test_user_id,
            "text": "I've been feeling anxious about my upcoming exams.",
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "text",
                "language": "en",
                "embedding_id": None,
                "emotion_score": "{\"anxiety\": 0.7, \"stress\": 0.6}"
            }
        }
        await firestore_service.save_message(conversation_id, text_message)
        
        # Add an AI response
        ai_message = {
            "message_id": str(uuid.uuid4()),
            "conversation_id": conversation_id,
            "sender_id": "ai",
            "text": "I understand that exam anxiety can be overwhelming. It's completely normal to feel this way. What specific aspects of the exams are worrying you the most?",
            "timestamp": datetime.now(timezone.utc),
            "metadata": {
                "source": "text",
                "language": "en",
                "embedding_id": None,
                "emotion_score": "{}"
            }
        }
        await firestore_service.save_message(conversation_id, ai_message)
        
        print("💬 Added text conversation context")
        
        # Test 3: Retrieve conversation context (what voice chat will now use)
        recent_messages = await conversation_service.get_recent_context(
            conversation_id, limit=5
        )
        
        if recent_messages:
            formatted_context = await conversation_service.format_context_for_rag(
                recent_messages, include_metadata=False
            )
            
            print(f"🔍 Retrieved context - {len(recent_messages)} messages:")
            for msg in recent_messages:
                sender = "User" if msg.get("sender_id") != "ai" else "AI"
                text = msg.get("text", "")[:50] + "..." if len(msg.get("text", "")) > 50 else msg.get("text", "")
                print(f"  {sender}: {text}")
            
            print(f"\n📋 Formatted context ({len(formatted_context)} chars):")
            print(f"'{formatted_context[:200]}...'")
            
        else:
            print("❌ No context retrieved")
            return
        
        # Test 4: Simulate voice processing with context
        print(f"\n🎤 Simulating voice message with context...")
        
        # This is what the voice pipeline now does:
        test_voice_transcript = "The math exam is what's bothering me most"
        
        from app.services.gemini_ai import GeminiService
        gemini_service = GeminiService()
        
        # Process with conversation context (like voice pipeline now does)
        voice_options = {
            "language": "en",
            "conversation_context": formatted_context
        }
        
        voice_response = await gemini_service.process_voice_conversation(
            test_voice_transcript, voice_options
        )
        
        print(f"🤖 Voice AI Response with context:")
        print(f"'{voice_response.get('response', 'No response')}'")
        
        # Test 5: Process without context for comparison
        print(f"\n🔍 Comparison - same input WITHOUT context:")
        
        no_context_response = await gemini_service.process_voice_conversation(
            test_voice_transcript, {"language": "en"}
        )
        
        print(f"🤖 Voice AI Response without context:")
        print(f"'{no_context_response.get('response', 'No response')}'")
        
        # Analysis
        with_context = voice_response.get('response', '')
        without_context = no_context_response.get('response', '')
        
        print(f"\n📊 Analysis:")
        print(f"Response with context: {len(with_context)} chars")
        print(f"Response without context: {len(without_context)} chars")
        
        # Check if context-aware response mentions exams/anxiety
        context_aware_keywords = ['exam', 'anxiety', 'anxious', 'math', 'worry']
        context_mentions = sum(1 for word in context_aware_keywords if word.lower() in with_context.lower())
        no_context_mentions = sum(1 for word in context_aware_keywords if word.lower() in without_context.lower())
        
        print(f"Context-aware response mentions: {context_mentions} relevant keywords")
        print(f"No-context response mentions: {no_context_mentions} relevant keywords")
        
        if context_mentions > no_context_mentions:
            print("✅ SUCCESS: Voice chat now uses conversation context!")
        else:
            print("⚠️  WARNING: Context may not be fully utilized")
        
        # Cleanup
        print(f"\n🧹 Cleaning up test conversation...")
        # Note: In a real implementation, you might want to delete test conversations
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Test failed: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_voice_context_integration())
