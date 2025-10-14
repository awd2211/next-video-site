import tokens from '@cloudscape-design/design-tokens/index-visual-refresh.json' assert { type: 'json' };

console.log('🎨 AWS CLOUDSCAPE - OFFICIAL HEX COLOR VALUES\n');
console.log('═'.repeat(80));

// Helper function to extract color value
function getColor(token) {
  if (!token) return null;
  return {
    light: token.light || token.value || 'N/A',
    dark: token.dark || token.value || 'N/A'
  };
}

// Background Colors
console.log('\n📦 BACKGROUND COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Layout Main:', JSON.stringify(getColor(tokens.color.background['layout-main']), null, 2));
console.log('Container Content:', JSON.stringify(getColor(tokens.color.background['container-content']), null, 2));
console.log('Container Header:', JSON.stringify(getColor(tokens.color.background['container-header']), null, 2));
console.log('Home Header:', JSON.stringify(getColor(tokens.color.background['home-header']), null, 2));

// Text Colors
console.log('\n✍️  TEXT COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Body Default:', JSON.stringify(getColor(tokens.color.text.body.default), null, 2));
console.log('Body Secondary:', JSON.stringify(getColor(tokens.color.text.body.secondary), null, 2));
console.log('Heading Default:', JSON.stringify(getColor(tokens.color.text.heading.default), null, 2));
console.log('Heading Secondary:', JSON.stringify(getColor(tokens.color.text.heading.secondary), null, 2));
console.log('Label:', JSON.stringify(getColor(tokens.color.text.label), null, 2));

// Border Colors
console.log('\n🖼️  BORDER COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Divider Default:', JSON.stringify(getColor(tokens.color.border.divider.default), null, 2));
console.log('Input Default:', JSON.stringify(getColor(tokens.color.border.input.default), null, 2));

// Primary/Interactive Colors
console.log('\n🔵 PRIMARY COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Button Primary Default:', JSON.stringify(getColor(tokens.color.background['button-primary-default']), null, 2));
console.log('Button Primary Hover:', JSON.stringify(getColor(tokens.color.background['button-primary-hover']), null, 2));
console.log('Button Primary Active:', JSON.stringify(getColor(tokens.color.background['button-primary-active']), null, 2));
console.log('Text Interactive Default:', JSON.stringify(getColor(tokens.color.text.interactive.default), null, 2));
console.log('Text Interactive Hover:', JSON.stringify(getColor(tokens.color.text.interactive.hover), null, 2));

// Status Colors
console.log('\n✅ SUCCESS COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Text:', JSON.stringify(getColor(tokens.color.text.status.success), null, 2));
console.log('Background:', JSON.stringify(getColor(tokens.color.background.status.success), null, 2));
console.log('Border:', JSON.stringify(getColor(tokens.color.border.status.success), null, 2));

console.log('\n⚠️  WARNING COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Text:', JSON.stringify(getColor(tokens.color.text.status.warning), null, 2));
console.log('Background:', JSON.stringify(getColor(tokens.color.background.status.warning), null, 2));
console.log('Border:', JSON.stringify(getColor(tokens.color.border.status.warning), null, 2));

console.log('\n❌ ERROR COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Text:', JSON.stringify(getColor(tokens.color.text.status.error), null, 2));
console.log('Background:', JSON.stringify(getColor(tokens.color.background.status.error), null, 2));
console.log('Border:', JSON.stringify(getColor(tokens.color.border.status.error), null, 2));

console.log('\n💡 INFO COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Text:', JSON.stringify(getColor(tokens.color.text.status.info), null, 2));
console.log('Background:', JSON.stringify(getColor(tokens.color.background.status.info), null, 2));
console.log('Border:', JSON.stringify(getColor(tokens.color.border.status.info), null, 2));

// Link Colors
console.log('\n🔗 LINK COLORS (Light / Dark)');
console.log('─'.repeat(80));
console.log('Link Default:', JSON.stringify(getColor(tokens.color.text['link-default']), null, 2));
console.log('Link Hover:', JSON.stringify(getColor(tokens.color.text['link-hover']), null, 2));

console.log('\n═'.repeat(80));
console.log('Extraction complete!\n');
