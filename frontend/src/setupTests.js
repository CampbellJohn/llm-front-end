// Import jest-dom for custom matchers
import '@testing-library/jest-dom';

// Mock the window.matchMedia function used by some components
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock the ResizeObserver which is used by some components
class ResizeObserver {
  observe() {}
  unobserve() {}
  disconnect() {}
}

window.ResizeObserver = ResizeObserver;

// Mock the scrollIntoView method used by some components
window.HTMLElement.prototype.scrollIntoView = jest.fn();

// Mock the scrollTo method
window.scrollTo = jest.fn();

// Mock the fetch API
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock the console.error to avoid cluttering test output
const originalConsoleError = console.error;
console.error = (...args) => {
  // Suppress specific error messages that are expected
  if (
    args[0] && 
    typeof args[0] === 'string' && 
    args[0].includes('A component is changing an uncontrolled input')
  ) {
    return;
  }
  originalConsoleError(...args);
};

// Mock the localStorage
const localStorageMock = (() => {
  let store = {};
  return {
    getItem: jest.fn((key) => store[key] || null),
    setItem: jest.fn((key, value) => {
      store[key] = value.toString();
    }),
    removeItem: jest.fn((key) => {
      delete store[key];
    }),
    clear: jest.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});
