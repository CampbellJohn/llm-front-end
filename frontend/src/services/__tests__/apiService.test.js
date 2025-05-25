const axios = require('axios');
const {
  fetchConversations,
  fetchConversation,
  createConversation,
  deleteConversation,
  updateConversation,
  sendChatRequest,
} = require('../api');

// Mock axios
jest.mock('axios', () => {
  const mockAxios = {
    create: jest.fn(() => mockAxios),
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
    interceptors: {
      request: { use: jest.fn(), eject: jest.fn() },
      response: { use: jest.fn(), eject: jest.fn() }
    }
  };
  return mockAxios;
});

// Add TextEncoder and TextDecoder polyfills for Node.js test environment
if (typeof TextEncoder === 'undefined') {
  global.TextEncoder = require('util').TextEncoder;
}
if (typeof TextDecoder === 'undefined') {
  global.TextDecoder = require('util').TextDecoder;
}

// Mock the Response object
class MockResponse {
  constructor(body, init = {}) {
    this.body = body;
    this.status = init.status || 200;
    this.statusText = init.statusText || 'OK';
    this.ok = this.status >= 200 && this.status < 300;
  }

  json() {
    return Promise.resolve(JSON.parse(this.body));
  }
}

// Helper function to create a mock fetch response
const createMockFetchResponse = (data, status = 200, statusText = 'OK') => {
  const response = new MockResponse(JSON.stringify(data), { status, statusText });
  response.body = {
    getReader: () => ({
      read: jest.fn().mockResolvedValueOnce({
        done: true,
        value: new TextEncoder().encode(`data: ${JSON.stringify(data)}\n\n`)
      })
    })
  };
  return response;
};

