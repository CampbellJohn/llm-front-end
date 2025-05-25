module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/src/$1',
    '^axios$': require.resolve('axios'),
  },
  testMatch: [
    '**/__tests__/**/*.[jt]s?(x)',
    '**/?(*.)+(spec|test).[jt]s?(x)',
  ],
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  transformIgnorePatterns: [
    'node_modules/(?!(axios|@?axios)/)',
    '^\\.*\\.(css|sass|scss|less)$',
  ],
  collectCoverage: true,
  coverageDirectory: 'coverage',
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js',
    '!src/serviceWorker.js',
    '!src/reportWebVitals.js',
    '!src/setupTests.js',
  ],
  coveragePathIgnorePatterns: [
    '/node_modules/'
  ],
  moduleFileExtensions: ['js', 'jsx', 'json', 'node'],
  testPathIgnorePatterns: [
    '/node_modules/\\\\.next/'
  ],
  verbose: true,
};
