/**
 * Video.js Plugins Initialization
 *
 * This file imports Video.js plugins which will auto-register themselves.
 * Import this file ONCE at the top level to ensure plugins are available globally.
 */

// These plugins auto-register themselves when imported
import 'videojs-contrib-quality-levels'
import 'videojs-hls-quality-selector'

// Export a flag to confirm plugins are loaded
export const videojsPluginsLoaded = true
