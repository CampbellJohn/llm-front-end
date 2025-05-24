const path = require('path');

module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.(js|jsx|mjs|cjs|ts|tsx)$': './jest-esm-transformer.js',
  },
  // Don't ignore any node_modules for transformation
  transformIgnorePatterns: [
    'node_modules/(?!(axios|@?axios|react-markdown|vfile|unist-util-.*|unified|bail|is-plain-obj|trough|remark-.*|mdast-util-.*|micromark-.*|decode-named-character-reference|character-entities|property-information|hast-util-whitespace|space-separated-tokens|comma-separated-tokens|web-namespaces|hast-util-.*|zwitch|ccount|escape-string-regexp|markdown-table|react-syntax-highlighter)/)',
  ],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1',
    // Mock react-markdown and its ESM dependencies
    'react-markdown': '<rootDir>/__mocks__/react-markdown.js',
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
  ],
  testEnvironmentOptions: {
    url: 'http://localhost',
  },
  modulePaths: ['<rootDir>/src'],
  moduleDirectories: ['node_modules', 'src'],
  // Enable ESM support
  extensionsToTreatAsEsm: ['.jsx', '.ts', '.tsx'],
  // Setup for ESM support
  globals: {
    'ts-jest': {
      useESM: true,
    },
  },
};
