/**
 * Extract AWS Cloudscape Design System color tokens
 * This script reads the official AWS design tokens and outputs them for use in our theme
 */

import * as tokens from '@cloudscape-design/design-tokens';

console.log('='.repeat(80));
console.log('AWS CLOUDSCAPE DESIGN SYSTEM - OFFICIAL COLOR TOKENS');
console.log('='.repeat(80));
console.log('\n');

// Helper function to format token output
function printToken(name, token) {
  if (typeof token === 'object' && token !== null && 'light' in token && 'dark' in token) {
    console.log(`${name}:`);
    console.log(`  Light: ${token.light}`);
    console.log(`  Dark:  ${token.dark}`);
  } else {
    console.log(`${name}: ${token}`);
  }
}

// Background Colors
console.log('\n📦 BACKGROUND COLORS');
console.log('-'.repeat(80));
printToken('colorBackgroundLayoutMain', tokens.colorBackgroundLayoutMain);
printToken('colorBackgroundContainerContent', tokens.colorBackgroundContainerContent);
printToken('colorBackgroundContainerHeader', tokens.colorBackgroundContainerHeader);
printToken('colorBackgroundHomeHeader', tokens.colorBackgroundHomeHeader);

// Text Colors
console.log('\n✍️  TEXT COLORS');
console.log('-'.repeat(80));
printToken('colorTextBodyDefault', tokens.colorTextBodyDefault);
printToken('colorTextBodySecondary', tokens.colorTextBodySecondary);
printToken('colorTextHeadingDefault', tokens.colorTextHeadingDefault);
printToken('colorTextHeadingSecondary', tokens.colorTextHeadingSecondary);
printToken('colorTextLabel', tokens.colorTextLabel);

// Border Colors
console.log('\n🖼️  BORDER COLORS');
console.log('-'.repeat(80));
printToken('colorBorderDividerDefault', tokens.colorBorderDividerDefault);
printToken('colorBorderContainerTop', tokens.colorBorderContainerTop);
printToken('colorBorderInputDefault', tokens.colorBorderInputDefault);

// Primary/Interactive Colors
console.log('\n🔵 PRIMARY (INTERACTIVE) COLORS');
console.log('-'.repeat(80));
printToken('colorTextInteractiveDefault', tokens.colorTextInteractiveDefault);
printToken('colorTextInteractiveHover', tokens.colorTextInteractiveHover);
printToken('colorTextInteractiveActive', tokens.colorTextInteractiveActive);
printToken('colorBackgroundButtonPrimaryDefault', tokens.colorBackgroundButtonPrimaryDefault);
printToken('colorBackgroundButtonPrimaryHover', tokens.colorBackgroundButtonPrimaryHover);
printToken('colorBackgroundButtonPrimaryActive', tokens.colorBackgroundButtonPrimaryActive);

// Status Colors - Success
console.log('\n✅ SUCCESS COLORS');
console.log('-'.repeat(80));
printToken('colorTextStatusSuccess', tokens.colorTextStatusSuccess);
printToken('colorBackgroundStatusSuccess', tokens.colorBackgroundStatusSuccess);
printToken('colorBorderStatusSuccess', tokens.colorBorderStatusSuccess);

// Status Colors - Warning
console.log('\n⚠️  WARNING COLORS');
console.log('-'.repeat(80));
printToken('colorTextStatusWarning', tokens.colorTextStatusWarning);
printToken('colorBackgroundStatusWarning', tokens.colorBackgroundStatusWarning);
printToken('colorBorderStatusWarning', tokens.colorBorderStatusWarning);

// Status Colors - Error
console.log('\n❌ ERROR COLORS');
console.log('-'.repeat(80));
printToken('colorTextStatusError', tokens.colorTextStatusError);
printToken('colorBackgroundStatusError', tokens.colorBackgroundStatusError);
printToken('colorBorderStatusError', tokens.colorBorderStatusError);

// Status Colors - Info
console.log('\n💡 INFO COLORS');
console.log('-'.repeat(80));
printToken('colorTextStatusInfo', tokens.colorTextStatusInfo);
printToken('colorBackgroundStatusInfo', tokens.colorBackgroundStatusInfo);
printToken('colorBorderStatusInfo', tokens.colorBorderStatusInfo);

// Link Colors
console.log('\n🔗 LINK COLORS');
console.log('-'.repeat(80));
printToken('colorTextLinkDefault', tokens.colorTextLinkDefault);
printToken('colorTextLinkHover', tokens.colorTextLinkHover);
printToken('colorTextLinkButtonUnderline', tokens.colorTextLinkButtonUnderline);

// Typography
console.log('\n📝 TYPOGRAPHY');
console.log('-'.repeat(80));
printToken('fontFamilyBase', tokens.fontFamilyBase);
printToken('fontFamilyMonospace', tokens.fontFamilyMonospace);
printToken('fontSizeBodyS', tokens.fontSizeBodyS);
printToken('fontSizeBodyM', tokens.fontSizeBodyM);
printToken('fontSizeHeadingXs', tokens.fontSizeHeadingXs);
printToken('fontSizeHeadingS', tokens.fontSizeHeadingS);
printToken('fontSizeHeadingM', tokens.fontSizeHeadingM);
printToken('fontSizeHeadingL', tokens.fontSizeHeadingL);
printToken('fontSizeHeadingXl', tokens.fontSizeHeadingXl);
printToken('lineHeightBodyM', tokens.lineHeightBodyM);
printToken('lineHeightHeadingXl', tokens.lineHeightHeadingXl);
printToken('fontWeightHeadingXl', tokens.fontWeightHeadingXl);

// Spacing
console.log('\n📏 SPACING');
console.log('-'.repeat(80));
printToken('spaceScaledXxxs', tokens.spaceScaledXxxs);
printToken('spaceScaledXxs', tokens.spaceScaledXxs);
printToken('spaceScaledXs', tokens.spaceScaledXs);
printToken('spaceScaledS', tokens.spaceScaledS);
printToken('spaceScaledM', tokens.spaceScaledM);
printToken('spaceScaledL', tokens.spaceScaledL);
printToken('spaceScaledXl', tokens.spaceScaledXl);
printToken('spaceScaledXxl', tokens.spaceScaledXxl);

// Border Radius
console.log('\n⭕ BORDER RADIUS');
console.log('-'.repeat(80));
printToken('borderRadiusButton', tokens.borderRadiusButton);
printToken('borderRadiusContainer', tokens.borderRadiusContainer);
printToken('borderRadiusInput', tokens.borderRadiusInput);

// Shadows
console.log('\n🌑 SHADOWS');
console.log('-'.repeat(80));
printToken('shadowContainer', tokens.shadowContainer);
printToken('shadowDropdown', tokens.shadowDropdown);
printToken('shadowModal', tokens.shadowModal);

console.log('\n');
console.log('='.repeat(80));
console.log('Token extraction complete!');
console.log('='.repeat(80));
