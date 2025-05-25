import React from 'react';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MessageInput from '../MessageInput';

// Mock the auto-resize effect
jest.mock('react', () => {
  const originReact = jest.requireActual('react');
  return {
    ...originReact,
    useEffect: (effect) => effect(), // Run effects immediately
  };
});

describe('MessageInput', () => {
  const onSend = jest.fn();
  const onStop = jest.fn();
  
  const renderComponent = (props = {}) => {
    return render(
      <MessageInput
        onSend={onSend}
        onStop={onStop}
        isSending={false}
        {...props}
      />
    );
  };

  beforeEach(() => {
    onSend.mockClear();
    onStop.mockClear();
  });

  it('renders the input and send button', () => {
    renderComponent();
    
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
    expect(screen.queryByRole('button', { name: /stop/i })).not.toBeInTheDocument();
  });

  it('calls onSend when the send button is clicked', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /send/i });
    
    await act(async () => {
      await user.type(input, 'Hello, world!');
      await user.click(button);
    });
    
    expect(onSend).toHaveBeenCalledWith('Hello, world!');
    expect(input).toHaveValue('');
  });

  it('calls onSend when Enter is pressed', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    const input = screen.getByRole('textbox');
    
    await act(async () => {
      await user.type(input, 'Hello, world!');
      await user.keyboard('{Enter}');
    });
    
    expect(onSend).toHaveBeenCalledWith('Hello, world!');
    expect(input).toHaveValue('');
  });

  it('does not call onSend for empty messages', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    const input = screen.getByRole('textbox');
    const button = screen.getByRole('button', { name: /send/i });
    
    await act(async () => {
      // Try sending empty message
      await user.click(button);
      
      // Try sending message with only whitespace
      await user.type(input, '   ');
      await user.click(button);
    });
    
    expect(onSend).not.toHaveBeenCalled();
  });

  it('shows sending state when isSending is true', async () => {
    await act(async () => {
      renderComponent({ isSending: true });
    });
    
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Sending...');
    expect(button).toBeDisabled();
  });

  it('disables the input when isSending is true', async () => {
    await act(async () => {
      renderComponent({ isSending: true });
    });
    
    expect(screen.getByRole('textbox')).toBeDisabled();
  });

  it('allows multiline input with Shift+Enter', async () => {
    const user = userEvent.setup();
    renderComponent();
    
    const input = screen.getByRole('textbox');
    
    // Type a message with Shift+Enter for new line
    await act(async () => {
      await user.type(input, 'Hello,');
      await user.keyboard('{Shift>}{Enter}');
      await user.type(input, 'world!');
    });
    
    // The input should now contain the newline
    expect(input.value).toBe('Hello,\nworld!');
    
    // Press Enter to send
    await act(async () => {
      await user.keyboard('{Enter}');
    });
    
    // Should send the message with the newline
    expect(onSend).toHaveBeenCalledWith('Hello,\nworld!');
  });

  it('handles pasted text correctly', async () => {
    const user = userEvent.setup();
    await act(async () => {
      renderComponent();
    });
    
    const input = screen.getByRole('textbox');
    
    // Focus the input
    input.focus();
    
    // Simulate paste event
    await act(async () => {
      await user.paste('Pasted text');
    });
    
    // The input should now contain the pasted text
    expect(input).toHaveValue('Pasted text');
  });
});
