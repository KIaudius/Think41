import React from 'react';
import MessageList from './MessageList';
import UserInput from './UserInput';

const ChatWindow = ({ messages, loading, onSendMessage }) => {
  return (
    <div className="chat-window">
      <div className="chat-container">
        <div className="chat-main">
          <MessageList messages={messages} loading={loading} />
          <UserInput onSendMessage={onSendMessage} disabled={loading} />
        </div>
      </div>
    </div>
  );
};

export default ChatWindow; 