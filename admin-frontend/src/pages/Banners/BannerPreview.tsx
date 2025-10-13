import { Modal, Button, Space } from 'antd'
import { EyeOutlined } from '@ant-design/icons'
import { useState } from 'react'

interface BannerPreviewProps {
  banner: {
    title: string
    image_url: string
    description?: string
    link_url?: string
  }
}

export const BannerPreviewButton: React.FC<BannerPreviewProps> = ({ banner }) => {
  const [visible, setVisible] = useState(false)

  return (
    <>
      <Button
        type="link"
        size="small"
        icon={<EyeOutlined />}
        onClick={() => setVisible(true)}
      >
        预览
      </Button>

      <Modal
        title="横幅预览"
        open={visible}
        onCancel={() => setVisible(false)}
        footer={[
          <Button key="close" onClick={() => setVisible(false)}>
            关闭
          </Button>,
        ]}
        width="90%"
        style={{ maxWidth: 1400 }}
      >
        <div
          style={{
            background: '#f5f5f5',
            padding: '20px',
            borderRadius: '8px',
          }}
        >
          {/* 桌面预览 */}
          <div style={{ marginBottom: '20px' }}>
            <h3 style={{ marginBottom: '12px', color: '#0073bb' }}>
              🖥️ 桌面预览 (1920x600)
            </h3>
            <div
              style={{
                position: 'relative',
                width: '100%',
                height: 0,
                paddingBottom: '31.25%', // 1920/600 = 31.25%
                backgroundColor: '#000',
                borderRadius: '8px',
                overflow: 'hidden',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              }}
            >
              <img
                src={banner.image_url}
                alt={banner.title}
                style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                }}
              />
              {/* 标题叠加层 */}
              <div
                style={{
                  position: 'absolute',
                  bottom: 0,
                  left: 0,
                  right: 0,
                  padding: '24px',
                  background: 'linear-gradient(to top, rgba(0,0,0,0.8), transparent)',
                  color: '#fff',
                }}
              >
                <h2
                  style={{
                    color: '#fff',
                    margin: 0,
                    marginBottom: '8px',
                    fontSize: '28px',
                    fontWeight: 600,
                  }}
                >
                  {banner.title}
                </h2>
                {banner.description && (
                  <p style={{ margin: 0, fontSize: '16px', opacity: 0.9 }}>
                    {banner.description}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* 移动端预览 */}
          <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
            <div style={{ flex: '1 1 300px' }}>
              <h3 style={{ marginBottom: '12px', color: '#0073bb' }}>
                📱 移动端预览
              </h3>
              <div
                style={{
                  width: '375px',
                  maxWidth: '100%',
                  margin: '0 auto',
                }}
              >
                <div
                  style={{
                    position: 'relative',
                    width: '100%',
                    height: 0,
                    paddingBottom: '50%',
                    backgroundColor: '#000',
                    borderRadius: '8px',
                    overflow: 'hidden',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                  }}
                >
                  <img
                    src={banner.image_url}
                    alt={banner.title}
                    style={{
                      position: 'absolute',
                      top: 0,
                      left: 0,
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                    }}
                  />
                </div>
              </div>
            </div>

            {/* 横幅信息 */}
            <div style={{ flex: '1 1 400px' }}>
              <h3 style={{ marginBottom: '12px', color: '#0073bb' }}>📝 横幅信息</h3>
              <div
                style={{
                  background: '#fff',
                  padding: '16px',
                  borderRadius: '8px',
                  border: '1px solid #e9e9e7',
                }}
              >
                <div style={{ marginBottom: '12px' }}>
                  <strong style={{ color: '#37352f' }}>标题:</strong>
                  <div style={{ marginTop: '4px', color: '#787774' }}>{banner.title}</div>
                </div>

                {banner.description && (
                  <div style={{ marginBottom: '12px' }}>
                    <strong style={{ color: '#37352f' }}>描述:</strong>
                    <div style={{ marginTop: '4px', color: '#787774' }}>
                      {banner.description}
                    </div>
                  </div>
                )}

                {banner.link_url && (
                  <div>
                    <strong style={{ color: '#37352f' }}>链接:</strong>
                    <div
                      style={{
                        marginTop: '4px',
                        color: '#0073bb',
                        fontFamily: 'Monaco, Menlo, Consolas, monospace',
                        fontSize: '13px',
                        wordBreak: 'break-all',
                      }}
                    >
                      {banner.link_url}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </Modal>
    </>
  )
}

export default BannerPreviewButton
