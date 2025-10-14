/**
 * AWS Cloudscape Design System Color Helpers
 * Provides theme-aware color functions for consistent styling across the admin frontend
 * All colors are based on official AWS Cloudscape design tokens
 */

export type ThemeMode = 'light' | 'dark';

/**
 * AWS Cloudscape official color palette
 * Source: @cloudscape-design/design-tokens v3.0.62
 */
const AWS_COLORS = {
  light: {
    // Primary colors
    primary: '#0073bb',
    primaryHover: '#005a8e',
    primaryActive: '#004567',
    primaryBackground: 'rgba(0, 115, 187, 0.1)',
    primaryBorder: 'rgba(0, 115, 187, 0.2)',

    // Success colors (green)
    success: '#1d8102',
    successHover: '#165f01',
    successActive: '#0f4501',
    successBackground: 'rgba(29, 129, 2, 0.1)',
    successBorder: 'rgba(29, 129, 2, 0.2)',

    // Warning colors (orange)
    warning: '#ff9900',
    warningHover: '#e88b00',
    warningActive: '#cc7a00',
    warningBackground: 'rgba(255, 153, 0, 0.1)',
    warningBorder: 'rgba(255, 153, 0, 0.2)',

    // Error colors (red)
    error: '#d13212',
    errorHover: '#a82a0e',
    errorActive: '#7f210a',
    errorBackground: 'rgba(209, 50, 18, 0.1)',
    errorBorder: 'rgba(209, 50, 18, 0.2)',

    // Info colors (blue)
    info: '#0073bb',
    infoHover: '#005a8e',
    infoActive: '#004567',
    infoBackground: 'rgba(0, 115, 187, 0.1)',
    infoBorder: 'rgba(0, 115, 187, 0.2)',

    // Neutral colors (gray)
    neutral: '#5f6b7a',
    neutralHover: '#4d5763',
    neutralActive: '#3b444e',
    neutralBackground: 'rgba(95, 107, 122, 0.1)',
    neutralBorder: 'rgba(95, 107, 122, 0.2)',

    // Text colors
    textPrimary: '#16191f',
    textSecondary: '#5f6b7a',
    textDisabled: '#9ea8b3',

    // Background colors
    backgroundPrimary: '#ffffff',
    backgroundSecondary: '#f9fafb',
    backgroundHover: '#f2f3f5',

    // Border colors
    borderDefault: '#e9ebed',
    borderStrong: '#d1d5db',

    // Special status colors
    statusPositive: '#1d8102',
    statusNegative: '#d13212',
    statusPending: '#ff9900',
    statusInfo: '#0073bb',
    statusInactive: '#9ea8b3',
  },
  dark: {
    // Primary colors
    primary: '#42b4ff',
    primaryHover: '#68c2ff',
    primaryActive: '#8ed0ff',
    primaryBackground: 'rgba(66, 180, 255, 0.15)',
    primaryBorder: 'rgba(66, 180, 255, 0.3)',

    // Success colors (green)
    success: '#7dde86',
    successHover: '#99e59f',
    successActive: '#b5ecb8',
    successBackground: 'rgba(125, 222, 134, 0.15)',
    successBorder: 'rgba(125, 222, 134, 0.3)',

    // Warning colors (orange)
    warning: '#ffb84d',
    warningHover: '#ffc670',
    warningActive: '#ffd493',
    warningBackground: 'rgba(255, 184, 77, 0.15)',
    warningBorder: 'rgba(255, 184, 77, 0.3)',

    // Error colors (red)
    error: '#ff9b8a',
    errorHover: '#ffaea0',
    errorActive: '#ffc1b6',
    errorBackground: 'rgba(255, 155, 138, 0.15)',
    errorBorder: 'rgba(255, 155, 138, 0.3)',

    // Info colors (blue)
    info: '#42b4ff',
    infoHover: '#68c2ff',
    infoActive: '#8ed0ff',
    infoBackground: 'rgba(66, 180, 255, 0.15)',
    infoBorder: 'rgba(66, 180, 255, 0.3)',

    // Neutral colors (gray)
    neutral: '#9ea8b3',
    neutralHover: '#b4bcc5',
    neutralActive: '#cad0d7',
    neutralBackground: 'rgba(158, 168, 179, 0.15)',
    neutralBorder: 'rgba(158, 168, 179, 0.3)',

    // Text colors
    textPrimary: '#f9fafb',
    textSecondary: '#d1d5db',
    textDisabled: '#687078',

    // Background colors
    backgroundPrimary: '#16191f',
    backgroundSecondary: '#1f2430',
    backgroundHover: '#2a2f3f',

    // Border colors
    borderDefault: '#414d5c',
    borderStrong: '#5f6b7a',

    // Special status colors
    statusPositive: '#7dde86',
    statusNegative: '#ff9b8a',
    statusPending: '#ffb84d',
    statusInfo: '#42b4ff',
    statusInactive: '#687078',
  },
};

/**
 * Get color value based on theme mode
 */
export const getColor = (colorKey: keyof typeof AWS_COLORS.light, theme: ThemeMode = 'light'): string => {
  return AWS_COLORS[theme][colorKey];
};

/**
 * Get status color based on status type and theme
 */
