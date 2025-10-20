/**
 * Video.js Plugin Type Extensions
 * Extends the base Video.js Player interface with custom plugin types
 */

// HLS Quality Selector Plugin types
interface QualityLevel {
  height?: number
  width?: number
  bitrate?: number
  enabled: boolean
}

interface QualityLevels extends Array<QualityLevel> {
  selectedIndex: number
  on(event: string, callback: () => void): void
  off(event: string, callback: () => void): void
}

interface HLSQualitySelectorOptions {
  displayCurrentQuality?: boolean
  vjsIconClass?: string
  placementIndex?: number
}

// Note: Video.js plugins are added at runtime and may not have complete type definitions
// We use @ts-ignore in the actual code where these plugins are used
