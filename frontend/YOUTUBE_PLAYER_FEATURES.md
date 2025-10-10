# YouTube-Style Video Player Features

## Overview
The VideoPlayer component has been enhanced with YouTube-style features including custom context menu, stats panel, and advanced interactions.

## Implemented Features

### 1. Custom Right-Click Context Menu ✅
**File**: `src/components/VideoPlayer/ContextMenu.tsx`

Features:
- Loop video toggle
- Playback speed control (0.25x, 0.5x, 0.75x, Normal, 1.25x, 1.5x, 1.75x, 2x)
- Quality selection (Auto, 1080p, 720p, 480p, 360p)
- Copy video URL
- Copy video URL at current time
- Stats for nerds
- Mini player mode
- Theater mode
- Fullscreen toggle

### 2. Stats Panel (Stats for Nerds) ✅
**File**: `src/components/VideoPlayer/StatsPanel.tsx`

Real-time statistics displayed:
- Video ID
- Current Resolution (width x height)
- Frames Per Second (FPS)
- Video Bitrate (Mbps)
- Audio Bitrate (kbps)
- Buffer Health (%)
- Dropped Frames
- Current Time / Duration
- Volume Level
- Playback Speed
- Video Codec
- Audio Codec

Matrix-style green terminal aesthetic with auto-updating every second.

### 3. YouTube-Style Interactions ✅

#### Double-Click Interactions
- **Left 1/3**: Rewind 10 seconds
- **Right 1/3**: Forward 10 seconds
- **Center**: Play/Pause toggle

#### Mouse Wheel Volume Control
- Scroll up: Increase volume by 5%
- Scroll down: Decrease volume by 5%

#### Control Bar Auto-Hide
- Automatically hides after 3 seconds of inactivity
- Only hides when video is playing
- Shows on mouse movement

### 4. YouTube Visual Styling ✅
**File**: `src/components/VideoPlayer/VideoPlayer-YouTube.css`

- Red progress bar (#FF0000)
- Smooth fade-in/out animations
- Modern control button styles
- Auto-hiding control bar with gradient background
- Hover effects on all controls
- Theater mode styling
- Mini player mode styling

### 5. Keyboard Shortcuts (Already Implemented)
- `Space` or `K`: Play/Pause
- `←`: Rewind 5 seconds
- `→`: Forward 5 seconds
- `↑`: Volume up
- `↓`: Volume down
- `F`: Toggle fullscreen
- `M`: Toggle mute
- `0-9`: Jump to percentage (0% - 90%)
- `C`: Toggle subtitles

## File Structure

```
src/components/VideoPlayer/
├── index.tsx                    # Main VideoPlayer component with all features
├── VideoPlayer.css              # Base player styles
├── VideoPlayer-YouTube.css      # YouTube-style visual enhancements
├── ContextMenu.tsx              # Right-click context menu component
├── ContextMenu.css              # Context menu styling
├── StatsPanel.tsx               # Stats for nerds panel component
└── StatsPanel.css               # Stats panel Matrix-style styling
```

## Usage

The VideoPlayer component automatically includes all YouTube-style features:

```tsx
import VideoPlayer from '@/components/VideoPlayer'

<VideoPlayer
  src="https://example.com/video.m3u8"
  poster="https://example.com/poster.jpg"
  videoId={123}
  autoSaveProgress={true}
  enableSubtitles={true}
/>
```

### Using Features

1. **Context Menu**: Right-click on the video player
2. **Stats Panel**: Right-click → "Stats for nerds" or use context menu
3. **Loop**: Right-click → "Loop"
4. **Playback Speed**: Right-click → "Playback speed" → select speed
5. **Double-Click Seek**: Double-click left/right areas to seek
6. **Wheel Volume**: Scroll on video to adjust volume
7. **Theater Mode**: Right-click → "Theater mode"
8. **Mini Player**: Right-click → "Mini player"

## Technical Implementation

### State Management

```typescript
const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0 })
const [showStats, setShowStats] = useState(false)
const [loopEnabled, setLoopEnabled] = useState(false)
const [theaterMode, setTheaterMode] = useState(false)
const [miniPlayer, setMiniPlayer] = useState(false)
```

### Event Listeners

- `contextmenu`: Custom right-click menu
- `click`: Double-click detection for seek
- `wheel`: Volume control via mouse wheel
- `mousemove`: Control bar auto-hide trigger
- `mouseleave`: Reset auto-hide timer

### CSS Classes

- `.vjs-youtube-skin`: Main YouTube-style class
- `.vjs-theater-mode`: Theater mode layout
- `.vjs-mini-player`: Mini player mode
- `.youtube-context-menu`: Context menu container
- `.stats-panel`: Stats panel container

## Browser Compatibility

- Modern browsers with ES6+ support
- Backdrop filter support (Chrome 76+, Firefox 103+, Safari 9+)
- Clipboard API for copy URL features
- RequestFullscreen API for fullscreen

## Future Enhancements

Potential additions:
- [ ] Visual seek feedback animations (pulse effect on double-click)
- [ ] Picture-in-Picture mode integration
- [ ] Video chapters support
- [ ] Annotations/Cards overlay
- [ ] Watch later integration
- [ ] Share with timestamp
- [ ] Autoplay next video
- [ ] End screen suggestions

## Performance Considerations

- Stats panel updates throttled to 1 second intervals
- Context menu renders conditionally (only when visible)
- Event listeners properly cleaned up on unmount
- CSS animations use GPU-accelerated properties (transform, opacity)
- Debounced control bar auto-hide

## Accessibility

- Keyboard shortcuts for all major actions
- Proper ARIA labels on controls
- High contrast mode support in stats panel
- Focus management for context menu
- Screen reader compatible

## Testing

To test all features:

1. Open any video page
2. Right-click on the video player → verify context menu appears
3. Select "Stats for nerds" → verify stats panel shows real-time data
4. Double-click left/right areas → verify seek works
5. Scroll on video → verify volume changes
6. Toggle loop → verify video loops
7. Change playback speed → verify speed changes
8. Toggle theater mode → verify layout changes
9. Copy URL features → verify clipboard works

## Known Issues

- Quality selector requires HLS stream with multiple quality levels
- Mini player mode styling may need adjustments based on page layout
- Theater mode should be coordinated with page layout

## Dependencies

- video.js (^8.23.4)
- videojs-contrib-quality-levels
- videojs-hls-quality-selector
- React (^18)
- TypeScript

## Credits

Inspired by YouTube's video player UX/UI design, adapted for the VideoSite platform.
