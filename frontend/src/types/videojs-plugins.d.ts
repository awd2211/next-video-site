/**
 * TypeScript definitions for Video.js plugins
 */
import videojs from 'video.js'

declare module 'video.js' {
  export interface VideoJsPlayer {
    /**
     * HLS Quality Selector plugin
     * Allows users to manually select video quality levels
     */
    hlsQualitySelector?: (options?: {
      displayCurrentQuality?: boolean
      placementIndex?: number
      vjsIconClass?: string
    }) => void

    /**
     * Quality Levels plugin
     * Provides access to the list of available quality levels
     */
    qualityLevels?: () => QualityLevelList
  }

  export interface QualityLevel {
    id: string
    label: string
    width: number
    height: number
    bitrate: number
    enabled: boolean
  }

  export interface QualityLevelList extends Array<QualityLevel> {
    selectedIndex: number
    trigger(event: string): void
    on(event: string, callback: Function): void
  }
}

declare module 'videojs-contrib-quality-levels'
declare module 'videojs-hls-quality-selector'
