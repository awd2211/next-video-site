import { useState } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  message,
  Tag,
  Spin,
  Empty,
  Divider,
  Alert,
} from 'antd';
import {
  SendOutlined,
  ThunderboltOutlined,
  RobotOutlined,
  ClockCircleOutlined,
  ApiOutlined,
} from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import ReactMarkdown from 'react-markdown';
import { testAIProvider, chatWithAI, type AIProvider } from '@/services/aiManagement';

interface AITestPanelProps {
  provider: AIProvider;
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  tokens?: number;
  latency?: number;
}

const AITestPanel: React.FC<AITestPanelProps> = ({ provider }) => {
  const { t } = useTranslation();
  const [inputMessage, setInputMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [testResult, setTestResult] = useState<any>(null);

  // Test connection mutation
  const testMutation = useMutation({
    mutationFn: () => testAIProvider(provider.id, { message: 'Hello' }),
    onSuccess: (data) => {
      setTestResult(data);
      if (data.success) {
        message.success(t('ai.testSuccess'));
      } else {
        message.error(t('ai.testFailed'));
      }
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('ai.testFailed'));
    },
  });

  // Chat mutation
  const chatMutation = useMutation({
    mutationFn: (messages: Array<{ role: string; content: string }>) =>
      chatWithAI({
        provider_id: provider.id,
        messages,
      }),
    onSuccess: (data) => {
      if (data.success && data.response) {
        setChatHistory((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: data.response!,
            timestamp: new Date(),
            tokens: data.tokens_used,
            latency: data.latency_ms,
          },
        ]);
      } else {
        message.error(data.error || t('ai.chatFailed'));
      }
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || t('ai.chatFailed'));
    },
  });

  const handleTestConnection = () => {
    testMutation.mutate();
  };

  const handleSendMessage = () => {
    if (!inputMessage.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setChatHistory((prev) => [...prev, userMessage]);

    // Prepare messages for API
    const messages = [...chatHistory, userMessage].map((msg) => ({
      role: msg.role,
      content: msg.content,
    }));

    chatMutation.mutate(messages);
    setInputMessage('');
  };

  const handleClearHistory = () => {
    setChatHistory([]);
    setTestResult(null);
  };

  return (
    <div className="ai-test-panel">
      {/* Connection Test */}
      <Card
        title={
          <Space>
            <ThunderboltOutlined />
            {t('ai.connectionTest')}
          </Space>
        }
        extra={
          <Button
            type="primary"
            size="small"
            icon={<ThunderboltOutlined />}
            onClick={handleTestConnection}
            loading={testMutation.isPending}
          >
            {t('ai.test')}
          </Button>
        }
        size="small"
        style={{ marginBottom: 16 }}
      >
        {testResult ? (
          <Alert
            message={testResult.success ? t('ai.connectionSuccess') : t('ai.connectionFailed')}
            description={
              <Space direction="vertical" style={{ width: '100%' }}>
                <div>{testResult.response || testResult.error}</div>
                {testResult.latency_ms && (
                  <Tag icon={<ClockCircleOutlined />} color="blue">
                    {testResult.latency_ms}ms
                  </Tag>
                )}
              </Space>
            }
            type={testResult.success ? 'success' : 'error'}
            showIcon
          />
        ) : (
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={t('ai.noTestResult')}
          />
        )}
      </Card>

      {/* Chat Interface */}
      <Card
        title={
          <Space>
            <RobotOutlined />
            {t('ai.chatTest')}
          </Space>
        }
        extra={
          <Button size="small" onClick={handleClearHistory}>
            {t('ai.clearHistory')}
          </Button>
        }
        size="small"
      >
        {/* Chat History */}
        <div
          className="chat-history"
          style={{
            height: 400,
            overflowY: 'auto',
            marginBottom: 16,
            padding: 16,
            backgroundColor: '#f5f5f5',
            borderRadius: 4,
          }}
        >
          {chatHistory.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={t('ai.noChatHistory')}
            />
          ) : (
            chatHistory.map((msg, index) => (
              <div
                key={index}
                className={`chat-message ${msg.role}`}
                style={{
                  marginBottom: 16,
                  padding: 12,
                  borderRadius: 8,
                  backgroundColor: msg.role === 'user' ? '#e6f7ff' : '#fff',
                  border: `1px solid ${msg.role === 'user' ? '#91d5ff' : '#d9d9d9'}`,
                }}
              >
                <div style={{ marginBottom: 8 }}>
                  <Space>
                    <Tag color={msg.role === 'user' ? 'blue' : 'green'}>
                      {msg.role === 'user' ? t('ai.user') : t('ai.assistant')}
                    </Tag>
                    <span style={{ fontSize: 12, color: '#999' }}>
                      {msg.timestamp.toLocaleTimeString()}
                    </span>
                    {msg.tokens && (
                      <Tag icon={<ApiOutlined />} color="purple">
                        {msg.tokens} tokens
                      </Tag>
                    )}
                    {msg.latency && (
                      <Tag icon={<ClockCircleOutlined />} color="cyan">
                        {msg.latency}ms
                      </Tag>
                    )}
                  </Space>
                </div>
                <div className="message-content" style={{ whiteSpace: 'pre-wrap' }}>
                  {msg.role === 'assistant' ? (
                    <ReactMarkdown>{msg.content}</ReactMarkdown>
                  ) : (
                    msg.content
                  )}
                </div>
              </div>
            ))
          )}
          {chatMutation.isPending && (
            <div style={{ textAlign: 'center', padding: 20 }}>
              <Spin tip={t('ai.thinking')} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <Space.Compact style={{ width: '100%' }}>
          <Input
            placeholder={t('ai.inputPlaceholder')}
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onPressEnter={handleSendMessage}
            disabled={chatMutation.isPending}
            size="large"
          />
          <Button
            type="primary"
            icon={<SendOutlined />}
            onClick={handleSendMessage}
            loading={chatMutation.isPending}
            disabled={!inputMessage.trim()}
            size="large"
          >
            {t('ai.send')}
          </Button>
        </Space.Compact>

        <Divider style={{ margin: '12px 0' }} />

        {/* Provider Info */}
        <Space wrap>
          <Tag color="blue">{provider.provider_type}</Tag>
          <Tag color="green">{provider.model_name}</Tag>
          <Tag>Temp: {provider.temperature || 0.7}</Tag>
          <Tag>Max Tokens: {provider.max_tokens || 2048}</Tag>
        </Space>
      </Card>
    </div>
  );
};

export default AITestPanel;
