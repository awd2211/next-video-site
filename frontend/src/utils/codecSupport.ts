/**
 * 视频编解码器支持检测工具
 * - AV1检测
 * - H.264/H.265检测
 * - 浏览器能力检测
 */

/**
 * 检测浏览器是否支持AV1解码
 */
export function supportsAV1(): boolean {
  if (typeof window === 'undefined') return false;

  const video = document.createElement('video');

  // 方法1: canPlayType检测
  // AV1 codec string: av01.0.05M.08
  // - av01: AV1
  // - 0: Profile 0 (Main)
  // - 05: Level 5.0
  // - M: Main tier
  // - 08: 8-bit depth
  const canPlay = video.canPlayType('video/mp4; codecs="av01.0.05M.08"');

  if (canPlay === 'probably' || canPlay === 'maybe') {
    return true;
  }

  // 方法2: MediaSource检测
  if (typeof MediaSource !== 'undefined') {
    return MediaSource.isTypeSupported('video/mp4; codecs="av01.0.05M.08"');
  }

  return false;
}

/**
 * 检测浏览器是否支持H.265/HEVC
 */
export function supportsHEVC(): boolean {
  if (typeof window === 'undefined') return false;

  const video = document.createElement('video');
  return video.canPlayType('video/mp4; codecs="hev1.1.6.L93.B0"') !== '';
}

/**
 * 检测浏览器是否支持VP9
 */
export function supportsVP9(): boolean {
  if (typeof window === 'undefined') return false;

  const video = document.createElement('video');
  return video.canPlayType('video/webm; codecs="vp9"') !== '';
}

/**
 * 获取所有支持的编解码器
 */
export interface CodecSupport {
  h264: boolean;
  h265: boolean;
  vp9: boolean;
  av1: boolean;
}

export function getSupportedCodecs(): CodecSupport {
  if (typeof window === 'undefined') {
    return { h264: false, h265: false, vp9: false, av1: false };
  }

  const video = document.createElement('video');

  return {
    h264: video.canPlayType('video/mp4; codecs="avc1.42E01E"') !== '',
    h265: supportsHEVC(),
    vp9: supportsVP9(),
    av1: supportsAV1(),
  };
}

/**
 * 获取浏览器信息
 */
export function getBrowserInfo(): {
  name: string;
  version: string;
  supportsAV1: boolean;
} {
  const ua = navigator.userAgent;
  let name = 'Unknown';
  let version = 'Unknown';

  // Chrome
  if (/Chrome/.test(ua) && !/Edge/.test(ua)) {
    name = 'Chrome';
    const match = ua.match(/Chrome\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  }
  // Firefox
  else if (/Firefox/.test(ua)) {
    name = 'Firefox';
    const match = ua.match(/Firefox\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  }
  // Safari
  else if (/Safari/.test(ua) && !/Chrome/.test(ua)) {
    name = 'Safari';
    const match = ua.match(/Version\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  }
  // Edge
  else if (/Edg/.test(ua)) {
    name = 'Edge';
    const match = ua.match(/Edg\/(\d+)/);
    version = match ? match[1] : 'Unknown';
  }

  return {
    name,
    version,
    supportsAV1: supportsAV1(),
  };
}

/**
 * 获取最佳视频URL (AV1优先,自动降级)
 */
export interface VideoUrls {
  av1_master_url?: string;
  hls_master_url: string;
  is_av1_available: boolean;
}

export function getBestVideoUrl(video: VideoUrls): string {
  // 优先AV1 (如果浏览器支持且视频有AV1版本)
  if (video.is_av1_available && video.av1_master_url && supportsAV1()) {
    return video.av1_master_url;
  }

  // 降级到H.264
  return video.hls_master_url;
}

/**
 * 获取编解码器名称
 */
export function getCodecName(url: string, video: VideoUrls): 'av1' | 'h264' {
  if (url === video.av1_master_url) {
    return 'av1';
  }
  return 'h264';
}

/**
 * 估算带宽节省
 */
export function estimateBandwidthSavings(
  durationMinutes: number,
  quality: '1080p' | '720p' | '480p' = '1080p'
): {
  h264SizeMB: number;
  av1SizeMB: number;
  savingsMB: number;
  savingsPercent: number;
} {
  // 平均码率 (Mbps)
  const bitrates = {
    '1080p': { h264: 5, av1: 2.2 },
    '720p': { h264: 3, av1: 1.2 },
    '480p': { h264: 1.5, av1: 0.6 },
  };

  const bitrate = bitrates[quality];
  const durationSeconds = durationMinutes * 60;

  // 文件大小 (MB)
  const h264SizeMB = (bitrate.h264 * durationSeconds * 1000) / 8 / 1024;
  const av1SizeMB = (bitrate.av1 * durationSeconds * 1000) / 8 / 1024;
  const savingsMB = h264SizeMB - av1SizeMB;
  const savingsPercent = (savingsMB / h264SizeMB) * 100;

  return {
    h264SizeMB: Math.round(h264SizeMB),
    av1SizeMB: Math.round(av1SizeMB),
    savingsMB: Math.round(savingsMB),
    savingsPercent: Math.round(savingsPercent),
  };
}
