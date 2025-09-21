// MITRA Sense API Service
// Centralized API calls with proper error handling and async patterns

interface ConversationInfo {
  conversation_id: string;
  participants: string[];
  created_at: string | null;
  last_active_at: string | null;
  participant_count: number;
}

interface ConversationsListResponse {
  conversations: ConversationInfo[];
  total_count: number;
}

interface MessageInfo {
  message_id: string;
  conversation_id: string;
  sender_id: string;
  text: string;
  timestamp: string;
  metadata: Record<string, any>;
  mood_score?: Record<string, string> | null;
}

interface ConversationMessagesResponse {
  conversation_id: string;
  messages: MessageInfo[];
  message_count: number;
  limit: number;
  has_more: boolean;
}

interface ConversationContextResponse {
  context: MessageInfo[];
  formatted_context: string;
  message_count: number;
  conversation_id: string;
  limit: number;
}

interface ChatRequest {
  text: string;
  context: Record<string, any>;
  language: string;
  region: string | null;
  max_rag_results: number;
  force_new_conversation?: boolean;
  conversation_id?: string;
  include_conversation_context?: boolean;
  context_limit?: number;
}

interface ChatResponse {
  response: string;
  conversation_id: string;
  sources?: Array<{
    text: string;
    source: string;
    relevance_score: number;
  }>;
  context_used?: boolean;
  emotion_detected?: Record<string, number>;
  crisis_score?: number;
  rag_sources?: string[];
  suggested_actions?: string[];
  cultural_adaptations?: Record<string, string>;
}

class APIError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class APIService {
  private baseURL: string;
  private cachePrefix: string = 'mitra_chat_';
  private cacheExpiry: number = 30 * 60 * 1000; // 30 minutes

