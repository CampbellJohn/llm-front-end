// Mock for react-syntax-highlighter
const React = require('react');

const Prism = ({ children, language, style, ...props }) => (
  <pre className={`language-${language}`} style={style} {...props}>
    <code>{children}</code>
  </pre>
);

// Mock the default export
const mockSyntaxHighlighter = {
  Prism: Prism,
  default: Prism
};

module.exports = mockSyntaxHighlighter;
