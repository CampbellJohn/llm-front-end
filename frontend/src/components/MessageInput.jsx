import React, { useState, useEffect, useRef } from 'react';

const MessageInput = ({ onSend, isSending = false, disabled = false }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);
  const isInputDisabled = disabled || isSending;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (message.trim() && !isInputDisabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  }, [message]);

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex items-center gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isInputDisabled ? 'Please wait for the response...' : 'Type your message...'}
            className={`w-full p-3 pr-12 border rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
              isInputDisabled ? 'bg-gray-100 border-gray-200 cursor-not-allowed' : 'border-gray-300'
            }`}
            rows="1"
            style={{ minHeight: '44px' }}
            disabled={isInputDisabled}
          />
        </div>
        <button
          type="submit"
          disabled={!message.trim() || isInputDisabled}
          className={`px-4 py-2 h-10 rounded-lg focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors ${
            isInputDisabled
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
          }`}
        >
          {isSending ? 'Sending...' : 'Send'}
        </button>
      </div>
    </form>
  );
};

export default MessageInput;