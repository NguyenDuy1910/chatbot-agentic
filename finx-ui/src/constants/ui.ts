/**
 * UI constants
 */

// Breakpoints
export const BREAKPOINTS = {
  sm: '640px',
  md: '768px',
  lg: '1024px',
  xl: '1280px',
  '2xl': '1536px',
} as const;

// Z-index layers
export const Z_INDEX = {
  dropdown: 1000,
  sticky: 1020,
  fixed: 1030,
  modal: 1040,
  popover: 1050,
  tooltip: 1060,
  toast: 1070,
} as const;

// Animation durations
export const ANIMATION_DURATION = {
  fast: 150,
  normal: 300,
  slow: 500,
} as const;

// Component sizes
export const COMPONENT_SIZES = {
  button: {
    sm: { height: '32px', padding: '0 12px', fontSize: '14px' },
    md: { height: '40px', padding: '0 16px', fontSize: '16px' },
    lg: { height: '48px', padding: '0 20px', fontSize: '18px' },
  },
  input: {
    sm: { height: '32px', padding: '0 8px', fontSize: '14px' },
    md: { height: '40px', padding: '0 12px', fontSize: '16px' },
    lg: { height: '48px', padding: '0 16px', fontSize: '18px' },
  },
} as const;

// Layout constants
export const LAYOUT = {
  sidebar: {
    width: '280px',
    collapsedWidth: '64px',
  },
  header: {
    height: '64px',
  },
  footer: {
    height: '48px',
  },
} as const;
