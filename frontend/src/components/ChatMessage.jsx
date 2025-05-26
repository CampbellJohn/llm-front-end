import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { FaCopy, FaCheck } from 'react-icons/fa';

const CodeBlock = ({ language, value }) => {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="relative my-2 rounded-lg overflow-hidden">
      <div 
        className="flex justify-between items-center text-gray-300 text-xs px-4 py-2"
        style={{ backgroundColor: 'var(--color-dark)' }}
      >
        <span className="font-mono text-xs">{language || 'code'}</span>
        <button
          onClick={copyToClipboard}
          className="flex items-center gap-1 px-2 py-1 rounded hover:bg-opacity-50 hover:bg-gray-700 transition-colors text-xs"
          title="Copy to clipboard"
        >
          {copied ? (
            <>
              <FaCheck className="text-green-400" />
              <span className="text-xs">Copied!</span>
            </>
          ) : (
            <>
              <FaCopy className="text-xs" />
              <span className="text-xs">Copy</span>
            </>
          )}
        </button>
      </div>
      <SyntaxHighlighter
        language={language}
        style={atomDark}
        customStyle={{
          margin: 0,
          padding: '1rem',
          fontSize: '0.875rem',
          lineHeight: '1.5',
          borderRadius: '0 0 0.5rem 0.5rem',
          backgroundColor: 'var(--color-dark)',
        }}
        showLineNumbers={value.split('\n').length > 5}
        wrapLines={true}
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
};

const ChatMessage = ({ message, isLastMessage }) => {
  const { role, content } = message;
  const isUser = role === 'user';
  
  // Custom renderers for markdown
  const renderers = {
    // Code block rendering
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      const language = match ? match[1] : '';
      
      return !inline ? (
        <CodeBlock 
          language={language} 
          value={String(children).replace(/\n$/, '')} 
        />
      ) : (
        <code className="bg-gray-200 dark:bg-gray-700 px-1.5 py-0.5 rounded text-sm font-mono">
          {children}
        </code>
      );
    },
    // Headers
    h1: ({node, ...props}) => <h1 className="text-2xl font-bold my-4" {...props} />,
    h2: ({node, ...props}) => <h2 className="text-xl font-bold my-3" {...props} />,
    h3: ({node, ...props}) => <h3 className="text-lg font-semibold my-2.5" {...props} />,
    h4: ({node, ...props}) => <h4 className="text-base font-semibold my-2" {...props} />,
    // Paragraphs
    p: ({node, ...props}) => <p className="my-3 leading-relaxed" {...props} />,
    // Lists
    ul: ({node, ...props}) => <ul className="list-disc pl-6 my-3 space-y-1.5" {...props} />,
    ol: ({node, ...props}) => <ol className="list-decimal pl-6 my-3 space-y-1.5" {...props} />,
    // List items
    li: ({node, ordered, ...props}) => (
      <li className={ordered ? 'mb-1' : 'mb-1'} {...props} />
    ),
    // Blockquotes
    blockquote: ({node, ...props}) => (
      <blockquote 
        className="border-l-4 border-gray-300 pl-4 my-4 text-gray-700 dark:text-gray-300"
        {...props} 
      />
    ),
    // Links
    a: ({node, ...props}) => (
      <a 
        className="text-blue-600 dark:text-blue-400 hover:underline" 
        target="_blank" 
        rel="noopener noreferrer"
        {...props} 
      />
    ),
  };

  return (
    <div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}
      id={isLastMessage ? 'last-message' : undefined}
    >
      <div className={`message-container ${isUser ? 'user-message' : 'assistant-message'}`}>
        <div className="text-sm font-medium mb-2" style={{ color: isUser ? '#25293c' : '#f9fefc' }}>
          {isUser ? 'You' : 'Assistant'}
        </div>
        <div className="prose max-w-none">
          <ReactMarkdown components={renderers}>
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;