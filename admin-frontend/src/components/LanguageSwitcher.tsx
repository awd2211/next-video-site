import { GlobalOutlined } from '@ant-design/icons';
import { Dropdown, Space } from 'antd';
import type { MenuProps } from 'antd';
import { useLanguage } from '../contexts/LanguageContext';
import { useQueryClient } from '@tanstack/react-query';

const LanguageSwitcher = () => {
  const { language, setLanguage } = useLanguage();
  const queryClient = useQueryClient();

  const handleLanguageChange = (lang: 'zh-CN' | 'en-US') => {
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
  ];

  const currentLanguageLabel = language === 'zh-CN' ? '简体中文' : 'English';

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

