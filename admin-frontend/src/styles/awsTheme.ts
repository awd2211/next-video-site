/**
 * AWS Cloudscape Design System Theme
 * Reference: https://cloudscape.design/
 *
 * 100% Official AWS Cloudscape Colors and Typography
 * Source: @cloudscape-design/design-tokens v3.0.62
 */

export const awsLightTheme = {
  // ============ Background Colors (AWS Official) ============
  colorBgLayout: '#ffffff',              // AWS: color-background-layout-main
  colorBgContainer: '#ffffff',           // AWS: color-background-container-content
  colorBgElevated: '#ffffff',            // AWS: color-background-container-header
  colorBgSpotlight: '#f9f9fa',           // AWS: lighter variant

  // ============ Text Colors (AWS Official) ============
  colorText: '#0f141a',                  // AWS: color-text-body-default
  colorTextSecondary: '#424650',         // AWS: color-text-body-secondary
  colorTextTertiary: '#656871',          // AWS: lighter text
  colorTextQuaternary: '#8c8c94',        // AWS: disabled text
  colorTextHeading: '#0f141a',           // AWS: color-text-heading-default
  colorTextLabel: '#0f141a',             // AWS: color-text-label

  // ============ Border Colors (AWS Official) ============
  colorBorder: '#c6c6cd',                // AWS: color-border-divider-default
  colorBorderSecondary: '#ebebf0',       // AWS: color-border-divider-secondary
  colorSplit: '#ebebf0',                 // AWS: divider secondary

  // ============ Primary Colors (AWS Blue - Official) ============
  colorPrimary: '#006ce0',               // AWS: color-background-button-primary-default
  colorPrimaryBg: '#f0fbff',             // AWS: color-background-status-info (light blue bg)
  colorPrimaryBgHover: '#d3ebf4',        // Derived from AWS primary
  colorPrimaryBorder: '#006ce0',         // AWS: color-border-input-focused
  colorPrimaryBorderHover: '#002b66',    // AWS: color-background-button-primary-hover
  colorPrimaryHover: '#002b66',          // AWS: color-background-button-primary-hover
  colorPrimaryActive: '#002b66',         // AWS: color-background-button-primary-active
  colorPrimaryTextHover: '#002b66',      // AWS: color-text-link-hover
  colorPrimaryText: '#006ce0',           // AWS: color-text-link-default
  colorPrimaryTextActive: '#002b66',     // AWS: color-text-link-hover

  // ============ Success Colors (AWS Green - Official) ============
  colorSuccess: '#00802f',               // AWS: color-text-status-success
  colorSuccessBg: '#effff1',             // AWS: color-background-status-success
  colorSuccessBorder: '#00802f',         // AWS: color-border-status-success
  colorSuccessTextHover: '#00802f',      // AWS: same as success
  colorSuccessTextActive: '#00802f',     // AWS: same as success

  // ============ Warning Colors (AWS Orange - Official) ============
  colorWarning: '#855900',               // AWS: color-text-status-warning
  colorWarningBg: '#fffef0',             // AWS: color-background-status-warning
  colorWarningBorder: '#855900',         // AWS: color-border-status-warning

  // ============ Error Colors (AWS Red - Official) ============
  colorError: '#db0000',                 // AWS: color-text-status-error
  colorErrorBg: '#fff5f5',               // AWS: color-background-status-error
  colorErrorBorder: '#db0000',           // AWS: color-border-status-error
  colorErrorTextHover: '#db0000',        // AWS: same as error
  colorErrorTextActive: '#db0000',       // AWS: same as error

  // ============ Info Colors (AWS Blue - Official) ============
  colorInfo: '#006ce0',                  // AWS: color-text-status-info
  colorInfoBg: '#f0fbff',                // AWS: color-background-status-info
  colorInfoBorder: '#006ce0',            // AWS: color-border-status-info

  // ============ Link Colors (AWS Official) ============
  colorLink: '#006ce0',                  // AWS: color-text-link-default
  colorLinkHover: '#002b66',             // AWS: color-text-link-hover
  colorLinkActive: '#002b66',            // AWS: color-text-link-hover
};

