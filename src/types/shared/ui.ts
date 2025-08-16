/**
 * UI component types
 */

// Button variants
export type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
export type ButtonSize = 'sm' | 'md' | 'lg';

// Input variants
export type InputVariant = 'default' | 'error' | 'success';

// Card variants
export type CardVariant = 'default' | 'elevated' | 'outlined';

// Badge variants
export type BadgeVariant = 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error';

// Modal sizes
export type ModalSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

// Toast types
export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

// Table column definition
export interface TableColumn<T = any> {
  key: keyof T;
  label: string;
  sortable?: boolean;
  render?: (value: any, row: T) => React.ReactNode;
  width?: string;
}

// Select option
export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}
