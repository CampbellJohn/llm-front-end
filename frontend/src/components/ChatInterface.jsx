import React, { useEffect, useRef } from 'react';
import useChat from '../hooks/useChat';
import ChatMessage from './ChatMessage';
import MessageInput from './MessageInput';
import { FiRefreshCw } from 'react-icons/fi';

const ChatInterface = ({ selectedModel, selectedProvider }) => {
  const { messages, isLoading, error, sendMessage, clearMessages } = useChat(
    [],
    selectedModel,
    selectedProvider
  );
  
  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-sm">
        {/* Messages area */}
        <div className="chat-container p-4 overflow-y-auto">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-500">
              <div className="mb-4 text-center">
                <h2 className="text-2xl font-bold mb-2">Welcome to LLM Chat</h2>
                <p className="text-lg">
                  Start a conversation with {selectedModel}
                </p>
              </div>
              <div className="w-full max-w-md">
                <div className="grid grid-cols-2 gap-2">
                  {[
                    "Tell me about quantum computing",
                    "Write a short story about a time traveler",
                    "Explain how neural networks work",
                    "What are the ethical implications of AI?"
                  ].map((suggestion, i) => (
                    <button
                      key={i}
                      className="bg-gray-100 hover:bg-gray-200 rounded-md py-2 px-3 text-left text-sm transition-colors"
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
          <div className="flex items-center justify-between mb-2">
            <div className="text-sm text-gray-500">
              Model: <span className="font-medium">{selectedModel}</span>
            </div>
            {messages.length > 0 && (
              <button
                onClick={clearMessages}
                className="flex items-center text-sm text-gray-500 hover:text-gray-700"
              >
                <FiRefreshCw className="mr-1" size={14} />
                New Chat
              </button>
            )}
          </div>
          
          <MessageInput onSendMessage={sendMessage} isLoading={isLoading} />
          
          {isLoading && (
            <div className="text-center mt-4">
              <div className="inline-block h-4 w-4 border-t-2 border-blue-500 rounded-full animate-spin"></div>
              <span className="ml-2 text-sm text-gray-500">Assistant is thinking...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;