export const awsDarkTheme = {
  // ============ Background Colors (AWS Official Dark) ============
  colorBgLayout: '#161d26',              // AWS: color-background-layout-main (dark)
  colorBgContainer: '#161d26',           // AWS: color-background-container-content (dark)
  colorBgElevated: '#232b37',            // AWS: elevated surface
  colorBgSpotlight: '#1b232d',           // AWS: subtle elevation

  // ============ Text Colors (AWS Official Dark) ============
  colorText: '#c6c6cd',                  // AWS: color-text-body-default (dark)
  colorTextSecondary: '#c6c6cd',         // AWS: color-text-body-secondary (dark)
  colorTextTertiary: '#a4a4ad',          // AWS: color-text-heading-secondary (dark)
  colorTextQuaternary: '#656871',        // AWS: color-text-interactive-disabled (dark)
  colorTextHeading: '#ebebf0',           // AWS: color-text-heading-default (dark)
  colorTextLabel: '#dedee3',             // AWS: color-text-label (dark)

  // ============ Border Colors (AWS Official Dark) ============
  colorBorder: '#424650',                // AWS: color-border-divider-default (dark)
  colorBorderSecondary: '#232b37',       // AWS: color-border-divider-secondary (dark)
  colorSplit: '#424650',                 // AWS: divider default (dark)

  // ============ Primary Colors (AWS Blue - Official Dark) ============
  colorPrimary: '#42b4ff',               // AWS: color-background-button-primary-default (dark)
  colorPrimaryBg: '#001129',             // AWS: color-background-status-info (dark)
  colorPrimaryBgHover: '#002b66',        // Derived from dark primary
  colorPrimaryBorder: '#42b4ff',         // AWS: color-border-input-focused (dark)
  colorPrimaryBorderHover: '#75cfff',    // AWS: color-background-button-primary-hover (dark)
  colorPrimaryHover: '#75cfff',          // AWS: color-background-button-primary-hover (dark)
  colorPrimaryActive: '#42b4ff',         // AWS: color-background-button-primary-active (dark)
  colorPrimaryTextHover: '#75cfff',      // AWS: color-text-link-hover (dark)
  colorPrimaryText: '#42b4ff',           // AWS: color-text-link-default (dark)
  colorPrimaryTextActive: '#75cfff',     // AWS: color-text-link-hover (dark)

  // ============ Success Colors (AWS Green - Official Dark) ============
  colorSuccess: '#2bb534',               // AWS: color-text-status-success (dark)
  colorSuccessBg: '#001401',             // AWS: color-background-status-success (dark)
  colorSuccessBorder: '#2bb534',         // AWS: color-border-status-success (dark)
  colorSuccessTextHover: '#2bb534',      // AWS: same as success
  colorSuccessTextActive: '#2bb534',     // AWS: same as success

  // ============ Warning Colors (AWS Orange - Official Dark) ============
  colorWarning: '#fbd332',               // AWS: color-text-status-warning (dark)
  colorWarningBg: '#191100',             // AWS: color-background-status-warning (dark)
  colorWarningBorder: '#fbd332',         // AWS: color-border-status-warning (dark)

  // ============ Error Colors (AWS Red - Official Dark) ============
  colorError: '#ff7a7a',                 // AWS: color-text-status-error (dark)
  colorErrorBg: '#1f0000',               // AWS: color-background-status-error (dark)
  colorErrorBorder: '#ff7a7a',           // AWS: color-border-status-error (dark)
  colorErrorTextHover: '#ff7a7a',        // AWS: same as error
  colorErrorTextActive: '#ff7a7a',       // AWS: same as error

  // ============ Info Colors (AWS Blue - Official Dark) ============
  colorInfo: '#42b4ff',                  // AWS: color-text-status-info (dark)
  colorInfoBg: '#001129',                // AWS: color-background-status-info (dark)
  colorInfoBorder: '#42b4ff',            // AWS: color-border-status-info (dark)

  // ============ Link Colors (AWS Official Dark) ============
  colorLink: '#42b4ff',                  // AWS: color-text-link-default (dark)
  colorLinkHover: '#75cfff',             // AWS: color-text-link-hover (dark)
  colorLinkActive: '#75cfff',            // AWS: color-text-link-hover (dark)
};

/**
 * AWS Typography System (Official Cloudscape)
 * Font: Open Sans (official AWS Cloudscape font)
 */
