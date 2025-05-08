import React, { useState, useEffect, useRef } from 'react';
import { FiSend } from 'react-icons/fi';

const MessageInput = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;
    
    onSendMessage(message);
    setMessage('');
    
    // Reset height after sending
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex items-end border border-gray-300 rounded-md bg-white p-2">
        <textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          className="message-input flex-grow resize-none min-h-[40px] max-h-[200px] outline-none"
          rows={1}
          disabled={isLoading}
        />
        <button
          type="submit"
          className={`ml-2 p-2 rounded-full ${
            isLoading || !message.trim()
              ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700'
          }`}
          disabled={isLoading || !message.trim()}
        >
          <FiSend size={18} />
        </button>
      </div>
      <div className="text-xs text-gray-500 mt-1 text-center">
        Press Enter to send, Shift+Enter for new line
      </div>
    </form>
  );
};

export default MessageInput;