import '@testing-library/jest-dom'

// Mock localStorage
const localStorageMock = (() => {
  let store = {}
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => {
      store[key] = String(value)
    }),
    removeItem: vi.fn((key) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock IntersectionObserver
class MockIntersectionObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}
Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  value: MockIntersectionObserver,
})

// Mock scrollTo
window.scrollTo = vi.fn()

// Mock getComputedStyle for MUI + jsdom compatibility
const originalGetComputedStyle = window.getComputedStyle
window.getComputedStyle = (elt, pseudoElt) => {
  const style = originalGetComputedStyle ? originalGetComputedStyle(elt, pseudoElt) : {}
  return {
    ...style,
    getPropertyValue: (prop) => style.getPropertyValue?.(prop) ?? '',
  }
}

// Mock ResizeObserver for MUI components
class MockResizeObserver {
  constructor() {}
  observe() {}
  unobserve() {}
  disconnect() {}
}
Object.defineProperty(window, 'ResizeObserver', {
  writable: true,
  value: MockResizeObserver,
})

// Suppress React Router future warnings in tests
beforeEach(() => {
  localStorageMock.clear()
  vi.clearAllMocks()
})
