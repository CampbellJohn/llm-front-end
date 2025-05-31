import { useState, useCallback, useEffect, useRef } from 'react';
import { sendChatRequest, fetchConversation, updateConversation, createConversation } from '../services/api';

export const useChat = () => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [conversationTitle, setConversationTitle] = useState('New Chat');
  const abortControllerRef = useRef(null);

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

  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
      setIsLoading(false);
    }
  }, []);

  const sendMessage = async (content) => {
    // If we're already streaming, stop the current stream
    if (isStreaming) {
      stopStreaming();
      return;
    }

    const userMessage = { role: 'user', content };
    let conversationId = currentConversationId;
    let updatedMessages = [];
    
    // Create a new AbortController for this request
    abortControllerRef.current = new AbortController();
    
    // Step 1: Create a new conversation if we don't have one yet
    if (!conversationId) {
      try {
        // Create a title from the first message
        const title = content.length > 30 ? `${content.substring(0, 30)}...` : content;
        const newConversation = await createConversation(title);
        conversationId = newConversation.id;
        setCurrentConversationId(conversationId);
        setConversationTitle(newConversation.title);
        
        // For a new conversation, start with just the user message
        updatedMessages = [userMessage];
      } catch (err) {
        console.error('Failed to create new conversation:', err);
        setError('Failed to create new conversation');
        abortControllerRef.current = null;
        return;
      }
    } else {
      // For existing conversations, include all previous messages plus the new one
      updatedMessages = [...messages, userMessage];
    }
    
    // Step 2: Update the UI with the user message
    setMessages(updatedMessages);
    setIsLoading(true);
    setIsStreaming(true);
    setError(null);
    
    // Step 3: Save the updated messages to the conversation
    try {
      await updateConversation(conversationId, { messages: updatedMessages });
    } catch (err) {
      console.error(`Error saving messages to conversation ${conversationId}:`, err);
      // Continue anyway - we'll try to get a response
    }

    // Step 4: Add an empty assistant message that we'll stream into
    const assistantMessage = { role: 'assistant', content: '' };
    updatedMessages = [...updatedMessages, assistantMessage];
    setMessages(updatedMessages);

    // Step 5: Send the request to the API
    try {
      await new Promise((resolve, reject) => {
        // Use the updated messages array without the empty assistant message
        const messagesToSend = updatedMessages.slice(0, -1); // Remove the empty assistant message
        
        sendChatRequest(
          messagesToSend, 
          (chunk) => {
            try {
              if (chunk.choices && chunk.choices[0].delta) {
                const delta = chunk.choices[0].delta;
                if (delta.content) {
                  updateLastMessage(delta.content);
                  
                  // Update our local copy of the messages
                  const lastIndex = updatedMessages.length - 1;
                  updatedMessages[lastIndex].content += delta.content;
                }
              }
            } catch (err) {
              console.error('Error processing chunk:', err);
              reject(err);
            }
          },
          abortControllerRef.current?.signal
        )
        .then(resolve)
        .catch(reject);
      });
      
      // Step 6: Save the final conversation with the complete assistant response
      if (!abortControllerRef.current?.signal.aborted) {
        try {
          await updateConversation(conversationId, { messages: updatedMessages });
        } catch (err) {
          console.error(`Error saving completed conversation ${conversationId}:`, err);
        }
      }
    } catch (err) {
      // Only show error if it's not an abort error
      if (err.name !== 'AbortError') {
        console.error('Error in sendMessage:', err);
        setError('Failed to get response from the server');
        // Remove the assistant's message if there was an error
        setMessages(prev => prev.filter(msg => msg.role !== 'assistant' || msg.content !== ''));
        updatedMessages = updatedMessages.filter(msg => msg.role !== 'assistant' || msg.content !== '');
      }
    } finally {
      abortControllerRef.current = null;
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  // Clean up any pending requests when the component unmounts
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  const clearMessages = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
    setMessages([]);
    setError(null);
    setCurrentConversationId(null);
    setConversationTitle('New Chat');
    setIsLoading(false);
    setIsStreaming(false);
  };
  
  // Save messages to the conversation when they change
  useEffect(() => {
    // Only update if we have a current conversation and messages
    if (currentConversationId && messages.length > 0) {
      // Don't save if we're in the middle of streaming
      if (!isStreaming) {
        const timeoutId = setTimeout(() => {
          updateConversation(currentConversationId, { messages })
            .then(updatedConversation => {
              if (updatedConversation.id !== currentConversationId) {
                setCurrentConversationId(updatedConversation.id);
              }
              if (updatedConversation.title !== conversationTitle) {
                setConversationTitle(updatedConversation.title);
              }
            })
            .catch(err => {
              console.error(`Error saving messages to conversation ${currentConversationId}:`, err);
            });
        }, 1000);
        
        return () => clearTimeout(timeoutId);
      }
    }
  }, [messages, currentConversationId, conversationTitle, isStreaming]);

  const loadConversation = async (conversationId) => {
    try {
      // Abort any ongoing requests when loading a new conversation
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      
      setIsLoading(true);
      setError(null);
      
      const conversation = await fetchConversation(conversationId);
      setMessages(conversation.messages || []);
      setConversationTitle(conversation.title);
      setCurrentConversationId(conversationId);
    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error('Error loading conversation:', err);
        setError('Failed to load conversation');
      }
    } finally {
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  return {
    messages,
    isLoading,
    isStreaming,
    error,
    sendMessage,
    stopStreaming,
    clearMessages,
    loadConversation,
    currentConversationId,
    conversationTitle,
    setCurrentConversationId
  };
};

export default useChat;