/**
 * AWS Cloudscape Design System Theme
 * Reference: https://cloudscape.design/
 * 
 * 基于 AWS Console 的专业企业级配色方案
 */

export const awsLightTheme = {
  // ============ Background Colors (Notion Style) ============
  colorBgLayout: '#f7f6f3',              // 主布局背景（温暖米灰）
  colorBgContainer: '#ffffff',           // 容器背景（纯白）
  colorBgElevated: '#ffffff',            // 悬浮层背景
  colorBgSpotlight: '#fafaf9',           // 聚光灯背景（浅米色）

  // ============ Text Colors (Notion Style) ============
  colorText: '#37352f',                  // 主要文字（Notion 深灰）
  colorTextSecondary: '#787774',         // 次要文字（Notion 中灰）
  colorTextTertiary: '#9b9a97',          // 三级文字（Notion 浅灰）
  colorTextQuaternary: '#b4b3af',        // 四级文字（更浅）
  colorTextHeading: '#37352f',           // 标题文字

  // ============ Border Colors (Notion Style) ============
  colorBorder: '#e9e9e7',                // 默认边框（温暖灰）
  colorBorderSecondary: '#d3d2ce',       // 次要边框
  colorSplit: '#efefed',                 // 分割线（极浅）
  
  // ============ Primary Colors (AWS Blue) ============
  colorPrimary: '#0073bb',               // AWS 主色（蓝色）
  colorPrimaryBg: '#e8f4f8',             // 主色背景
  colorPrimaryBgHover: '#d3ebf4',        // 主色背景悬停
  colorPrimaryBorder: '#9fc7de',         // 主色边框
  colorPrimaryBorderHover: '#7eb3d2',    // 主色边框悬停
  colorPrimaryHover: '#005a8e',          // 主色悬停
  colorPrimaryActive: '#004c73',         // 主色激活
  colorPrimaryTextHover: '#005a8e',      // 主色文字悬停
  colorPrimaryText: '#0073bb',           // 主色文字
  colorPrimaryTextActive: '#004c73',     // 主色文字激活
  
  // ============ Success Colors (Green) ============
  colorSuccess: '#1d8102',               // 成功色
  colorSuccessBg: '#e9f7e4',             // 成功背景
  colorSuccessBorder: '#9dd588',         // 成功边框
  colorSuccessTextHover: '#156801',      // 成功文字悬停
  colorSuccessTextActive: '#0f4d01',     // 成功文字激活
  
  // ============ Warning Colors (Orange) ============
  colorWarning: '#ff9900',               // 警告色
  colorWarningBg: '#fff4e5',             // 警告背景
  colorWarningBorder: '#ffd699',         // 警告边框
  
  // ============ Error Colors (Red) ============
  colorError: '#d13212',                 // 错误色
  colorErrorBg: '#fdecea',               // 错误背景
  colorErrorBorder: '#f5a99b',           // 错误边框
  colorErrorTextHover: '#a82810',        // 错误文字悬停
  colorErrorTextActive: '#7f1e0c',       // 错误文字激活
  
  // ============ Info Colors (Blue) ============
  colorInfo: '#0073bb',                  // 信息色
  colorInfoBg: '#e8f4f8',                // 信息背景
  colorInfoBorder: '#9fc7de',            // 信息边框
  
  // ============ Link Colors ============
  colorLink: '#0073bb',                  // 链接色
  colorLinkHover: '#005a8e',             // 链接悬停
  colorLinkActive: '#004c73',            // 链接激活
};

export const awsDarkTheme = {
  // ============ Background Colors ============
  colorBgLayout: '#000716',              // 主布局背景（深蓝黑）
  colorBgContainer: '#0f1b2a',           // 容器背景（深蓝）
  colorBgElevated: '#192534',            // 悬浮层背景（中蓝）
  colorBgSpotlight: '#1e3040',           // 聚光灯背景
  
  // ============ Text Colors ============
  colorText: '#d1d5db',                  // 主要文字（浅灰）
  colorTextSecondary: '#9ba7b6',         // 次要文字（中灰）
  colorTextTertiary: '#7d8998',          // 三级文字（深灰）
  colorTextQuaternary: '#5a5f6a',        // 四级文字（更深）
  colorTextHeading: '#ffffff',           // 标题文字（白色）
  
  // ============ Border Colors ============
  colorBorder: '#2a2e33',                // 默认边框
  colorBorderSecondary: '#414d5c',       // 次要边框
  colorSplit: '#2a2e33',                 // 分割线
  
  // ============ Primary Colors (AWS Blue - Dark) ============
  colorPrimary: '#539fe5',               // AWS 主色（亮蓝）
  colorPrimaryBg: '#0d2a45',             // 主色背景
  colorPrimaryBgHover: '#123c5f',        // 主色背景悬停
  colorPrimaryBorder: '#2b5f8a',         // 主色边框
  colorPrimaryBorderHover: '#3d7aab',    // 主色边框悬停
  colorPrimaryHover: '#85b7ed',          // 主色悬停
  colorPrimaryActive: '#9fc5f0',         // 主色激活
  colorPrimaryTextHover: '#85b7ed',      // 主色文字悬停
  colorPrimaryText: '#539fe5',           // 主色文字
  colorPrimaryTextActive: '#9fc5f0',     // 主色文字激活
  
  // ============ Success Colors (Green - Dark) ============
  colorSuccess: '#1dab56',               // 成功色
  colorSuccessBg: '#0a2e1a',             // 成功背景
  colorSuccessBorder: '#166938',         // 成功边框
  colorSuccessTextHover: '#2ac96c',      // 成功文字悬停
  colorSuccessTextActive: '#3fdb82',     // 成功文字激活
  
  // ============ Warning Colors (Orange - Dark) ============
  colorWarning: '#ff9900',               // 警告色
  colorWarningBg: '#3d2200',             // 警告背景
  colorWarningBorder: '#7a4400',         // 警告边框
  
  // ============ Error Colors (Red - Dark) ============
  colorError: '#ff5d64',                 // 错误色
  colorErrorBg: '#3d0f11',               // 错误背景
  colorErrorBorder: '#7a1e23',           // 错误边框
  colorErrorTextHover: '#ff8a8f',        // 错误文字悬停
  colorErrorTextActive: '#ffb3b6',       // 错误文字激活
  
  // ============ Info Colors (Blue - Dark) ============
  colorInfo: '#539fe5',                  // 信息色
  colorInfoBg: '#0d2a45',                // 信息背景
  colorInfoBorder: '#2b5f8a',            // 信息边框
  
  // ============ Link Colors ============
  colorLink: '#539fe5',                  // 链接色
  colorLinkHover: '#85b7ed',             // 链接悬停
  colorLinkActive: '#9fc5f0',            // 链接激活
};

