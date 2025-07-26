import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Chat API
export const chatAPI = {
  sendMessage: async (userMessage, userId = 1, sessionId = null) => {
    try {
      const response = await api.post('/chat', {
        user_id: userId,
        message: userMessage,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  getConversations: async (userId = 1) => {
    try {
      const response = await api.get(`/users/${userId}/conversations`);
      return response.data;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  getConversationMessages: async (sessionId) => {
    try {
      const response = await api.get(`/conversations/${sessionId}/messages`);
      return response.data;
    } catch (error) {
      console.error('Error fetching conversation messages:', error);
      throw error;
    }
  },

  createConversation: async (userId = 1, title = 'New Conversation') => {
    try {
      const response = await api.post('/conversations', {
        user_id: userId,
        title: title
      });
      return response.data;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  }
};

// Memory API
export const memoryAPI = {
  searchMemory: async (userId, query, sessionId = null, limit = 5) => {
    try {
      const response = await api.post(`/memory/search/${userId}`, {
        query,
        session_id: sessionId,
        limit
      });
      return response.data;
    } catch (error) {
      console.error('Error searching memory:', error);
      throw error;
    }
  },

  getMemoryStats: async (userId) => {
    try {
      const response = await api.get(`/memory/stats/${userId}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching memory stats:', error);
      throw error;
    }
  }
};

export default api; 