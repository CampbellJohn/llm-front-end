import React from 'react';
import { render, screen } from '../../test-utils';
import ChatMessage from '../ChatMessage';

// Mock react-markdown and react-syntax-highlighter
jest.mock('react-markdown', () => ({
  __esModule: true,
  default: ({ children }) => <div data-testid="mock-markdown">{children}</div>,
}));

jest.mock('react-syntax-highlighter', () => ({
  Prism: ({ children, language, style }) => (
    <pre className={`language-${language}`} style={style} data-testid="syntax-highlighter">
      <code>{children}</code>
    </pre>
  ),
}));

describe('ChatMessage', () => {
  const mockMessage = {
    id: '1',
    role: 'user',
    content: 'Hello, world!',
    timestamp: new Date().toISOString(),
  };

  it('renders user message correctly', () => {
    render(<ChatMessage message={mockMessage} />);
    
    expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    expect(screen.getByText('You')).toBeInTheDocument();
    
    // Check the message container has the right alignment
    const messageDiv = screen.getByText('Hello, world!').closest('div[class*="flex"]');
    expect(messageDiv).toHaveClass('justify-end');
  });

  it('renders assistant message correctly', () => {
    const assistantMessage = { ...mockMessage, role: 'assistant' };
    render(<ChatMessage message={assistantMessage} />);
    
    expect(screen.getByText('Hello, world!')).toBeInTheDocument();
    expect(screen.getByText('Assistant')).toBeInTheDocument();
    
    // Check the message container has the right alignment
    const messageDiv = screen.getByText('Hello, world!').closest('div[class*="flex"]');
    expect(messageDiv).toHaveClass('justify-start');
  });

  it('passes markdown content to react-markdown', () => {
    const markdownContent = 'This is **bold** text and `inline code`';
    const markdownMessage = {
      ...mockMessage,
      content: markdownContent
    };
    render(<ChatMessage message={markdownMessage} />);
    
    // Check that the raw markdown content is passed to react-markdown
    const markdownElement = screen.getByTestId('mock-markdown');
    expect(markdownElement).toHaveTextContent(markdownContent);
  });
  
  it('passes code blocks to react-markdown', () => {
    const codeContent = 'const hello = "world";';
    const codeMessage = {
      ...mockMessage,
      content: `\`\`\`javascript\n${codeContent}\n\`\`\``
    };
    render(<ChatMessage message={codeMessage} />);
    
    // Check that the code block content is passed to react-markdown
    const markdownElement = screen.getByTestId('mock-markdown');
    expect(markdownElement).toHaveTextContent(codeContent);
  });
  
  it('adds last message ID when isLastMessage is true', () => {
    render(<ChatMessage message={mockMessage} isLastMessage={true} />);
    
    const messageDiv = screen.getByText('Hello, world!').closest('div[class*="flex"]');
    expect(messageDiv).toHaveAttribute('id', 'last-message');
  });
});
