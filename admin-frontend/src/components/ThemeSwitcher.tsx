import { BulbOutlined, BulbFilled } from '@ant-design/icons';
import { Switch, Space, Tooltip } from 'antd';
import { useTheme } from '../contexts/ThemeContext';

const ThemeSwitcher = () => {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';

  return (
    <Tooltip title={isDark ? '切换到亮色模式' : '切换到暗黑模式'}>
      <Space>
        <Switch
          checked={isDark}
          onChange={toggleTheme}
          checkedChildren={<BulbFilled />}
          unCheckedChildren={<BulbOutlined />}
        />
      </Space>
    </Tooltip>
  );
};

export default ThemeSwitcher;


