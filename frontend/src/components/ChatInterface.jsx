import React, { useState, useRef, useEffect, useCallback } from 'react';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';

const ChatInterface = ({ messages, isLoading, isStreaming, error, sendMessage, clearMessages }) => {
  const messagesEndRef = useRef(null);
  const [autoScroll, setAutoScroll] = useState(true);

  const scrollToBottom = useCallback(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [autoScroll]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming, scrollToBottom]);

  const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    const isAtBottom = scrollHeight - (scrollTop + clientHeight) < 100;
    setAutoScroll(isAtBottom);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8 h-full flex flex-col">
      <div className="bg-white rounded-lg shadow-sm flex flex-col flex-grow">
        {/* Messages area */}
        <div 
          className="chat-container p-4 overflow-y-auto flex-grow"
          onScroll={handleScroll}
        >
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <div className="mb-8 text-center">
                <h2 className="text-2xl font-bold mb-2">Welcome!</h2>
                <p className="text-gray-600 mb-6">This is a custom, scalable LLM front-end.</p>
              </div>
              <div className="w-full max-w-md">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {[
                    "Which model are you?",
                    "Tell me about Docker containers.",
                    "Write me an excel formula.",
                    "What are your capabilities?"
                  ].map((suggestion, i) => (
                    <button
                      key={i}
                      className="bg-gray-100 hover:bg-gray-200 rounded-lg py-3 px-4 text-left text-sm transition-colors"
                      onClick={() => sendMessage(suggestion)}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message, index) => (
                <ChatMessage
                  key={index}
                  message={message}
                  isLastMessage={index === messages.length - 1}
                />
              ))}
              {error && (
                <div className="bg-red-50 text-red-700 p-4 rounded-md my-4">
                  <strong>Error:</strong> {error}
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input area */}
        <div className="border-t border-gray-200 p-4">
          <div className="p-4 border-t border-gray-200 bg-white">
            <MessageInput 
              onSend={sendMessage} 
              isSending={isLoading} 
              disabled={isStreaming} 
            />
            {error && <div className="mt-2 text-red-500 text-sm">{error}</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;