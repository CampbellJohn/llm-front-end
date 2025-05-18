import { useState, useCallback, useEffect } from 'react';
import { sendChatRequest, fetchConversation, updateConversation, createConversation } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationTitle, setConversationTitle] = useState('New Chat');

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
    
    // Create a new conversation if we don't have one yet
    if (!currentConversationId) {
      try {
        // Create a title from the first message
        const title = content.length > 30 ? `${content.substring(0, 30)}...` : content;
        const newConversation = await createConversation(title);
        setCurrentConversationId(newConversation.id);
        setConversationTitle(newConversation.title);
        console.log(`Created new conversation: ${newConversation.id}`);
      } catch (err) {
        console.error('Failed to create new conversation:', err);
        setError('Failed to create new conversation');
        return; // Don't proceed if we couldn't create a conversation
      }
    } else {
      console.log(`Appending message to existing conversation: ${currentConversationId}`);
    }
    
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
    setCurrentConversationId(null);
    setConversationTitle('New Chat');
  };
  
  // Save messages to the conversation when they change
  useEffect(() => {
    // Only update if we have a current conversation and messages
    if (currentConversationId && messages.length > 0) {
      console.log(`Saving ${messages.length} messages to conversation ${currentConversationId}`);
      
      // Debounce the update to avoid too many API calls
      const timeoutId = setTimeout(() => {
        updateConversation(currentConversationId, { messages })
          .then(updatedConversation => {
            console.log(`Successfully updated conversation ${currentConversationId}:`, updatedConversation.id);
            
            // Verify the returned conversation ID matches what we expect
            if (updatedConversation.id !== currentConversationId) {
              console.warn(`Warning: Updated conversation ID (${updatedConversation.id}) doesn't match current ID (${currentConversationId})`);
            }
            
            // Update the conversation title if it changed
            if (updatedConversation.title !== conversationTitle) {
              setConversationTitle(updatedConversation.title);
            }
          })
          .catch(err => {
            console.error(`Error saving messages to conversation ${currentConversationId}:`, err);
          });
      }, 1000); // Wait 1 second after messages stop changing
      
      return () => clearTimeout(timeoutId);
    }
  }, [messages, currentConversationId, conversationTitle]);

  const loadConversation = async (conversationId) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const conversation = await fetchConversation(conversationId);
      setMessages(conversation.messages || []);
      setConversationTitle(conversation.title);
      setCurrentConversationId(conversationId);
    } catch (err) {
      console.error('Error loading conversation:', err);
      setError('Failed to load conversation');
    } finally {
      setIsLoading(false);
    }
  };

  return {
    messages,
    isLoading,
    isStreaming,
    error,
    sendMessage,
    clearMessages,
    loadConversation,
    currentConversationId,
    conversationTitle,
    setCurrentConversationId
  };
};

export default useChat;