describe('API Service', () => {
  // Reset all mocks before each test
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Set up default mock implementations
    axios.get.mockResolvedValue({ data: [] });
    axios.post.mockResolvedValue({ data: {} });
    axios.put.mockResolvedValue({ data: {} });
    axios.delete.mockResolvedValue({ data: {} });
    
    // Reset the fetch mock
    global.fetch = jest.fn();
  });



  describe('sendChatRequest', () => {
    it('sends a message with the correct parameters', async () => {
      const messages = [{ role: 'user', content: 'Hello, world!' }];
      const expectedResponse = { id: '1', content: 'Response' };
      
      // Mock the fetch implementation used by sendChatRequest
      const mockReader = {
        read: jest.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode(`data: ${JSON.stringify(expectedResponse)}\n\n`)
          })
          .mockResolvedValueOnce({
            done: true
          })
      };
      
      const mockResponse = createMockFetchResponse(expectedResponse);
      mockResponse.body = {
        getReader: () => mockReader
      };
      
      global.fetch.mockResolvedValue(mockResponse);
      
      const onChunk = jest.fn();
      await sendChatRequest(messages, onChunk);
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/chat'),
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages,
            stream: true,
          }),
        }
      );
      
      // Wait for the next tick to allow the async operations to complete
      await new Promise(resolve => process.nextTick(resolve));
      
      expect(onChunk).toHaveBeenCalledWith(expectedResponse);
    });

    it('throws an error when the response is not ok', async () => {
      const errorResponse = { message: 'Server Error' };
      
      // Mock console.error to prevent error logs in test output
      const originalConsoleError = console.error;
      console.error = jest.fn();
      
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Server Error',
        json: () => Promise.resolve(errorResponse)
      });
      
      await expect(sendChatRequest([], jest.fn())).rejects.toThrow('Server Error');
      
      // Restore console.error
      console.error = originalConsoleError;
    });

    it('throws an error when there is no response body', async () => {
      // Mock console.error to prevent error logs in test output
      const originalConsoleError = console.error;
      console.error = jest.fn();
      
      global.fetch.mockResolvedValueOnce({
        ok: true,
        body: null
      });
      
      await expect(sendChatRequest([], jest.fn())).rejects.toThrow('No response body');
      
      // Restore console.error
      console.error = originalConsoleError;
    });
  });

  describe('fetchConversations', () => {
    it('fetches conversations', async () => {
      const mockConversations = [{ id: '1', title: 'Test' }];
      axios.get.mockResolvedValueOnce({ data: mockConversations });
      
      const response = await fetchConversations();
      
      expect(axios.get).toHaveBeenCalledWith('/conversations/');
      expect(response).toEqual(mockConversations);
    });

    it('throws an error when fetching conversations fails', async () => {
      const error = new Error('Network Error');
      axios.get.mockRejectedValueOnce(error);
      
      // Mock console.error to prevent error logs in test output
      const originalConsoleError = console.error;
      console.error = jest.fn();
      
      await expect(fetchConversations()).rejects.toThrow(error);
      
      // Restore console.error
      console.error = originalConsoleError;
    });
  });

  describe('fetchConversation', () => {
    it('fetches a conversation by ID', async () => {
      const conversationId = 'conv1';
      const mockConversation = { 
        id: conversationId, 
        title: 'Test',
        messages: [{ id: '1', content: 'Hello' }] 
      };
      
      axios.get.mockResolvedValueOnce({ data: mockConversation });
      
      const response = await fetchConversation(conversationId);
      
      expect(axios.get).toHaveBeenCalledWith(`/conversations/${conversationId}`);
      expect(response).toEqual(mockConversation);
    });

    it('throws an error when fetching a conversation fails', async () => {
      const conversationId = 'nonexistent';
      const error = new Error('Not Found');
      
      // Mock console.error to prevent error logs in test output
      const originalConsoleError = console.error;
      console.error = jest.fn();
      
      axios.get.mockRejectedValueOnce(error);
      
      await expect(fetchConversation(conversationId)).rejects.toThrow(error);
      
      // Restore console.error
      console.error = originalConsoleError;
    });
  });

  describe('createConversation', () => {
    it('creates a new conversation', async () => {
      const title = 'New Chat';
      const mockConversation = { id: 'new', title, messages: [], model: 'gpt-4', provider: 'openai' };
      axios.post.mockResolvedValueOnce({ data: mockConversation });
      
      const response = await createConversation(title);
      
      expect(axios.post).toHaveBeenCalledWith(
        '/conversations/',
        {
          title,
          messages: [],
          model: 'gpt-4',
          provider: 'openai'
        }
      );
      expect(response).toEqual(mockConversation);
    });

    it('creates a conversation with custom model and provider', async () => {
      const title = 'Custom Model Chat';
      const model = 'gpt-3.5-turbo';
      const provider = 'azure';
      const mockConversation = { id: 'custom', title, messages: [], model, provider };
      axios.post.mockResolvedValueOnce({ data: mockConversation });
      
      const response = await createConversation(title, model, provider);
      
      expect(axios.post).toHaveBeenCalledWith(
        '/conversations/',
        {
          title,
          messages: [],
          model,
          provider
        }
      );
      expect(response).toEqual(mockConversation);
    });

    it('throws an error when creation fails', async () => {
      const error = new Error('Failed to create conversation');
      
      // Mock console.error to prevent error logs in test output
      const originalConsoleError = console.error;
      console.error = jest.fn();
      
      axios.post.mockRejectedValueOnce(error);
      
      await expect(createConversation('Test')).rejects.toThrow(error);
      
      // Restore console.error
      console.error = originalConsoleError;
    });
  });

  describe('deleteConversation', () => {
    it('deletes a conversation', async () => {
      const conversationId = 'conv1';
      axios.delete.mockResolvedValueOnce({ data: {} });
      
      await deleteConversation(conversationId);
      
      expect(axios.delete).toHaveBeenCalledWith(`/conversations/${conversationId}`);
    });

    it('throws an error when deletion fails', async () => {
      const conversationId = 'nonexistent';
      const error = new Error('Not Found');
      
      // Mock console.error to prevent error logs in test output
      const originalConsoleError = console.error;
      console.error = jest.fn();
      
      axios.delete.mockRejectedValueOnce(error);
      
      await expect(deleteConversation(conversationId)).rejects.toThrow(error);
      
      // Restore console.error
      console.error = originalConsoleError;
    });
  });

  describe('updateConversation', () => {
    it('updates a conversation', async () => {
      const conversationId = 'conv1';
      const updates = { title: 'Updated Title' };
      const updatedConversation = { id: conversationId, ...updates };
      
      axios.put.mockResolvedValueOnce({ data: updatedConversation });
      
      const response = await updateConversation(conversationId, updates);
      
      expect(axios.put).toHaveBeenCalledWith(
        `/conversations/${conversationId}`,
        updates
      );
      expect(response).toEqual(updatedConversation);
    });

    it('throws an error when update fails', async () => {
      const conversationId = 'nonexistent';
      const updates = { title: 'Updated Title' };
      const error = new Error('Not Found');
      
      // Mock the console.error to prevent error logs from cluttering the test output
      const originalConsoleError = console.error;
      console.error = jest.fn();
      
      axios.put.mockRejectedValueOnce(error);
      
      // The actual implementation throws the original error
      await expect(updateConversation(conversationId, updates)).rejects.toThrow(error);
      
      // Restore the original console.error
      console.error = originalConsoleError;
    });
  });
});
