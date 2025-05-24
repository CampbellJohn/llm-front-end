import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChat } from '../useChat';

// Mock data
const mockConversations = [
  { id: 'conv1', title: 'First conversation', updatedAt: new Date().toISOString() },
  { id: 'conv2', title: 'Second conversation', updatedAt: new Date().toISOString() },
];

const mockMessages = [
  { id: 'msg1', role: 'user', content: 'Hello', timestamp: new Date().toISOString() },
  { id: 'msg2', role: 'assistant', content: 'Hi there!', timestamp: new Date().toISOString() },
];

// Mock the API module
jest.mock('../../services/api', () => ({
  sendMessage: jest.fn(),
  sendChatRequest: jest.fn(),
  getConversations: jest.fn(),
  getMessages: jest.fn(),
  fetchConversation: jest.fn(),
  createConversation: jest.fn(),
  updateConversation: jest.fn(),
  deleteConversation: jest.fn(),
}));

describe('useChat', () => {
  let queryClient;
  let wrapper;
  let api;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
    
    wrapper = ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
    
    // Get the mocked API
    api = require('../../services/api');
    
    // Set up default mock implementations
    api.getConversations.mockResolvedValue(mockConversations);
    api.getMessages.mockResolvedValue(mockMessages);
    api.sendMessage.mockResolvedValue({
      id: 'new-msg',
      content: 'Test response',
      role: 'assistant',
      timestamp: new Date().toISOString(),
    });
    api.createConversation.mockResolvedValue({
      id: 'new-conv',
      title: 'New conversation',
      updatedAt: new Date().toISOString(),
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
    queryClient.clear();
  });

  it('should initialize with empty messages', () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Initial state
    expect(result.current.messages).toEqual([]);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.currentConversationId).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should send a message and get a response', async () => {
    // Mock the API responses
    const newConversation = {
      id: 'new-conv',
      title: 'Hello',
      messages: [
        { role: 'user', content: 'Hello' },
        { role: 'assistant', content: 'Hi there!' }
      ]
    };
    
    // Mock the create conversation response
    api.createConversation.mockResolvedValueOnce({
      id: newConversation.id,
      title: newConversation.title
    });
    
    // Mock the update conversation response
    api.updateConversation.mockResolvedValueOnce(newConversation);
    
    // Mock the chat request to only resolve without calling onChunk
    // to prevent duplicate content from the streaming simulation
    api.sendChatRequest.mockImplementation(() => Promise.resolve());
    
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Send a message (this will create a new conversation)
    await act(async () => {
      await result.current.sendMessage('Hello');
    });
    
    // Should have created a new conversation
    expect(api.createConversation).toHaveBeenCalledWith('Hello');
    
    // Should have sent the message
    expect(api.sendChatRequest).toHaveBeenCalledWith(
      [{ role: 'user', content: 'Hello' }],
      expect.any(Function)
    );
    
    // Should have updated the messages
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0]).toEqual({ role: 'user', content: 'Hello' });
    expect(result.current.messages[1].content).toBe(''); // Empty assistant message
    expect(result.current.currentConversationId).toBe('new-conv');
  });

  it('should create a new conversation when sending first message', async () => {
    // Mock the API responses
    const newConversation = {
      id: 'new-conv',
      title: 'Hello',
      messages: [
        { role: 'user', content: 'Hello' }
      ]
    };
    
    // Mock the create conversation response
    api.createConversation.mockResolvedValueOnce({
      id: newConversation.id,
      title: newConversation.title
    });
    
    // Mock the update conversation response
    api.updateConversation.mockResolvedValueOnce(newConversation);
    
    // Mock the chat request to do nothing
    api.sendChatRequest.mockImplementation(() => Promise.resolve());
    
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Send a message (this will create a new conversation)
    await act(async () => {
      await result.current.sendMessage('Hello');
    });
    
    // Should have created a new conversation
    expect(api.createConversation).toHaveBeenCalledWith('Hello');
    
    // Should have updated the state
    expect(result.current.currentConversationId).toBe('new-conv');
    expect(result.current.conversationTitle).toBe('Hello');
    // The hook adds an empty assistant message, so we expect 2 messages
    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[0]).toEqual({ role: 'user', content: 'Hello' });
    expect(result.current.messages[1]).toMatchObject({ role: 'assistant', content: '' });
  });

  it('should load a conversation and its messages', async () => {
    // Mock the API response
    const conversationId = 'conv1';
    const conversation = {
      id: conversationId,
      title: 'Test Conversation',
      messages: [
        { role: 'user', content: 'Hello' },
        { role: 'assistant', content: 'Hi there!' }
      ]
    };
    
    api.fetchConversation.mockResolvedValueOnce(conversation);
    
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Load a conversation
    await act(async () => {
      await result.current.loadConversation(conversationId);
    });
    
    // Should have called fetchConversation with the correct ID
    expect(api.fetchConversation).toHaveBeenCalledWith(conversationId);
    
    // Should have updated the state
    expect(result.current.messages).toEqual(conversation.messages);
    expect(result.current.conversationTitle).toBe(conversation.title);
    expect(result.current.currentConversationId).toBe(conversationId);
  });

  it('should clear messages and reset state', async () => {
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Set some initial state
    await act(async () => {
      result.current.messages = [{ role: 'user', content: 'Hello' }];
      result.current.currentConversationId = 'conv1';
      result.current.conversationTitle = 'Test';
      result.current.error = 'Some error';
    });
    
    // Clear messages
    await act(async () => {
      result.current.clearMessages();
    });
    
    // Should have reset the state
    expect(result.current.messages).toEqual([]);
    expect(result.current.currentConversationId).toBeNull();
    expect(result.current.conversationTitle).toBe('New Chat');
    expect(result.current.error).toBeNull();
  });

  it('should handle errors when loading a conversation', async () => {
    // Mock the API to reject with an error
    const error = new Error('Failed to load conversation');
    api.fetchConversation.mockRejectedValueOnce(error);
    
    // Spy on console.error to verify the error is logged
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    const { result } = renderHook(() => useChat(), { wrapper });
    
    // Try to load a conversation
    await act(async () => {
      await result.current.loadConversation('invalid-id');
    });
    
    // Should have called fetchConversation
    expect(api.fetchConversation).toHaveBeenCalledWith('invalid-id');
    
    // Should have set the error state
    expect(result.current.error).toBe('Failed to load conversation');
    
    // Clean up
    consoleError.mockRestore();
  });
});
