import React, { useEffect } from 'react';
import './App.css';
import ChatWindow from './components/ChatWindow';
import ConversationHistory from './components/ConversationHistory';
import TestComponent from './components/TestComponent';
import { ChatProvider, useChat } from './context/ChatContext';
import { chatAPI } from './services/api';

const ChatApp = () => {
  const {
    messages,
    loading,
    currentSessionId,
    conversations,
    addMessage,
    setLoading,
    setCurrentSession,
    setConversations,
    loadConversation
  } = useChat();

  useEffect(() => {
    // Load conversations on component mount
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const conversationsData = await chatAPI.getConversations();
      setConversations(conversationsData);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const handleSendMessage = async (userMessage) => {
    try {
      // Add user message to the chat
      const userMsg = {
        type: 'user',
        content: userMessage,
        timestamp: new Date().toISOString()
      };
      addMessage(userMsg);

      // Set loading state
      setLoading(true);

      // Send message to backend
      const response = await chatAPI.sendMessage(userMessage, 1, currentSessionId);
      
      // Add AI response to the chat
      const aiMsg = {
        type: 'ai',
        content: response.ai_response,
        timestamp: new Date().toISOString()
      };
      addMessage(aiMsg);

      // Update current session if it's a new conversation
      if (!currentSessionId && response.session_id) {
        setCurrentSession(response.session_id);
        // Reload conversations to include the new one
        loadConversations();
      }

    } catch (error) {
      console.error('Failed to send message:', error);
      // Add error message
      const errorMsg = {
        type: 'ai',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString()
      };
      addMessage(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleConversationSelect = async (sessionId) => {
    try {
      setLoading(true);
      const messages = await chatAPI.getConversationMessages(sessionId);
      
      // Transform messages to match our format
      const formattedMessages = messages.map(msg => ({
        type: msg.message_type,
        content: msg.content,
        timestamp: msg.created_at
      }));

      loadConversation(sessionId, formattedMessages);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConversation = await chatAPI.createConversation(1, 'New Conversation');
      setCurrentSession(newConversation.id);
      loadConversations();
    } catch (error) {
      console.error('Failed to create new conversation:', error);
    }
  };

  return (
    <div className="chat-window">
      <TestComponent />
      <div className="chat-container">
        <ConversationHistory
          conversations={conversations}
          currentSessionId={currentSessionId}
          onConversationSelect={handleConversationSelect}
          onNewConversation={handleNewConversation}
        />
        <div className="chat-main">
          <ChatWindow
            messages={messages}
            loading={loading}
            onSendMessage={handleSendMessage}
          />
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Think41 AI Chat</h1>
      </header>
      <main>
        <ChatProvider>
          <ChatApp />
        </ChatProvider>
      </main>
    </div>
  );
}

export default App; 