export const awsFonts = {
  // Primary font: Open Sans (AWS Cloudscape official)
  fontFamily: `'Open Sans', 'Helvetica Neue', Roboto, Arial, sans-serif`,

  // Monospace font (AWS Cloudscape official)
  fontFamilyCode: `Monaco, Menlo, Consolas, 'Courier Prime', Courier, 'Courier New', monospace`,

  // Font sizes (AWS Cloudscape official spec)
  fontSizeXS: 12,        // Body Small (AWS: fontSizeBodyS)
  fontSizeSM: 13,        // Between small and medium
  fontSize: 14,          // Body Medium (AWS: fontSizeBodyM)
  fontSizeLG: 16,        // Heading Small (AWS: fontSizeHeadingS)
  fontSizeXL: 18,        // Heading Medium (AWS: fontSizeHeadingM)
  fontSizeHeading1: 24,  // Heading XL (AWS: fontSizeHeadingXl)
  fontSizeHeading2: 20,  // Heading Large (AWS: fontSizeHeadingL)
  fontSizeHeading3: 18,  // Heading Medium (AWS: fontSizeHeadingM)
  fontSizeHeading4: 16,  // Heading Small (AWS: fontSizeHeadingS)
  fontSizeHeading5: 14,  // Heading XS (AWS: fontSizeHeadingXs)

  // Font weights (AWS Cloudscape spec)
  fontWeightStrong: 700, // Bold (AWS: fontWeightHeadingXl)

  // Line heights (AWS Cloudscape spec)
  lineHeight: 1.4286,          // 20px for 14px font (AWS: lineHeightBodyM)
  lineHeightHeading1: 1.25,    // 30px for 24px font (AWS: lineHeightHeadingXl)
  lineHeightHeading2: 1.4,     // Consistent heading line height
};

/**
 * AWS Spacing System (Cloudscape scaled spacing)
 */
export const awsSpacing = {
  sizeXXS: 2,      // AWS: spaceScaledXxxs (2px)
  sizeXS: 4,       // AWS: spaceScaledXxs (4px)
  sizeSM: 8,       // AWS: spaceScaledXs (8px)
  size: 12,        // AWS: spaceScaledS (12px)
  sizeMD: 16,      // AWS: spaceScaledM (16px)
  sizeLG: 20,      // AWS: spaceScaledL (20px)
  sizeXL: 24,      // AWS: spaceScaledXl (24px)
  sizeXXL: 32,     // AWS: spaceScaledXxl (32px)
};

/**
 * AWS Border Radius System (Cloudscape official)
 */
export const awsBorderRadius = {
  borderRadius: 8,         // AWS: borderRadiusInput (8px)
  borderRadiusLG: 16,      // AWS: borderRadiusContainer (16px)
  borderRadiusSM: 4,       // Smaller radius
  borderRadiusXS: 2,       // Minimal radius
};

/**
 * AWS Shadow System (Light Mode)
 */
export const awsShadows = {
  boxShadow: '0 0 0 1px rgba(0, 7, 22, 0.05), 0 1px 1px 0 rgba(0, 7, 22, 0.05)',
  boxShadowSecondary: '0 4px 20px 1px rgba(0, 7, 22, 0.10)',
  boxShadowTertiary: '0 8px 16px 0 rgba(0, 7, 22, 0.12)',
};

/**
 * AWS Shadow System (Dark Mode)
 */
export const awsShadowsDark = {
  boxShadow: '0 0 0 1px rgba(255, 255, 255, 0.1), 0 1px 1px 0 rgba(0, 0, 0, 0.3)',
  boxShadowSecondary: '0 4px 20px 1px rgba(0, 0, 0, 0.30)',
  boxShadowTertiary: '0 8px 16px 0 rgba(0, 0, 0, 0.40)',
};

/**
 * Complete AWS Cloudscape Theme Configuration
 * 100% Official AWS Colors and Typography
 */
