import { useState, useCallback } from 'react';
import { sendChatRequest } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);

  const updateLastMessage = useCallback((content) => {
    setMessages(prev => {
      const newMessages = [...prev];
      const lastMessage = newMessages[newMessages.length - 1];
      
      if (lastMessage && lastMessage.role === 'assistant') {
        newMessages[newMessages.length - 1] = {
          ...lastMessage,
          content: lastMessage.content + (content || '')
        };
      }
      return newMessages;
    });
  }, []);

  const sendMessage = async (content) => {
    const userMessage = { role: 'user', content };
    
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);

    try {
      // Add an empty assistant message that we'll stream into
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      await new Promise((resolve, reject) => {
        sendChatRequest([...messages, userMessage], (chunk) => {
          try {
            if (chunk.choices && chunk.choices[0].delta) {
              const delta = chunk.choices[0].delta;
              if (delta.content) {
                updateLastMessage(delta.content);
              }
            }
          } catch (err) {
            console.error('Error processing chunk:', err);
            reject(err);
          }
        })
        .then(resolve)
        .catch(reject);
      });
    } catch (err) {
      console.error('Error in sendMessage:', err);
      setError('Failed to get response from the server');
      // Remove the assistant's message if there was an error
      setMessages(prev => prev.filter(msg => msg.role !== 'assistant' || msg.content !== ''));
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setError(null);
  };

  return {
    messages,
    isLoading,
    isStreaming,
    error,
    sendMessage,
    clearMessages,
  };
};

export default useChat;