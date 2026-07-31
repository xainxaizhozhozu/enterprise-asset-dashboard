import '@testing-library/jest-dom';

// Mock ResizeObserver (needed by some chart components)
global.ResizeObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
};
