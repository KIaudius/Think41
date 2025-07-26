import React, { createContext, useContext, useReducer } from 'react';

// Initial state
const initialState = {
  messages: [],
  loading: false,
  userInput: '',
  currentSessionId: null,
  conversations: []
};

// Action types
const ACTIONS = {
  ADD_MESSAGE: 'ADD_MESSAGE',
  SET_LOADING: 'SET_LOADING',
  SET_USER_INPUT: 'SET_USER_INPUT',
  SET_CURRENT_SESSION: 'SET_CURRENT_SESSION',
  SET_CONVERSATIONS: 'SET_CONVERSATIONS',
  LOAD_CONVERSATION: 'LOAD_CONVERSATION',
  CLEAR_MESSAGES: 'CLEAR_MESSAGES'
};

// Reducer function
const chatReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.ADD_MESSAGE:
      return {
        ...state,
        messages: [...state.messages, action.payload]
      };
    
    case ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };
    
    case ACTIONS.SET_USER_INPUT:
      return {
        ...state,
        userInput: action.payload
      };
    
    case ACTIONS.SET_CURRENT_SESSION:
      return {
        ...state,
        currentSessionId: action.payload
      };
    
    case ACTIONS.SET_CONVERSATIONS:
      return {
        ...state,
        conversations: action.payload
      };
    
    case ACTIONS.LOAD_CONVERSATION:
      return {
        ...state,
        messages: action.payload.messages,
        currentSessionId: action.payload.sessionId
      };
    
    case ACTIONS.CLEAR_MESSAGES:
      return {
        ...state,
        messages: []
      };
    
    default:
      return state;
  }
};

// Create context
const ChatContext = createContext();

// Provider component
export const ChatProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatReducer, initialState);

  const addMessage = (message) => {
    dispatch({ type: ACTIONS.ADD_MESSAGE, payload: message });
  };

  const setLoading = (loading) => {
    dispatch({ type: ACTIONS.SET_LOADING, payload: loading });
  };

  const setUserInput = (input) => {
    dispatch({ type: ACTIONS.SET_USER_INPUT, payload: input });
  };

  const setCurrentSession = (sessionId) => {
    dispatch({ type: ACTIONS.SET_CURRENT_SESSION, payload: sessionId });
  };

  const setConversations = (conversations) => {
    dispatch({ type: ACTIONS.SET_CONVERSATIONS, payload: conversations });
  };

  const loadConversation = (sessionId, messages) => {
    dispatch({ 
      type: ACTIONS.LOAD_CONVERSATION, 
      payload: { sessionId, messages } 
    });
  };

  const clearMessages = () => {
    dispatch({ type: ACTIONS.CLEAR_MESSAGES });
  };

  const value = {
    ...state,
    addMessage,
    setLoading,
    setUserInput,
    setCurrentSession,
    setConversations,
    loadConversation,
    clearMessages
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
};

// Custom hook to use the context
export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}; 