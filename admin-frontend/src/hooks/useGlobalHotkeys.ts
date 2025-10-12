import { useHotkeys } from 'react-hotkeys-hook';
import { message } from 'antd';

/**
 * Global keyboard shortcuts for admin panel
 */
export const useGlobalHotkeys = () => {
  // Show help dialog
  useHotkeys('shift+?', (e) => {
    e.preventDefault();
    message.info('Quick help: Ctrl+N=New, Ctrl+S=Save, Ctrl+F=Search, /=Quick Search, Esc=Close');
  }, { enableOnFormTags: false });

  // Quick search (/)
  useHotkeys('/', (e) => {
    e.preventDefault();
    const searchInput = document.querySelector('input[type="search"], input[placeholder*="搜索"], input[placeholder*="Search"]') as HTMLInputElement;
    if (searchInput) {
      searchInput.focus();
    }
  }, { enableOnFormTags: false });

  return {
    // Can expose shortcuts info for help dialog
    shortcuts: [
      { key: 'Ctrl+N', description: 'Create new item' },
      { key: 'Ctrl+S', description: 'Save' },
      { key: 'Ctrl+F', description: 'Focus search' },
      { key: '/', description: 'Quick search' },
      { key: 'Esc', description: 'Close dialog' },
      { key: '?', description: 'Show help' },
    ],
  };
};

