import { GlobalOutlined } from '@ant-design/icons';
import { Dropdown, Space } from 'antd';
import type { MenuProps } from 'antd';
import { useLanguage } from '../contexts/LanguageContext';
import { useQueryClient } from '@tanstack/react-query';

const LanguageSwitcher = () => {
  const { language, setLanguage } = useLanguage();
  const queryClient = useQueryClient();

  const handleLanguageChange = (lang: 'zh-CN' | 'en-US' | 'zh-TW' | 'ja-JP' | 'de-DE' | 'fr-FR') => {
    setLanguage(lang);
    // 清除所有查询缓存，重新获取本地化数据
    queryClient.invalidateQueries();
  };

  const items: MenuProps['items'] = [
    {
      key: 'zh-CN',
      label: '简体中文',
      icon: <span>🇨🇳</span>,
      onClick: () => handleLanguageChange('zh-CN'),
    },
    {
      key: 'en-US',
      label: 'English',
      icon: <span>🇺🇸</span>,
      onClick: () => handleLanguageChange('en-US'),
    },
    {
      key: 'zh-TW',
      label: '繁體中文',
      icon: <span>🇹🇼</span>,
      onClick: () => handleLanguageChange('zh-TW'),
    },
    {
      key: 'ja-JP',
      label: '日本語',
      icon: <span>🇯🇵</span>,
      onClick: () => handleLanguageChange('ja-JP'),
    },
    {
      key: 'de-DE',
      label: 'Deutsch',
      icon: <span>🇩🇪</span>,
      onClick: () => handleLanguageChange('de-DE'),
    },
    {
      key: 'fr-FR',
      label: 'Français',
      icon: <span>🇫🇷</span>,
      onClick: () => handleLanguageChange('fr-FR'),
    },
  ];

  const languageLabels: Record<string, string> = {
    'zh-CN': '简体中文',
    'en-US': 'English',
    'zh-TW': '繁體中文',
    'ja-JP': '日本語',
    'de-DE': 'Deutsch',
    'fr-FR': 'Français',
  };

  const currentLanguageLabel = languageLabels[language] || '简体中文';

  return (
    <Dropdown menu={{ items, selectedKeys: [language] }} placement="bottomRight">
      <Space style={{ cursor: 'pointer' }}>
        <GlobalOutlined />
        <span>{currentLanguageLabel}</span>
      </Space>
    </Dropdown>
  );
};

export default LanguageSwitcher;

