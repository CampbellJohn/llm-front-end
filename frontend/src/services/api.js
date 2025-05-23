import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Conversation API functions
export const fetchConversations = async () => {
  try {
    const response = await api.get('/conversations/');
    return response.data;
  } catch (error) {
    console.error('Error fetching conversations:', error);
    throw error;
  }
};

export const fetchConversation = async (id) => {
  try {
    const response = await api.get(`/conversations/${id}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching conversation ${id}:`, error);
    throw error;
  }
};

export const createConversation = async (title, model = 'gpt-4', provider = 'openai') => {
  try {
    const response = await api.post('/conversations/', {
      title,
      messages: [],
      model,
      provider
    });
    return response.data;
  } catch (error) {
    console.error('Error creating conversation:', error);
    throw error;
  }
};

export const deleteConversation = async (id) => {
  try {
    await api.delete(`/conversations/${id}`);
  } catch (error) {
    console.error(`Error deleting conversation ${id}:`, error);
    throw error;
  }
};

export const updateConversation = async (id, updates) => {
  try {
    console.log(`Updating conversation ${id} with:`, updates);
    const response = await api.put(`/conversations/${id}`, updates);
    console.log(`Update response for conversation ${id}:`, response.data);
    return response.data;
  } catch (error) {
    console.error(`Error updating conversation ${id}:`, error);
    // Log more details about the error
    if (error.response) {
      console.error(`Server responded with status ${error.response.status}:`, error.response.data);
    } else if (error.request) {
      console.error('No response received from server');
    }
    throw error;
  }
};

export const sendChatRequest = async (messages, onChunk) => {
  try {
    const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        messages,
        stream: true,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    if (!response.body) {
      throw new Error('No response body');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      // Convert the Uint8Array to a string
      const chunk = decoder.decode(value, { stream: true });
      buffer += chunk;

      // Process each complete line in the buffer
      let boundary;
      while ((boundary = buffer.indexOf('\n\n')) !== -1) {
        const line = buffer.slice(0, boundary).trim();
        buffer = buffer.slice(boundary + 2);

        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          
          // Skip empty lines and the [DONE] message
          if (!data || data === '[DONE]') continue;

          try {
            const parsed = JSON.parse(data);
            
            // Handle potential error from the server
            if (parsed.error) {
              throw new Error(parsed.error);
            }
            
            onChunk && onChunk(parsed);
          } catch (e) {
            console.error('Error parsing chunk:', e, 'Chunk:', data);
            throw e; // Re-throw to be caught by the outer try-catch
          }
        }
      }
    }
    
    // Process any remaining data in the buffer
    if (buffer.trim()) {
      try {
        const line = buffer.trim();
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data && data !== '[DONE]') {
            const parsed = JSON.parse(data);
            onChunk && onChunk(parsed);
          }
        }
      } catch (e) {
        console.error('Error parsing final chunk:', e);
        throw e;
      }
    }
  } catch (error) {
    console.error('Error in sendChatRequest:', error);
    throw error;
  }
};

export default api;