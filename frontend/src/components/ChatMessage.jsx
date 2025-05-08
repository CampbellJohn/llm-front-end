import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

const ChatMessage = ({ message, isLastMessage }) => {
  const { role, content } = message;
  const isUser = role === 'user';
  
  // Custom renderers for markdown
  const renderers = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={atomDark}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    }
  };

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      id={isLastMessage ? 'last-message' : undefined}
    >
      <div className={`message-container ${isUser ? 'user-message' : 'assistant-message'}`}>
        <div className="text-sm font-medium text-gray-500 mb-1">
          {isUser ? 'You' : 'Assistant'}
        </div>
        <div className="prose max-w-none">
          <ReactMarkdown components={renderers}>{content}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;