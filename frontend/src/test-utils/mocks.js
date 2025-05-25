// Mock data for tests
export const mockMessages = [
  {
    id: '1',
    role: 'user',
    content: 'Hello, how are you?',
    timestamp: '2023-05-21T10:00:00Z',
  },
  {
    id: '2',
    role: 'assistant',
    content: 'I am doing well, thank you!',
    timestamp: '2023-05-21T10:00:05Z',
  },
];

export const mockConversations = [
  {
    id: 'conv1',
    title: 'First Conversation',
    updatedAt: '2023-05-21T10:00:00Z',
  },
  {
    id: 'conv2',
    title: 'Second Conversation',
    updatedAt: '2023-05-21T11:00:00Z',
  },
];

// Mock API responses
export const mockApiResponses = {
  getConversations: {
    success: {
      data: mockConversations,
    },
  },
  getMessages: {
    success: (conversationId) => ({
      data: mockMessages.filter(msg => msg.conversationId === conversationId || !msg.conversationId),
    }),
  },
  sendMessage: {
    success: (content) => ({
      data: {
        id: `msg-${Date.now()}`,
        role: 'assistant',
        content: `Response to: ${content}`,
        timestamp: new Date().toISOString(),
      },
    }),
  },
};

// Mock the API module
export const mockApi = {
  getConversations: jest.fn(),
  getMessages: jest.fn(),
  sendMessage: jest.fn(),
  // Add other API methods as needed
};

// Mock the useChat hook
export const mockUseChat = {
  messages: mockMessages,
  conversations: mockConversations,
  isLoading: false,
  error: null,
  sendMessage: jest.fn(),
  selectConversation: jest.fn(),
  createNewConversation: jest.fn(),
  currentConversationId: 'conv1',
};

// Mock the window.matchMedia function
export const mockMatchMedia = () => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: jest.fn().mockImplementation(query => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    })),
  });
};

// Mock the IntersectionObserver
export const mockIntersectionObserver = () => {
  // Mock IntersectionObserver
  class MockIntersectionObserver {
    constructor() {}
    disconnect() {}
    observe() {}
    unobserve() {}
    takeRecords() { return []; }
  }
  
  Object.defineProperty(window, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: MockIntersectionObserver,
  });
  
  Object.defineProperty(global, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: MockIntersectionObserver,
  });
};
