/**
 * Resizable Sidebar Hook
 * 可拖拽调整宽度的侧边栏
 * 参考: VS Code, Notion, GitHub
 */

import { useState, useEffect, useCallback, useRef } from 'react';

interface UseResizableSidebarOptions {
  defaultWidth?: number;
  minWidth?: number;
  maxWidth?: number;
  storageKey?: string;
}

export const useResizableSidebar = ({
  defaultWidth = 260,
  minWidth = 200,
  maxWidth = 400,
  storageKey = 'sidebar-width',
}: UseResizableSidebarOptions = {}) => {
  // 从 localStorage 读取保存的宽度
  const getSavedWidth = () => {
    const saved = localStorage.getItem(storageKey);
    if (saved) {
      const width = parseInt(saved, 10);
      if (width >= minWidth && width <= maxWidth) {
        return width;
      }
    }
    return defaultWidth;
  };

  const [sidebarWidth, setSidebarWidth] = useState(getSavedWidth());
  const [isResizing, setIsResizing] = useState(false);
  const startXRef = useRef(0);
  const startWidthRef = useRef(0);

  // 开始拖拽
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
    startXRef.current = e.clientX;
    startWidthRef.current = sidebarWidth;

    // 禁止文本选择
    document.body.classList.add('resizing');
    document.body.style.userSelect = 'none';
    document.body.style.cursor = 'col-resize';
  }, [sidebarWidth]);

  // 拖拽中
  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;

    const delta = e.clientX - startXRef.current;
    const newWidth = startWidthRef.current + delta;

    // 限制最小/最大宽度
    if (newWidth >= minWidth && newWidth <= maxWidth) {
      setSidebarWidth(newWidth);
    }
  }, [isResizing, minWidth, maxWidth]);

  // 结束拖拽
  const handleMouseUp = useCallback(() => {
    if (!isResizing) return;

    setIsResizing(false);
    
    // 恢复文本选择
    document.body.classList.remove('resizing');
    document.body.style.userSelect = '';
    document.body.style.cursor = '';

    // 保存到 localStorage
    localStorage.setItem(storageKey, sidebarWidth.toString());
  }, [isResizing, sidebarWidth, storageKey]);

  // 监听鼠标事件
  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
    return undefined;
  }, [isResizing, handleMouseMove, handleMouseUp]);

  // 重置宽度
  const resetWidth = useCallback(() => {
    setSidebarWidth(defaultWidth);
    localStorage.setItem(storageKey, defaultWidth.toString());
  }, [defaultWidth, storageKey]);

  return {
    sidebarWidth,
    isResizing,
    handleMouseDown,
    resetWidth,
  };
};