export const getAWSThemeConfig = (isDark: boolean) => ({
  token: {
    // Apply official AWS theme colors
    ...(isDark ? awsDarkTheme : awsLightTheme),

    // AWS Typography System
    ...awsFonts,

    // AWS Spacing System
    ...awsSpacing,

    // AWS Border Radius System
    ...awsBorderRadius,

    // AWS Shadow System
    ...(isDark ? awsShadowsDark : awsShadows),

    // Control heights (AWS standard)
    controlHeight: 32,
    controlHeightLG: 40,
    controlHeightSM: 24,

    // Border styling
    lineWidth: 1,
    lineType: 'solid' as const,

    // Animation (minimal, AWS-style)
    motionUnit: 0.1,
    motionBase: 0,
    motionEaseInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },

  // Component-level configurations (AWS Cloudscape style)
  components: {
    // Button - AWS flat design
    Button: {
      primaryShadow: 'none',
      fontWeight: 500,
      borderRadius: 20,          // AWS: borderRadiusButton (20px)
      controlHeight: 32,
      controlHeightLG: 40,
      controlHeightSM: 24,
      paddingContentHorizontal: 16,
    },

    // Table - AWS compact style
    Table: {
      headerBg: isDark ? '#232b37' : '#f9f9fa',
      headerColor: isDark ? '#ebebf0' : '#0f141a',
      headerFontWeight: 700,
      cellPaddingBlock: 12,
      cellPaddingInline: 16,
      fontSize: 14,
      rowHoverBg: isDark ? 'rgba(66, 180, 255, 0.08)' : 'rgba(0, 108, 224, 0.04)',
      borderColor: isDark ? '#424650' : '#c6c6cd',
    },

    // Card - AWS container style
    Card: {
      boxShadow: isDark ? awsShadowsDark.boxShadow : awsShadows.boxShadow,
      headerBg: 'transparent',
      headerFontSize: 18,
      headerFontSizeSM: 16,
      borderRadiusLG: 16,        // AWS: borderRadiusContainer
      paddingLG: 24,
      boxShadowTertiary: isDark ? awsShadowsDark.boxShadowTertiary : awsShadows.boxShadowTertiary,
    },

    // Menu
    Menu: {
      itemBg: 'transparent',
      itemHeight: 40,
      itemPaddingInline: 16,
      fontSize: 14,
      borderRadius: 8,
    },

    // Input - AWS input style
    Input: {
      controlHeight: 32,
      controlHeightLG: 40,
      controlHeightSM: 24,
      paddingBlock: 5,
      paddingInline: 12,
      borderRadius: 8,           // AWS: borderRadiusInput
      hoverBorderColor: isDark ? '#42b4ff' : '#006ce0',
      activeBorderColor: isDark ? '#42b4ff' : '#006ce0',
    },

    // Select
    Select: {
      controlHeight: 32,
      controlHeightLG: 40,
      controlHeightSM: 24,
      borderRadius: 8,
    },

    // Layout
    Layout: {
      headerBg: isDark ? '#161d26' : '#ffffff',
      headerColor: isDark ? '#ebebf0' : '#0f141a',
      headerHeight: 56,
      siderBg: isDark ? '#161d26' : '#ffffff',
      bodyBg: isDark ? '#161d26' : '#ffffff',
    },

    // Modal - AWS dialog style
    Modal: {
      borderRadiusLG: 16,
      headerBg: 'transparent',
      contentBg: isDark ? '#161d26' : '#ffffff',
      titleFontSize: 20,
    },

    // Drawer
    Drawer: {
      paddingLG: 24,
    },

    // Tag - AWS badge style
    Tag: {
      borderRadius: 4,
      fontSize: 12,
      defaultBg: isDark ? 'rgba(66, 180, 255, 0.15)' : 'rgba(0, 108, 224, 0.1)',
      defaultColor: isDark ? '#42b4ff' : '#006ce0',
    },

    // Badge
    Badge: {
      fontSize: 11,
      fontWeight: 600,
    },

    // Statistic - Dashboard cards
    Statistic: {
      titleFontSize: 14,
      contentFontSize: 32,
      contentFontWeight: 700,
    },

    // Pagination
    Pagination: {
      itemSize: 32,
      itemSizeSM: 24,
      borderRadius: 8,
    },

    // Form
    Form: {
      labelFontSize: 13,
      labelColor: isDark ? '#dedee3' : '#0f141a',
      labelRequiredMarkColor: isDark ? '#ff7a7a' : '#db0000',
    },

    // Tabs
    Tabs: {
      titleFontSize: 14,
      titleFontSizeSM: 13,
      itemColor: isDark ? '#c6c6cd' : '#424650',
      itemActiveColor: isDark ? '#42b4ff' : '#006ce0',
      itemHoverColor: isDark ? '#75cfff' : '#002b66',
      inkBarColor: isDark ? '#42b4ff' : '#006ce0',
    },

    // Divider
    Divider: {
      colorSplit: isDark ? '#424650' : '#c6c6cd',
    },

    // Tooltip
    Tooltip: {
      colorBgSpotlight: isDark ? '#232b37' : '#0f141a',
      colorTextLightSolid: '#ffffff',
      borderRadius: 8,
    },

    // Progress
    Progress: {
      defaultColor: isDark ? '#42b4ff' : '#006ce0',
      remainingColor: isDark ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.06)',
    },

    // Alert
    Alert: {
      borderRadiusLG: 8,
      withDescriptionPadding: '16px 24px',
    },

    // Spin
    Spin: {
      colorPrimary: isDark ? '#42b4ff' : '#006ce0',
    },
  },
});
