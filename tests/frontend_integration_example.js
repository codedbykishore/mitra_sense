// Example: Updated sendMessage function in AIAssistantUI.jsx
// This shows how to integrate the new conversation context feature

// Replace the existing sendMessage function with this enhanced version:

async function sendMessage(convId, content) {
  if (!content.trim()) return
  const now = new Date().toISOString()
  const userMsg = { id: Math.random().toString(36).slice(2), role: "user", content, createdAt: now }

  // Update conversation with user message
  setConversations((prev) =>
    prev.map((c) => {
      if (c.id !== convId) return c
      const msgs = [...(c.messages || []), userMsg]
      return {
        ...c,
        messages: msgs,
        updatedAt: now,
        messageCount: msgs.length,
        preview: content.slice(0, 80),
      }
    }),
  )

  setIsThinking(true)
  setThinkingConvId(convId)

  try {
    // Check if this is a new conversation (temporary ID)
    const isNewConversation = convId.startsWith('temp_');
    console.log("🔍 Sending message - convId:", convId, "isNewConversation:", isNewConversation);
    
    let data;
    
    if (isNewConversation) {
      // For new conversations, use the original method
      data = await apiService.sendChatMessage({
        text: content,
        context: {},
        language: "en",
        region: null,
        max_rag_results: 3,
        force_new_conversation: true,
        include_conversation_context: false, // No context for new conversations
      })
    } else {
      // For existing conversations, use the enhanced method with context
      data = await apiService.sendChatMessageWithContext(
        convId,
        content,
        {
          language: "en",
          region: null,
          max_rag_results: 3,
          context_limit: 10, // Include last 10 messages for context
        }
      )
    }

    // Debug: Log the API response
    console.log("🔍 AIAssistantUI - Full API response:", JSON.stringify(data, null, 2))
    console.log("🔍 AIAssistantUI - data.response:", data.response)
    console.log("🔍 AIAssistantUI - data.conversation_id:", data.conversation_id)

    // Use the response directly from API
    const responseText = data.response || "I'm here to help. Please let me know what's on your mind."
    const realConversationId = data.conversation_id;
    
    console.log("🔍 AIAssistantUI - Final responseText:", responseText)
    console.log("🔍 AIAssistantUI - Real conversation_id:", realConversationId)
    
    // Debug: Check if we have duplicate conversation IDs
    const existingConvWithSameId = conversations.find(c => c.id === realConversationId && c.id !== convId);
    if (existingConvWithSameId) {
      console.warn("⚠️ DUPLICATE CONVERSATION ID DETECTED!", {
        realConversationId,
        currentConvId: convId,
        existingConv: existingConvWithSameId.title
      });
    }
    
    // Add assistant response and update with real conversation ID
    const assistantMsg = {
      id: Math.random().toString(36).slice(2),
      role: "assistant",
      content: responseText,
      createdAt: new Date().toISOString(),
      // Include additional metadata if available
      sources: data.sources || [],
      crisis_score: data.crisis_score || 0,
      emotion_detected: data.emotion_detected || {},
    }

    setConversations((prev) => {
      return prev.map((c) => {
        if (c.id !== convId && c.id !== realConversationId) return c
        
        const msgs = [...(c.messages || []), assistantMsg]
        return {
          ...c,
          id: realConversationId, // Update to real conversation ID
          messages: msgs,
          updatedAt: new Date().toISOString(),
          messageCount: msgs.length,
          preview: responseText.slice(0, 80),
          title: c.title || content.slice(0, 30) + "...",
        }
      })
    })

    // If this was a new conversation, update the selected conversation
    if (isNewConversation && realConversationId !== convId) {
      setSelected(prev => prev ? { ...prev, id: realConversationId } : null)
    }

  } catch (error) {
    console.error("❌ Error sending message:", error)
    
    // Show error to user
    const errorMsg = {
      id: Math.random().toString(36).slice(2),
      role: "assistant",
      content: "I apologize, but I encountered an error processing your message. Please try again.",
      createdAt: new Date().toISOString(),
      isError: true,
    }

    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== convId) return c
        const msgs = [...(c.messages || []), errorMsg]
        return { ...c, messages: msgs, updatedAt: new Date().toISOString() }
      })
    )
  } finally {
    setIsThinking(false)
    setThinkingConvId(null)
  }
}

// Alternative: Simple direct usage example for sending a message with context
async function sendMessageWithManualContext() {
  try {
    const conversationId = "existing-conversation-id-123";
    
    // Method 1: Let the API automatically fetch and include context
    const response = await apiService.sendChatMessage({
      text: "I'm feeling anxious about my upcoming exams",
      conversation_id: conversationId,
      include_conversation_context: true,
      context_limit: 10, // Include last 10 messages
      language: "en",
      region: null,
      max_rag_results: 3,
    });
    
    console.log("AI Response:", response.response);
    console.log("Crisis Score:", response.crisis_score);
    console.log("RAG Sources:", response.sources);
    
    // Method 2: Manually fetch context first (for more control)
    const contextData = await apiService.getConversationContext(conversationId, 10);
    
    const responseWithManualContext = await apiService.sendChatMessage({
      text: "I'm feeling anxious about my upcoming exams",
      conversation_id: conversationId,
      include_conversation_context: false, // We're handling context manually
      context: {
        manual_context: contextData.formatted_context,
        context_message_count: contextData.message_count,
      },
      language: "en",
      region: null,
      max_rag_results: 3,
    });
    
  } catch (error) {
    console.error("Error:", error);
  }
}

// Method 3: Using the simplified wrapper method
async function sendMessageSimple() {
  try {
    const response = await apiService.sendChatMessageWithContext(
      "existing-conversation-id-123",
      "I need help with my anxiety",
      {
        context_limit: 15, // Include last 15 messages for more context
        language: "hi", // Hindi language
        max_rag_results: 5,
      }
    );
    
    console.log("AI Response:", response.response);
  } catch (error) {
    console.error("Error:", error);
  }
}
