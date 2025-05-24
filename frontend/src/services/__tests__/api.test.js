import { sendChatRequest, fetchConversations, fetchConversation } from '../api';

// Mock axios
jest.mock('axios', () => ({
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  create: jest.fn(function() { return this; })
}));

// Add TextEncoder and TextDecoder polyfills for Node.js test environment
if (typeof TextEncoder === 'undefined') {
  global.TextEncoder = require('util').TextEncoder;
}
if (typeof TextDecoder === 'undefined') {
  global.TextDecoder = require('util').TextDecoder;
}

describe('API Service', () => {
  const originalFetch = global.fetch;
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Set up default fetch mock
    global.fetch = jest.fn();
    
    // Set up default axios mocks
    const axios = require('axios');
    axios.get.mockResolvedValue({ data: {} });
    axios.post.mockResolvedValue({ data: {} });
    axios.put.mockResolvedValue({ data: {} });
    axios.delete.mockResolvedValue({ data: {} });
    
    // Set up default fetch mock implementation
    global.fetch.mockImplementation(() => 
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve({ data: {} })
      })
    );
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  afterAll(() => {
    global.fetch = originalFetch;
    jest.restoreAllMocks();
  });

  describe('sendChatRequest', () => {
    it('sends a chat request with the correct parameters', async () => {
      const messages = [{ role: 'user', content: 'Hello, world!' }];
      const onChunk = jest.fn();
      const mockResponse = { id: '1', content: 'Response' };
      
      // Mock the fetch implementation used by sendChatRequest
      const mockReader = {
        read: jest.fn()
          .mockResolvedValueOnce({
            done: false,
            value: new TextEncoder().encode(`data: ${JSON.stringify(mockResponse)}\n\n`)
          })
          .mockResolvedValueOnce({
            done: true
          })
      };
      
      const mockFetchResponse = {
        ok: true,
        body: {
          getReader: () => mockReader
        }
      };
      
      global.fetch = jest.fn().mockResolvedValue(mockFetchResponse);
      
      await sendChatRequest(messages, onChunk);
      
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/chat'),
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            messages,
            stream: true,
          }),
        })
      );
    });
  });

  describe('fetchConversations', () => {
    it('fetches conversations', async () => {
      const mockConversations = [{ id: '1', title: 'Test' }];
      
      // Mock axios.get since fetchConversations uses axios
      const mockAxios = require('axios');
      mockAxios.get.mockResolvedValueOnce({ data: mockConversations });
      
      const result = await fetchConversations();
      
      expect(mockAxios.get).toHaveBeenCalledWith('/conversations/');
      expect(result).toEqual(mockConversations);
    });
  });

  describe('fetchConversation', () => {
    it('fetches a conversation by ID', async () => {
      const conversationId = 'conv1';
      const mockConversation = { id: conversationId, title: 'Test', messages: [] };
      
      // Mock axios.get since fetchConversation uses axios
      const mockAxios = require('axios');
      mockAxios.get.mockResolvedValueOnce({ data: mockConversation });
      
      const result = await fetchConversation(conversationId);
      
      expect(mockAxios.get).toHaveBeenCalledWith(`/conversations/${conversationId}`);
      expect(result).toEqual(mockConversation);
    });
  });
});
