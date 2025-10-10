/**
 * AV1视频播放器组件
 * - 自动检测AV1支持
 * - 自动降级到H.264
 * - 显示编解码器指示器
 */
import React, { useEffect, useRef, useState } from 'react';
import videojs from 'video.js';
import 'video.js/dist/video-js.css';
import { supportsAV1, getBestVideoUrl, getCodecName, getBrowserInfo } from '@/utils/codecSupport';
import type Player from 'video.js/dist/types/player';

interface AV1PlayerProps {
  video: {
    id: number;
    title: string;
    av1_master_url?: string;
    hls_master_url: string;
    is_av1_available: boolean;
    poster_url?: string;
    duration?: number;
  };
  onPlay?: () => void;
  onPause?: () => void;
  onEnded?: () => void;
  onError?: (error: any) => void;
}

export const AV1Player: React.FC<AV1PlayerProps> = ({
  video,
  onPlay,
  onPause,
  onEnded,
  onError,
}) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const playerRef = useRef<Player | null>(null);
  const [codecUsed, setCodecUsed] = useState<'av1' | 'h264'>('h264');
  const [loadError, setLoadError] = useState<string | null>(null);

  useEffect(() => {
    if (!videoRef.current) return;

    // 检测浏览器AV1支持
    const browserInfo = getBrowserInfo();
    console.log('浏览器信息:', browserInfo);
    console.log('AV1支持:', supportsAV1());

    // 初始化Video.js播放器
    const player = videojs(videoRef.current, {
      controls: true,
      fluid: true,
      responsive: true,
      poster: video.poster_url,
      preload: 'metadata',
      html5: {
        vhs: {
          overrideNative: true,
        },
        nativeAudioTracks: false,
        nativeVideoTracks: false,
      },
    });

    playerRef.current = player;

    // 选择最佳视频源
    const videoUrl = getBestVideoUrl({
      av1_master_url: video.av1_master_url,
      hls_master_url: video.hls_master_url,
      is_av1_available: video.is_av1_available,
    });

    const codec = getCodecName(videoUrl, {
      av1_master_url: video.av1_master_url,
      hls_master_url: video.hls_master_url,
      is_av1_available: video.is_av1_available,
    });

    player.src({
      src: videoUrl,
      type: 'application/x-mpegURL',
    });

    setCodecUsed(codec);

    // 监听播放事件
    player.on('loadedmetadata', () => {
      console.log('✅ 视频元数据加载完成');
      console.log('使用编解码器:', codec === 'av1' ? 'AV1 (dav1d)' : 'H.264');
      console.log('视频URL:', videoUrl);
    });

    player.on('play', () => {
      console.log('▶️ 播放开始');
      onPlay?.();
    });

    player.on('pause', () => {
      console.log('⏸️ 播放暂停');
      onPause?.();
    });

    player.on('ended', () => {
      console.log('✅ 播放结束');
      onEnded?.();
    });

    // 错误处理 (AV1播放失败时自动降级)
    player.on('error', () => {
      const error = player.error();
      console.error('❌ 播放错误:', error);

      if (codec === 'av1' && video.hls_master_url) {
        console.warn('⚠️ AV1播放失败,自动降级到H.264...');
        setLoadError('AV1播放失败,已切换到H.264兼容模式');

        // 降级到H.264
        player.src({
          src: video.hls_master_url,
          type: 'application/x-mpegURL',
        });
        setCodecUsed('h264');
      } else {
        setLoadError(error?.message || '播放失败');
        onError?.(error);
      }
    });

    // 监听质量变化
    player.on('resolutionchange', () => {
      console.log('画质切换');
    });

    return () => {
      if (playerRef.current) {
        playerRef.current.dispose();
        playerRef.current = null;
      }
    };
  }, [video.id]);

  return (
    <div className="av1-player-container relative">
      {/* 编解码器指示器 */}
      <div className="absolute top-4 right-4 z-10">
        {codecUsed === 'av1' ? (
          <div className="bg-green-600 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg flex items-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            AV1 (节省56%流量)
          </div>
        ) : (
          <div className="bg-yellow-600 text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
            H.264 (兼容模式)
          </div>
        )}
      </div>

      {/* 视频播放器 */}
      <div data-vjs-player>
        <video
          ref={videoRef}
          className="video-js vjs-big-play-centered vjs-16-9"
        />
      </div>

      {/* 错误提示 */}
      {loadError && (
        <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
          <p className="text-sm text-yellow-800">⚠️ {loadError}</p>
        </div>
      )}

      {/* AV1不支持提示 */}
      {!supportsAV1() && video.is_av1_available && (
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
          <h4 className="text-sm font-medium text-blue-900 mb-2">
            💡 提示: 您的浏览器不支持AV1
          </h4>
          <p className="text-sm text-blue-700">
            更新到最新版Chrome/Firefox/Safari可享受:
          </p>
          <ul className="mt-2 text-sm text-blue-600 list-disc list-inside">
            <li>节省56%流量</li>
            <li>更快的加载速度</li>
            <li>更高的视频质量</li>
          </ul>
        </div>
      )}

      {/* 统计信息 (开发模式) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-3 bg-gray-100 rounded-md text-xs font-mono">
          <div>Video ID: {video.id}</div>
          <div>Codec: {codecUsed.toUpperCase()}</div>
          <div>AV1 Available: {video.is_av1_available ? 'Yes' : 'No'}</div>
          <div>Browser Supports AV1: {supportsAV1() ? 'Yes' : 'No'}</div>
        </div>
      )}
    </div>
  );
};

export default AV1Player;