/**
 * AWS 字体系统
 */
export const awsFonts = {
  // 主字体（系统字体栈，不依赖外部字体）
  fontFamily: `-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", Arial, sans-serif`,
  
  // 等宽字体（用于代码、日志、数字等）
  fontFamilyCode: `Monaco, Menlo, Consolas, "Courier New", monospace`,
  
  // 字号
  fontSizeXS: 12,
  fontSizeSM: 13,
  fontSize: 14,      // 主要字号（AWS 偏好较小字号）
  fontSizeLG: 16,
  fontSizeXL: 18,
  fontSizeHeading1: 24,
  fontSizeHeading2: 20,
  fontSizeHeading3: 18,
  fontSizeHeading4: 16,
  fontSizeHeading5: 14,
  
  // 字重
  fontWeightStrong: 700,
  
  // 行高
  lineHeight: 1.5714,        // 22px for 14px font
  lineHeightHeading1: 1.3333, // 32px for 24px font
  lineHeightHeading2: 1.4,    // 28px for 20px font
};

/**
 * AWS 间距系统
 */
export const awsSpacing = {
  sizeXXS: 4,
  sizeXS: 8,
  sizeSM: 12,
  size: 16,        // 基础间距
  sizeMD: 20,
  sizeLG: 24,
  sizeXL: 32,
  sizeXXL: 40,
};

/**
 * AWS 圆角系统
 */
export const awsBorderRadius = {
  borderRadius: 8,
  borderRadiusLG: 16,
  borderRadiusSM: 4,
  borderRadiusXS: 2,
};

/**
 * AWS 阴影系统 (Light Mode)
 */
export const awsShadows = {
  boxShadow: '0 0 0 1px rgba(0, 7, 22, 0.05), 0 1px 1px 0 rgba(0, 7, 22, 0.05)',
  boxShadowSecondary: '0 4px 20px 1px rgba(0, 7, 22, 0.10)',
  boxShadowTertiary: '0 8px 16px 0 rgba(0, 7, 22, 0.12)',
};

/**
 * AWS 阴影系统 (Dark Mode)
 */
export const awsShadowsDark = {
  boxShadow: '0 0 0 1px rgba(255, 255, 255, 0.1), 0 1px 1px 0 rgba(0, 0, 0, 0.3)',
  boxShadowSecondary: '0 4px 20px 1px rgba(0, 0, 0, 0.30)',
  boxShadowTertiary: '0 8px 16px 0 rgba(0, 0, 0, 0.40)',
};

/**
 * 完整的 AWS 主题配置（用于 Ant Design ConfigProvider）
 */
export const getAWSThemeConfig = (isDark: boolean) => ({
  token: {
    // 应用对应主题的颜色
    ...(isDark ? awsDarkTheme : awsLightTheme),
    
    // 字体系统
    ...awsFonts,
    
    // 间距系统
    ...awsSpacing,
    
    // 圆角系统
    ...awsBorderRadius,
    
    // 阴影系统
    ...(isDark ? awsShadowsDark : awsShadows),
    
    // 控制高度
    controlHeight: 32,
    controlHeightLG: 40,
    controlHeightSM: 24,
    
    // 线宽
    lineWidth: 1,
    lineType: 'solid',
    
    // 动画
    motionUnit: 0.1,
    motionBase: 0,
    motionEaseInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  },
  
  // 组件级别的配置
  components: {
    // Button 组件
    Button: {
      primaryShadow: 'none',
      fontWeight: 500,
    },
    
    // Table 组件
    Table: {
      headerBg: isDark ? '#192534' : '#f9fafb',
      headerColor: isDark ? '#d1d5db' : '#16191f',
      cellPaddingBlock: 12,
      cellPaddingInline: 16,
      fontSize: 14,
    },
    
    // Card 组件
    Card: {
      boxShadow: isDark ? awsShadowsDark.boxShadow : awsShadows.boxShadow,
      headerBg: 'transparent',
      headerFontSize: 18,
      headerFontSizeSM: 16,
    },
    
    // Menu 组件
    Menu: {
      itemBg: 'transparent',
      itemHeight: 40,
      itemPaddingInline: 16,
      fontSize: 14,
    },
    
    // Input 组件
    Input: {
      controlHeight: 32,
      paddingBlock: 5,
      paddingInline: 12,
    },
    
    // Layout 组件
    Layout: {
      headerBg: isDark ? '#0f1b2a' : '#ffffff',
      headerColor: isDark ? '#ffffff' : '#37352f',
      headerHeight: 56,
      siderBg: isDark ? '#0f1b2a' : '#f7f6f3',
      bodyBg: isDark ? '#000716' : '#f7f6f3',
    },
  },
});