  constructor() {
    // Use backend URL directly for Firebase Hosting deployment
    this.baseURL = process.env.NEXT_PUBLIC_BACKEND_URL 
      ? `${process.env.NEXT_PUBLIC_BACKEND_URL}/api/v1`
      : '/api/v1'; // Fallback for development
  }

  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        credentials: 'include', // Include session cookies
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new APIError(
          errorData.detail || `Request failed with status ${response.status}`,
          response.status,
          errorData
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      
      // Network or other errors
      console.error('API request failed:', error);
      throw new APIError(
        'Network error: Unable to connect to server',
        0,
        error
      );
    }
  }

  /**
   * Fetch all conversations for the current user
   * @returns Promise<ConversationsListResponse>
   */
  async getConversations(): Promise<ConversationsListResponse> {
    const cacheKey = 'conversations_list';
    
    // Try to get from cache first
    const cached = this.getCache(cacheKey);
    if (cached) {
      console.log('📥 Using cached conversations list');
      return cached;
    }

    // Fetch from API
    const response = await this.makeRequest<ConversationsListResponse>('/conversations');
    
    // Cache the response
    this.setCache(cacheKey, response);
    console.log('💾 Cached conversations list');
    
    return response;
  }

  /**
   * Fetch messages for a specific conversation
   * @param conversationId - The conversation ID
   * @param limit - Maximum number of messages to fetch (1-100)
   * @returns Promise<ConversationMessagesResponse>
   */
  async getConversationMessages(
    conversationId: string,
    limit: number = 50
  ): Promise<ConversationMessagesResponse> {
    const cacheKey = `messages_${conversationId}_${limit}`;
    
    // Try to get from cache first
    const cached = this.getCache(cacheKey);
    if (cached) {
      console.log(`📥 Using cached messages for conversation ${conversationId}`);
      return cached;
    }

    // Fetch from API
    const response = await this.makeRequest<ConversationMessagesResponse>(
      `/conversations/${conversationId}/messages?limit=${limit}`
    );
    
    // Clean up any malformed responses in the loaded messages
    if (response.messages) {
      response.messages = response.messages.map(message => {
        if (message.text && typeof message.text === 'string') {
          // Apply the same cleaning logic as new messages for assistant responses
          // Check if this looks like a malformed response format
          if (message.text.includes("'response':") || message.text.includes('"response":')) {
            message.text = this.extractResponseText(message.text);
          }
        }
        return message;
      });
    }
    
    // Cache the response
    this.setCache(cacheKey, response);
    console.log(`💾 Cached messages for conversation ${conversationId}`);
    
    return response;
  }

  /**
   * Get recent conversation context for RAG-enhanced responses
   * @param conversationId - The conversation ID
   * @param limit - Maximum number of recent messages (1-50)
   * @returns Promise<ConversationContextResponse>
   */
  async getConversationContext(
    conversationId: string,
    limit: number = 10
  ): Promise<ConversationContextResponse> {
    const cacheKey = `context_${conversationId}_${limit}`;
    
    // Try to get from cache first
    const cached = this.getCache(cacheKey);
    if (cached) {
      console.log(`📥 Using cached context for conversation ${conversationId}`);
      return cached;
    }

    // Fetch from API
    const response = await this.makeRequest<ConversationContextResponse>(
      `/conversations/${conversationId}/context?limit=${limit}`
    );
    
    // Cache the response for a shorter time (5 minutes) since context changes frequently
    const shortCacheData = {
      data: response,
      timestamp: Date.now(),
      expiry: Date.now() + (5 * 60 * 1000) // 5 minutes
    };
    
    try {
      localStorage.setItem(`${this.cachePrefix}context_${conversationId}_${limit}`, JSON.stringify(shortCacheData));
    } catch (error) {
      console.warn('Failed to cache context data:', error);
    }
    
    console.log(`💾 Cached context for conversation ${conversationId}`);
    return response;
  }

  /**
   * Send a chat message and get AI response with automatic conversation context
   * @param request - Chat request data
   * @returns Promise<ChatResponse>
   */
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    // Enhanced request with conversation context handling
    const enhancedRequest = {
      ...request,
      include_conversation_context: request.include_conversation_context ?? true,
      context_limit: request.context_limit ?? 10,
    };

    const response = await this.makeRequest<ChatResponse>('/input/chat', {
      method: 'POST',
      body: JSON.stringify(enhancedRequest),
    });

    // DEBUG: Log the full response structure
    console.log('🔍 Full API Response:', JSON.stringify(response, null, 2));
    console.log('🔍 Response.response:', response.response);
    console.log('🔍 Type of response.response:', typeof response.response);

    // Clean up the stringified dictionary response
    if (response.response && typeof response.response === 'string') {
      response.response = this.extractResponseText(response.response);
      console.log('🔍 Cleaned Response.response:', response.response);
    }

    // Invalidate relevant caches when new message is sent
    this.clearCache('conversations_list'); // New message might change conversation order
    // Clear message caches for all conversations since we don't know which conversation this belongs to
    this.clearCacheByPattern('messages_');
    this.clearCacheByPattern('history_');
    this.clearCacheByPattern('context_'); // Clear context cache as well

    return response;
  }

  /**
   * Send a chat message with explicit conversation context
   * @param conversationId - The conversation ID to get context from
   * @param messageText - The message text to send
   * @param options - Additional request options
   * @returns Promise<ChatResponse>
   */
  async sendChatMessageWithContext(
    conversationId: string,
    messageText: string,
    options: Partial<ChatRequest> = {}
  ): Promise<ChatResponse> {
    const request: ChatRequest = {
      text: messageText,
      conversation_id: conversationId,
      include_conversation_context: true,
      context_limit: options.context_limit ?? 10,
      context: options.context ?? {},
      language: options.language ?? "en",
      region: options.region ?? null,
      max_rag_results: options.max_rag_results ?? 3,
      force_new_conversation: options.force_new_conversation ?? false,
    };

    return this.sendChatMessage(request);
  }

  /**
   * Extract actual response text from stringified dictionary format
   * @param responseText - Raw response text like "{'response': 'actual text'}"
   * @returns Clean response text
   */
  private extractResponseText(responseText: string): string {
    try {
      // Handle stringified dictionary format: {'response': 'actual text'}
      if (responseText.includes("'response':") || responseText.includes('"response":')) {
        // Use regex to extract the response content directly
        // Match: {'response': "content"} or {"response": "content"}
        const match = responseText.match(/['"]response['"]:\s*["']([\s\S]+?)["']\s*[}]/);
        if (match && match[1]) {
          // Unescape the content
          return match[1]
            .replace(/\\n/g, '\n')      // Convert \n to actual newlines
            .replace(/\\'/g, "'")       // Convert \' to '
            .replace(/\\"/g, '"')       // Convert \" to "
            .replace(/\\\\/g, '\\')     // Convert \\ to \
            .trim();
        }
      }
      
      // If not in expected format, return as-is
      return responseText.trim();
    } catch (error) {
      console.warn('Failed to parse response format, using as-is:', error);
      return responseText.trim();
    }
  }

  /**
   * Cache data in localStorage with expiry
   * @param key - Cache key
   * @param data - Data to cache
   */
  private setCache(key: string, data: any): void {
    try {
      const cacheData = {
        data,
        timestamp: Date.now(),
        expiry: Date.now() + this.cacheExpiry
      };
      localStorage.setItem(`${this.cachePrefix}${key}`, JSON.stringify(cacheData));
    } catch (error) {
      console.warn('Failed to cache data:', error);
    }
  }

  /**
   * Get cached data from localStorage
   * @param key - Cache key
   * @returns Cached data or null if expired/not found
   */
  private getCache(key: string): any {
    try {
      const cached = localStorage.getItem(`${this.cachePrefix}${key}`);
      if (!cached) return null;

      const cacheData = JSON.parse(cached);
      if (Date.now() > cacheData.expiry) {
        localStorage.removeItem(`${this.cachePrefix}${key}`);
        return null;
      }

      return cacheData.data;
    } catch (error) {
      console.warn('Failed to get cached data:', error);
      return null;
    }
  }

  /**
   * Clear specific cache or all chat cache
   * @param key - Specific key to clear, or null to clear all
   */
  public clearCache(key?: string): void {
    try {
      if (key) {
        localStorage.removeItem(`${this.cachePrefix}${key}`);
      } else {
        // Clear all chat cache
        Object.keys(localStorage).forEach(storageKey => {
          if (storageKey.startsWith(this.cachePrefix)) {
            localStorage.removeItem(storageKey);
          }
        });
      }
    } catch (error) {
      console.warn('Failed to clear cache:', error);
    }
  }

  /**
   * Clear cache entries that match a pattern
   * @param pattern - Pattern to match cache keys
   */
  private clearCacheByPattern(pattern: string): void {
    try {
      Object.keys(localStorage).forEach(storageKey => {
        if (storageKey.startsWith(`${this.cachePrefix}${pattern}`)) {
          localStorage.removeItem(storageKey);
        }
      });
    } catch (error) {
      console.warn('Failed to clear cache by pattern:', error);
    }
  }

  /**
   * Get the latest conversation ID for the user
   * @returns Promise<string | null>
   */
  async getLatestConversationId(): Promise<string | null> {
    try {
      const response = await this.getConversations();
      if (response.conversations.length === 0) {
        return null;
      }

      // Sort by last_active_at to get the most recent conversation
      const sortedConversations = response.conversations.sort((a, b) => {
        const aTime = a.last_active_at ? new Date(a.last_active_at).getTime() : 0;
        const bTime = b.last_active_at ? new Date(b.last_active_at).getTime() : 0;
        return bTime - aTime; // Descending order (newest first)
      });

      return sortedConversations[0].conversation_id;
    } catch (error) {
      console.error('Error fetching latest conversation:', error);
      return null;
    }
  }

  /**
   * Transform backend message format to frontend message format
   * @param message - Backend message format
   * @returns Frontend message format
   */
  transformMessage(message: MessageInfo) {
    return {
      id: message.message_id,
      role: message.sender_id === 'ai' ? 'assistant' : 'user',
      content: message.text,
      createdAt: message.timestamp,
      metadata: message.metadata,
      emotion: message.mood_score,
      type: message.metadata?.type || 'text',
    };
  }

  /**
   * Load chat history and transform to frontend format
   * @param conversationId - The conversation ID
   * @param limit - Maximum number of messages to load
   * @returns Promise with messages and pagination info
   */
  async loadChatHistory(conversationId: string, limit: number = 50) {
    try {
      const response = await this.getConversationMessages(conversationId, limit);
      
      // Transform messages to frontend format
      const messages = response.messages.map(msg => this.transformMessage(msg));
      
      // Sort messages chronologically (oldest → newest) for display
      messages.sort((a, b) => new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime());

      const result = {
        messages,
        hasMore: response.has_more,
        messageCount: response.message_count,
        conversationId: response.conversation_id,
      };

      // Cache the transformed result as well for faster access
      const transformedCacheKey = `history_${conversationId}_${limit}`;
      this.setCache(transformedCacheKey, result);

      return result;
    } catch (error) {
      console.error('Error loading chat history:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new APIService();

// Export types for use in components
export type { 
  ConversationInfo, 
  ConversationsListResponse, 
  MessageInfo, 
  ConversationMessagesResponse,
  ConversationContextResponse,
  ChatRequest, 
  ChatResponse,
  APIError 
};
