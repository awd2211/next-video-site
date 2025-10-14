#!/bin/bash
# Extract all AWS Cloudscape official colors

JSON_FILE="node_modules/@cloudscape-design/design-tokens/index-visual-refresh.json"

echo "🎨 AWS CLOUDSCAPE DESIGN SYSTEM - OFFICIAL COLORS"
echo "═══════════════════════════════════════════════════════════════════════════════"
echo ""

extract_color() {
    local token_name=$1
    local label=$2
    local value=$(cat $JSON_FILE | jq -r ".tokens.\"$token_name\".\"\\$value\"")
    if [ "$value" != "null" ]; then
        echo "$label:"
        echo "$value" | jq '.'
    fi
}

echo "📦 BACKGROUND COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-background-layout-main" "Layout Main"
extract_color "color-background-container-content" "Container Content"
extract_color "color-background-container-header" "Container Header"
extract_color "color-background-home-header" "Home Header"

echo ""
echo "✍️  TEXT COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-text-body-default" "Body Default"
extract_color "color-text-body-secondary" "Body Secondary"
extract_color "color-text-heading-default" "Heading Default"
extract_color "color-text-heading-secondary" "Heading Secondary"
extract_color "color-text-label" "Label"

echo ""
echo "🖼️  BORDER COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-border-divider-default" "Divider Default"
extract_color "color-border-input-default" "Input Default"

echo ""
echo "🔵 PRIMARY / INTERACTIVE COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-background-button-primary-default" "Button Primary Default"
extract_color "color-background-button-primary-hover" "Button Primary Hover"
extract_color "color-background-button-primary-active" "Button Primary Active"
extract_color "color-text-interactive-default" "Text Interactive Default"
extract_color "color-text-interactive-hover" "Text Interactive Hover"
extract_color "color-text-interactive-active" "Text Interactive Active"

echo ""
echo "✅ SUCCESS COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-text-status-success" "Success Text"
extract_color "color-background-status-success" "Success Background"
extract_color "color-border-status-success" "Success Border"

echo ""
echo "⚠️  WARNING COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-text-status-warning" "Warning Text"
extract_color "color-background-status-warning" "Warning Background"
extract_color "color-border-status-warning" "Warning Border"

echo ""
echo "❌ ERROR COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-text-status-error" "Error Text"
extract_color "color-background-status-error" "Error Background"
extract_color "color-border-status-error" "Error Border"

echo ""
echo "💡 INFO COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-text-status-info" "Info Text"
extract_color "color-background-status-info" "Info Background"
extract_color "color-border-status-info" "Info Border"

echo ""
echo "🔗 LINK COLORS"
echo "─────────────────────────────────────────────────────────────────────────────────"
extract_color "color-text-link-default" "Link Default"
extract_color "color-text-link-hover" "Link Hover"

echo ""
echo "═══════════════════════════════════════════════════════════════════════════════"
echo "✅ Extraction complete!"
