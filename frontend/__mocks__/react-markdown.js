// Simple mock for react-markdown that just renders its children
const React = require('react');

const ReactMarkdown = ({ children, components = {} }) => {
  // If there's a code block, render it with the provided components or as a pre tag
  if (children && typeof children === 'string' && children.includes('```')) {
    const codeMatch = children.match(/```(\w+)?\n([\s\S]*?)\n```/);
    if (codeMatch) {
      const [, language, code] = codeMatch;
      const CodeBlock = components.code || (({ children }) => (
        <pre><code>{children}</code></pre>
      ));
      return (
        <CodeBlock className={`language-${language || ''}`}>
          {code}
        </CodeBlock>
      );
    }
  }
  
  // Otherwise just render the content in a div
  return <div>{children}</div>;
};

module.exports = ReactMarkdown;
