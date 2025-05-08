import { useState, useCallback } from 'react';
import { sendChatRequest } from '../services/api';

const useChat = (initialMessages = [], selectedModel, selectedProvider) => {
  const [messages, setMessages] = useState(initialMessages);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const addMessage = useCallback((message) => {
    setMessages((prevMessages) => [...prevMessages, message]);
  }, []);

  const sendMessage = useCallback(async (content) => {
    const userMessage = { role: 'user', content };
    addMessage(userMessage);
    setIsLoading(true);
    setError(null);

    try {
      // Add all previous messages to the conversation history
      const messagesToSend = [...messages, userMessage];
      
      const response = await sendChatRequest(
        messagesToSend,
        selectedModel,
        selectedProvider
      );
      
      addMessage(response.message);
      setIsLoading(false);
      return response;
    } catch (err) {
      console.error('Error sending message:', err);
      setError(
        err.response?.data?.error || 
        'Failed to get a response. Please try again.'
      );
      setIsLoading(false);
      return null;
    }
  }, [messages, addMessage, selectedModel, selectedProvider]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    sendMessage,
    clearMessages,
  };
};

export default useChat;