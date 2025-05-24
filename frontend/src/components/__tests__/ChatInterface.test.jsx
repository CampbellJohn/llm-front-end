import React from 'react';
import { render, screen, fireEvent } from '../../test-utils';
import ChatInterface from '../ChatInterface';

describe('ChatInterface', () => {
  const mockMessages = [
    { role: 'user', content: 'Hello' },
    { role: 'assistant', content: 'Hi there!' },
  ];

  const mockSendMessage = jest.fn();
  const mockClearMessages = jest.fn();

  const defaultProps = {
    messages: mockMessages,
    isLoading: false,
    isStreaming: false,
    error: null,
    sendMessage: mockSendMessage,
    clearMessages: mockClearMessages,
  };

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders chat interface with messages', () => {
    render(<ChatInterface {...defaultProps} />);
    
    // Check if messages are rendered
    expect(screen.getByText('Hello')).toBeInTheDocument();
    expect(screen.getByText('Hi there!')).toBeInTheDocument();
  });

  it('shows welcome message when no messages', () => {
    render(<ChatInterface {...defaultProps} messages={[]} />);
    
    expect(screen.getByText('Welcome!')).toBeInTheDocument();
    expect(screen.getByText('This is a custom, scalable LLM front-end.')).toBeInTheDocument();
  });

  it('shows error message when error exists', () => {
    const errorMessage = 'An error occurred';
    render(<ChatInterface {...defaultProps} error={errorMessage} />);
    
    // The error message is split across multiple elements, so we need to check for the error container
    const errorContainer = screen.getByText(/Error:/).closest('div');
    expect(errorContainer).toHaveTextContent(errorMessage);
  });

  it('calls sendMessage when message is submitted', () => {
    render(<ChatInterface {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    // Type a message
    fireEvent.change(input, { target: { value: 'New message' } });
    
    // Send the message
    fireEvent.click(sendButton);
    
    // Check if sendMessage was called with the correct message
    expect(mockSendMessage).toHaveBeenCalledWith('New message');
  });

  it('shows loading state when isLoading is true', () => {
    render(<ChatInterface {...defaultProps} isLoading={true} />);
    
    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
  });

  it('shows streaming state when isStreaming is true', () => {
    render(<ChatInterface {...defaultProps} isStreaming={true} />);
    
    const input = screen.getByRole('textbox');
    expect(input).toBeDisabled();
  });
});
