import { Slider, Typography, Space, Tooltip } from 'antd';
import { useTranslation } from 'react-i18next';
import { StarOutlined, StarFilled } from '@ant-design/icons';

const { Text } = Typography;

interface QualityScoreSliderProps {
  value?: number;
  onChange?: (value: number) => void;
  disabled?: boolean;
  showLabel?: boolean;
  size?: 'small' | 'default' | 'large';
}

const QualityScoreSlider: React.FC<QualityScoreSliderProps> = ({
  value = 0,
  onChange,
  disabled = false,
  showLabel = true,
  size = 'default',
}) => {
  const { t } = useTranslation();

  const getQualityLabel = (score: number): string => {
    if (score === 0) return t('video.operation.qualityNotRated') || '未评分';
    if (score < 30) return t('video.operation.qualityPoor') || '差';
    if (score < 60) return t('video.operation.qualityFair') || '中';
    if (score < 80) return t('video.operation.qualityGood') || '良';
    return t('video.operation.qualityExcellent') || '优';
  };

  const getQualityColor = (score: number): string => {
    if (score === 0) return '#d9d9d9';
    if (score < 30) return '#ff4d4f';
    if (score < 60) return '#faad14';
    if (score < 80) return '#1890ff';
    return '#52c41a';
  };

  const marks = {
    0: {
      style: { color: '#d9d9d9' },
      label: <Text type="secondary">0</Text>,
    },
    30: {
      style: { color: '#ff4d4f' },
      label: <Text type="danger">差</Text>,
    },
    60: {
      style: { color: '#faad14' },
      label: <Text style={{ color: '#faad14' }}>中</Text>,
    },
    80: {
      style: { color: '#1890ff' },
      label: <Text style={{ color: '#1890ff' }}>良</Text>,
    },
    100: {
      style: { color: '#52c41a' },
      label: <Text style={{ color: '#52c41a' }}>优</Text>,
    },
  };

  const renderStars = (score: number) => {
    const starCount = Math.round((score / 100) * 5);
    const stars = [];
    for (let i = 0; i < 5; i++) {
      stars.push(
        i < starCount ? (
          <StarFilled key={i} style={{ color: getQualityColor(score), fontSize: size === 'small' ? 12 : 16 }} />
        ) : (
          <StarOutlined key={i} style={{ color: '#d9d9d9', fontSize: size === 'small' ? 12 : 16 }} />
        )
      );
    }
    return stars;
  };

  return (
    <div style={{ width: '100%' }}>
      {showLabel && (
        <Space style={{ marginBottom: 8 }}>
          <Text strong>{t('video.operation.qualityScore') || '质量评分'}:</Text>
          <Text style={{ color: getQualityColor(value), fontWeight: 'bold' }}>{value}</Text>
          <Text type="secondary">({getQualityLabel(value)})</Text>
          <Space size={2}>{renderStars(value)}</Space>
        </Space>
      )}

      <Tooltip
        title={`${t('video.operation.currentScore') || '当前评分'}: ${value} - ${getQualityLabel(value)}`}
        placement="top"
      >
        <Slider
          min={0}
          max={100}
          marks={marks}
          step={1}
          value={value}
          onChange={(val) => onChange?.(val)}
          disabled={disabled}
          tooltip={{
            formatter: (val) => (val !== undefined ? `${val} - ${getQualityLabel(val)}` : ''),
          }}
          trackStyle={{ backgroundColor: getQualityColor(value) }}
          handleStyle={{ borderColor: getQualityColor(value) }}
        />
      </Tooltip>

      <div style={{ marginTop: 8 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          {t('video.operation.qualityScoreHelp') ||
            '评分范围: 0-30差, 30-60中, 60-80良, 80-100优'}
        </Text>
      </div>
    </div>
  );
};

export default QualityScoreSlider;
