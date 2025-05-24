import React from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MessageInput from '../MessageInput';

describe('MessageInput', () => {
  const mockOnSend = jest.fn();
  const mockOnStop = jest.fn();
  
  beforeEach(() => {
    mockOnSend.mockClear();
    mockOnStop.mockClear();
  });

  it('renders the input and buttons', () => {
    render(<MessageInput onSend={mockOnSend} onStop={mockOnStop} isSending={false} />);
    
    expect(screen.getByPlaceholderText('Type your message...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  it('allows typing a message', () => {
    render(<MessageInput onSend={mockOnSend} onStop={mockOnStop} isSending={false} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    fireEvent.change(input, { target: { value: 'Hello, world!' } });
    
    expect(input.value).toBe('Hello, world!');
  });

  it('calls onSend when send button is clicked', async () => {
    const user = userEvent.setup();
    render(<MessageInput onSend={mockOnSend} onStop={mockOnStop} isSending={false} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await act(async () => {
      await user.type(input, 'Test message');
      await user.click(sendButton);
    });
    
    expect(mockOnSend).toHaveBeenCalledWith('Test message');
  });

  it('calls onSend when Enter is pressed', async () => {
    const user = userEvent.setup();
    render(<MessageInput onSend={mockOnSend} onStop={mockOnStop} isSending={false} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    
    await act(async () => {
      await user.type(input, 'Test message{enter}');
    });
    
    expect(mockOnSend).toHaveBeenCalledWith('Test message');
  });

  it('does not send empty messages', async () => {
    const user = userEvent.setup();
    render(<MessageInput onSend={mockOnSend} onStop={mockOnStop} isSending={false} />);
    
    const input = screen.getByPlaceholderText('Type your message...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await act(async () => {
      await user.type(input, '   ');
      await user.click(sendButton);
    });
    
    expect(mockOnSend).not.toHaveBeenCalled();
  });

  it('shows sending state when isSending is true', () => {
    render(<MessageInput onSend={mockOnSend} onStop={mockOnStop} isSending={true} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Sending...');
    expect(button).toBeDisabled();
  });

  it('disables input and buttons when isSending is true', () => {
    render(<MessageInput onSend={mockOnSend} onStop={mockOnStop} isSending={true} />);
    
    const input = screen.getByPlaceholderText('Please wait for the response...');
    const button = screen.getByRole('button');
    
    expect(input).toBeDisabled();
    expect(button).toBeDisabled();
    expect(button).toHaveTextContent('Sending...');
  });
});