export const getStatusColor = (
  status: 'success' | 'error' | 'warning' | 'info' | 'neutral' | 'pending' | 'active' | 'inactive',
  theme: ThemeMode = 'light'
): string => {
  const statusMap: Record<string, keyof typeof AWS_COLORS.light> = {
    success: 'success',
    error: 'error',
    warning: 'warning',
    info: 'info',
    neutral: 'neutral',
    pending: 'warning',
    active: 'success',
    inactive: 'neutral',
  };

  return getColor(statusMap[status] || 'neutral', theme);
};

/**
 * Get Tag component style object based on variant and theme
 */
export interface TagStyleProps {
  backgroundColor: string;
  color: string;
  border: string;
  borderRadius: string;
}

export const getTagStyle = (
  variant: 'primary' | 'success' | 'error' | 'warning' | 'info' | 'neutral',
  theme: ThemeMode = 'light'
): TagStyleProps => {
  const colors = AWS_COLORS[theme];

  const variantMap = {
    primary: {
      backgroundColor: colors.primaryBackground,
      color: colors.primary,
      border: `1px solid ${colors.primaryBorder}`,
    },
    success: {
      backgroundColor: colors.successBackground,
      color: colors.success,
      border: `1px solid ${colors.successBorder}`,
    },
    error: {
      backgroundColor: colors.errorBackground,
      color: colors.error,
      border: `1px solid ${colors.errorBorder}`,
    },
    warning: {
      backgroundColor: colors.warningBackground,
      color: colors.warning,
      border: `1px solid ${colors.warningBorder}`,
    },
    info: {
      backgroundColor: colors.infoBackground,
      color: colors.info,
      border: `1px solid ${colors.infoBorder}`,
    },
    neutral: {
      backgroundColor: colors.neutralBackground,
      color: colors.neutral,
      border: `1px solid ${colors.neutralBorder}`,
    },
  };

  return {
    ...variantMap[variant],
    borderRadius: '4px',
  };
};

/**
 * Get status Tag style based on status string and theme
 */
export const getStatusTagStyle = (
  status: string,
  theme: ThemeMode = 'light'
): TagStyleProps => {
  const statusLower = status.toLowerCase();

  // Map common status strings to variants
  if (statusLower.includes('active') || statusLower.includes('approved') || statusLower.includes('published') || statusLower.includes('online')) {
    return getTagStyle('success', theme);
  }
  if (statusLower.includes('inactive') || statusLower.includes('rejected') || statusLower.includes('deleted') || statusLower.includes('banned') || statusLower.includes('offline')) {
    return getTagStyle('error', theme);
  }
  if (statusLower.includes('pending') || statusLower.includes('reviewing') || statusLower.includes('processing')) {
    return getTagStyle('warning', theme);
  }
  if (statusLower.includes('draft')) {
    return getTagStyle('info', theme);
  }

  return getTagStyle('neutral', theme);
};

/**
 * Get text color based on variant and theme
 */
export const getTextColor = (
  variant: 'primary' | 'secondary' | 'disabled' | 'success' | 'error' | 'warning' | 'info',
  theme: ThemeMode = 'light'
): string => {
  const colors = AWS_COLORS[theme];

  const variantMap = {
    primary: colors.textPrimary,
    secondary: colors.textSecondary,
    disabled: colors.textDisabled,
    success: colors.success,
    error: colors.error,
    warning: colors.warning,
    info: colors.info,
  };

  return variantMap[variant];
};

/**
 * Get background color based on variant and theme
 */
export const getBackgroundColor = (
  variant: 'primary' | 'secondary' | 'hover',
  theme: ThemeMode = 'light'
): string => {
  const colors = AWS_COLORS[theme];

  const variantMap = {
    primary: colors.backgroundPrimary,
    secondary: colors.backgroundSecondary,
    hover: colors.backgroundHover,
  };

  return variantMap[variant];
};

/**
 * Get border color based on variant and theme
 */
export const getBorderColor = (
  variant: 'default' | 'strong',
  theme: ThemeMode = 'light'
): string => {
  const colors = AWS_COLORS[theme];

  return variant === 'default' ? colors.borderDefault : colors.borderStrong;
};

/**
 * Get rating color based on rating value and theme
 */
export const getRatingColor = (rating: number, theme: ThemeMode = 'light'): string => {
  if (rating >= 8) {
    return getColor('success', theme);
  }
  if (rating >= 6) {
    return getColor('info', theme);
  }
  if (rating >= 4) {
    return getColor('warning', theme);
  }
  return getColor('error', theme);
};

/**
 * Get rating Tag style based on rating value and theme
 */
export const getRatingTagStyle = (rating: number, theme: ThemeMode = 'light'): TagStyleProps => {
  if (rating >= 8) {
    return getTagStyle('success', theme);
  }
  if (rating >= 6) {
    return getTagStyle('info', theme);
  }
  if (rating >= 4) {
    return getTagStyle('warning', theme);
  }
  return getTagStyle('error', theme);
};

/**
 * Get VIP status Tag style based on VIP status and theme
 */
export const getVIPTagStyle = (isVIP: boolean, theme: ThemeMode = 'light'): TagStyleProps => {
  return isVIP ? getTagStyle('warning', theme) : getTagStyle('neutral', theme);
};

/**
 * Export all AWS colors for direct access if needed
 */
export const awsColors = AWS_COLORS;
