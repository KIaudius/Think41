import React from 'react';

const ConversationHistory = ({ 
  conversations, 
  currentSessionId, 
  onConversationSelect, 
  onNewConversation 
}) => {
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="conversation-history">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h3>Conversations</h3>
        <button 
          onClick={onNewConversation}
          style={{
            padding: '8px 12px',
            background: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '0.8rem'
          }}
        >
          New
        </button>
      </div>
      
      {conversations.length === 0 ? (
        <div style={{ textAlign: 'center', color: '#6c757d', fontSize: '0.9rem' }}>
          No conversations yet. Start a new chat!
        </div>
      ) : (
        conversations.map((conversation) => (
          <div
            key={conversation.id}
            className={`conversation-item ${currentSessionId === conversation.id ? 'active' : ''}`}
            onClick={() => onConversationSelect(conversation.id)}
          >
            <h4>{conversation.title || 'Untitled Conversation'}</h4>
            <p>
              {formatDate(conversation.created_at)} at {formatTime(conversation.created_at)}
            </p>
            {conversation.message_count > 0 && (
              <p style={{ fontSize: '0.75rem', marginTop: '4px' }}>
                {conversation.message_count} message{conversation.message_count !== 1 ? 's' : ''}
              </p>
            )}
          </div>
        ))
      )}
    </div>
  );
};

export default ConversationHistory; 