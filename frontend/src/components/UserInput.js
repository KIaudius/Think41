import React, { useState } from 'react';

const UserInput = ({ onSendMessage, disabled = false }) => {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputValue.trim() && !disabled) {
      onSendMessage(inputValue.trim());
      setInputValue('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="user-input-container">
      <form className="user-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="user-input"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          disabled={disabled}
        />
        <button
          type="submit"
          className="send-button"
          disabled={!inputValue.trim() || disabled}
        >
          Send
        </button>
      </form>
    </div>
  );
};

export default UserInput; 