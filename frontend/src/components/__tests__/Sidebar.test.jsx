import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '../../test-utils';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Sidebar from '../Sidebar';
import * as api from '../../services/api';

// Mock the API module
jest.mock('../../services/api');

// Mock console.log to clean up test output
const originalConsoleLog = console.log;
beforeAll(() => {
  console.log = jest.fn(); // Suppress console.log during tests
});

afterAll(() => {
  console.log = originalConsoleLog;
});

// Create a custom render function that includes the QueryClientProvider
const renderWithProviders = (ui, options = {}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>,
    options
  );
};

describe('Sidebar', () => {
  const mockConversations = [
    { id: '1', title: 'First Conversation', updatedAt: '2023-05-21T10:00:00Z' },
    { id: '2', title: 'Second Conversation', updatedAt: '2023-05-21T11:00:00Z' },
  ];

  const mockOnNewChat = jest.fn();
  const mockOnSelectConversation = jest.fn();

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Mock the API responses
    api.fetchConversations.mockResolvedValue(mockConversations);
    api.deleteConversation.mockResolvedValue({});
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
  });

  it('renders the sidebar with conversations', async () => {
    await act(async () => {
      renderWithProviders(
        <Sidebar
          onNewChat={mockOnNewChat}
          onSelectConversation={mockOnSelectConversation}
          currentConversationId="1"
          refreshTrigger={0}
        />
      );
    });

    // Wait for the loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      expect(screen.getByText('First Conversation')).toBeInTheDocument();
    });

    // Check if conversations are rendered
    expect(screen.getByText('First Conversation')).toBeInTheDocument();
    expect(screen.getByText('Second Conversation')).toBeInTheDocument();
    
    // Check if new chat button is rendered
    expect(screen.getByText(/new chat/i)).toBeInTheDocument();
  });

  it('highlights the current conversation', async () => {
    await act(async () => {
      renderWithProviders(
        <Sidebar
          onNewChat={mockOnNewChat}
          onSelectConversation={mockOnSelectConversation}
          currentConversationId="1"
          refreshTrigger={0}
        />
      );
    });

    // Wait for the loading to complete and initial data to be loaded
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      expect(screen.getByText('First Conversation')).toBeInTheDocument();
    });

    // The first conversation should be highlighted
    const firstConversation = screen.getByText('First Conversation').closest('li');
    expect(firstConversation).toHaveStyle({ backgroundColor: 'rgb(230, 215, 169)' });
    
    // The second conversation should not be highlighted
    const secondConversation = screen.getByText('Second Conversation').closest('li');
    expect(secondConversation).not.toHaveStyle({ backgroundColor: 'rgb(230, 215, 169)' });
  });

  it('calls onNewChat when new chat button is clicked', async () => {
    renderWithProviders(
      <Sidebar
        onNewChat={mockOnNewChat}
        onSelectConversation={mockOnSelectConversation}
        currentConversationId="1"
        refreshTrigger={0}
      />
    );

    // Wait for the loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    const newChatButton = screen.getByRole('button', { name: /new chat/i });
    await act(async () => {
      fireEvent.click(newChatButton);
    });
    
    expect(mockOnNewChat).toHaveBeenCalled();
  });

  it('calls onSelectConversation when a conversation is clicked', async () => {
    renderWithProviders(
      <Sidebar
        onNewChat={mockOnNewChat}
        onSelectConversation={mockOnSelectConversation}
        currentConversationId="1"
        refreshTrigger={0}
      />
    );

    // Wait for the loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    const secondConversation = screen.getByText('Second Conversation');
    await act(async () => {
      fireEvent.click(secondConversation);
    });
    
    expect(mockOnSelectConversation).toHaveBeenCalledWith('2');
  });

  it('deletes a conversation when delete button is clicked', async () => {
    // Mock the confirm dialog to return true
    const mockConfirm = jest.spyOn(window, 'confirm').mockImplementation(() => true);
    
    // Mock the delete API
    api.deleteConversation.mockResolvedValueOnce({});
    
    // Render the component
    let container;
    await act(async () => {
      const { container: renderedContainer } = renderWithProviders(
        <Sidebar
          onNewChat={mockOnNewChat}
          onSelectConversation={mockOnSelectConversation}
          currentConversationId="1"
          refreshTrigger={0}
        />
      );
      container = renderedContainer;
    });

    // Wait for the loading to complete and initial data to be loaded
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      expect(screen.getByText('First Conversation')).toBeInTheDocument();
    });

    // Find the first conversation item
    const firstConversation = screen.getByText('First Conversation').closest('li');
    
    // Hover over the conversation to make the delete button visible
    await act(async () => {
      fireEvent.mouseEnter(firstConversation);
    });
    
    // Wait for the hover effect to be applied and find the delete button
    let deleteButton;
    await waitFor(() => {
      const buttons = screen.getAllByRole('button', { name: /delete conversation/i });
      expect(buttons.length).toBeGreaterThan(0);
      deleteButton = buttons[0];
    });
    
    // Click the delete button
    await act(async () => {
      fireEvent.click(deleteButton);
    });
    
    // Check if the confirmation dialog was shown
    expect(mockConfirm).toHaveBeenCalledWith('Are you sure you want to delete this conversation?');
    
    // Wait for the delete API to be called with the correct ID
    await waitFor(() => {
      expect(api.deleteConversation).toHaveBeenCalledWith('1');
    });
    
    // Clean up
    mockConfirm.mockRestore();
  });

  it('shows empty state when there are no conversations', async () => {
    // Mock empty conversations
    api.fetchConversations.mockResolvedValueOnce([]);
    
    renderWithProviders(
      <Sidebar
        onNewChat={mockOnNewChat}
        onSelectConversation={mockOnSelectConversation}
        currentConversationId={null}
        refreshTrigger={0}
      />
    );

    // Wait for the loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
      expect(screen.getByText('No conversations yet')).toBeInTheDocument();
    });
  });
});
