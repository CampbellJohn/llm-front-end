import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import App from '../App';
import * as api from '../services/api';

// Mock the ChatInterface component
jest.mock('../components/ChatInterface', () => ({
  __esModule: true,
  default: () => <div data-testid="chat-interface">Chat Interface</div>,
}));

// Mock the API calls
jest.mock('../services/api', () => ({
  fetchConversations: jest.fn(),
  fetchConversation: jest.fn(),
  createConversation: jest.fn(),
  deleteConversation: jest.fn(),
  updateConversation: jest.fn(),
  sendChatRequest: jest.fn(),
}));

// Mock the console.log to avoid cluttering test output
const originalConsole = { ...console };
beforeAll(() => {
  // Suppress expected console errors and logs
  jest.spyOn(console, 'error').mockImplementation((...args) => {
    // Suppress act warnings
    if (typeof args[0] === 'string' && args[0].includes('was not wrapped in act')) {
      return;
    }
    originalConsole.error(...args);
  });
  
  console.log = jest.fn();
});

afterAll(() => {
  // Restore original console methods
  console.log = originalConsole.log;
  console.error = originalConsole.error;
});

const mockConversations = [
  { id: '1', title: 'Test Conversation 1' },
  { id: '2', title: 'Test Conversation 2' },
];

const renderApp = () => {
  let utils;
  
  act(() => {
    utils = render(<App />);
  });
  
  return utils;
};

beforeEach(() => {
  // Reset all mocks before each test
  jest.clearAllMocks();
  
  // Mock the fetchConversations response
  api.fetchConversations.mockResolvedValue(mockConversations);
});

describe('App', () => {
  it('renders the app with header and main content', async () => {
    renderApp();
    
    // Wait for the loading to complete
    await waitFor(() => {
      // Check if the header is rendered
      const header = screen.getByRole('banner');
      expect(header).toBeInTheDocument();
    });
    
    // Check for the new header text
    expect(screen.getByText('New Chat')).toBeInTheDocument();
    
    // Check if the main content area is rendered
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
    
    // Check if the ChatInterface component is rendered
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
  });

  it('renders the sidebar and main content', async () => {
    renderApp();
    
    // Wait for the loading to complete and check for the new chat button
    const newChatButton = await screen.findByRole('button', { name: /new chat/i });
    expect(newChatButton).toBeInTheDocument();
    
    // Verify the button has the correct styling
    expect(newChatButton).toHaveStyle('background-color: rgb(249, 180, 20)');
    
    // Check if the main content area is rendered
    const main = screen.getByRole('main');
    expect(main).toBeInTheDocument();
  });

  it('renders the chat interface with initial state', async () => {
    renderApp();
    
    // Wait for the loading to complete
    const chatInterface = await screen.findByTestId('chat-interface');
    expect(chatInterface).toBeInTheDocument();
    
    // The input field might be in the ChatInterface component which is mocked
    // So we'll just check that the mock is rendered
    expect(chatInterface).toHaveTextContent('Chat Interface');
  });

  it('allows starting a new chat', async () => {
    renderApp();
    
    // Wait for the loading to complete and find the new chat button
    const newChatButton = await screen.findByRole('button', { name: /new chat/i });
    
    // Click the new chat button
    await act(async () => {
      fireEvent.click(newChatButton);
    });
    
    // Check if the header shows 'New Chat'
    expect(screen.getByText('New Chat')).toBeInTheDocument();
    
    // Verify the chat interface is still rendered
    expect(screen.getByTestId('chat-interface')).toBeInTheDocument();
  });
});
