import { Modal, Table, Tag } from 'antd';
import { QuestionCircleOutlined } from '@ant-design/icons';

interface HotkeysHelpProps {
  visible: boolean;
  onClose: () => void;
}

const HotkeysHelp: React.FC<HotkeysHelpProps> = ({ visible, onClose }) => {
  const shortcuts = [
    { key: 'Ctrl + N', description: '新建项目 / Create New', category: '通用 / General' },
    { key: 'Ctrl + S', description: '保存 / Save', category: '编辑 / Edit' },
    { key: 'Ctrl + F', description: '搜索 / Search', category: '导航 / Navigation' },
    { key: '/', description: '快速搜索 / Quick Search', category: '导航 / Navigation' },
    { key: 'Esc', description: '关闭对话框 / Close Dialog', category: '通用 / General' },
    { key: '?', description: '显示帮助 / Show Help', category: '通用 / General' },
  ];

  const columns = [
    {
      title: '快捷键',
      dataIndex: 'key',
      key: 'key',
      width: 150,
      render: (key: string) => <Tag color="blue">{key}</Tag>,
    },
    {
      title: '说明',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 150,
    },
  ];

  return (
    <Modal
      title={
        <>
          <QuestionCircleOutlined /> 键盘快捷键 / Keyboard Shortcuts
        </>
      }
      open={visible}
      onCancel={onClose}
      footer={null}
      width={700}
    >
      <Table
        columns={columns}
        dataSource={shortcuts}
        pagination={false}
        size="small"
        rowKey="key"
      />
    </Modal>
  );
};

export default HotkeysHelp;


