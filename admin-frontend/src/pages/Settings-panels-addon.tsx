/**
 * Settings Page - 新增面板代码片段
 * 将以下代码片段插入到 Settings.tsx 中的适当位置
 */

// ==========================================
// 1. 在邮件面板 (Panel 4) 的末尾，Form.Item 之后添加：
// ==========================================
/*
              <Divider orientation="left" plain>
                测试邮件配置
              </Divider>

              <Card
                size="small"
                style={{
                  marginBottom: 16,
                  background: 'var(--card-bg, #f5f5f5)'
                }}
              >
                <Space direction="vertical" style={{ width: '100%' }}>
                  <Text type="secondary">发送测试邮件以验证 SMTP 配置是否正确</Text>
                  <Button
                    icon={<MailOutlined />}
                    onClick={() => setEmailTestModalVisible(true)}
                  >
                    发送测试邮件
                  </Button>
                  {settings?.smtp_last_test_at && (
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary">最后测试: </Text>
                      <Text>{new Date(settings.smtp_last_test_at).toLocaleString()}</Text>
                      {' '}
                      <Tag color={settings.smtp_last_test_status === 'success' ? 'success' : 'error'}>
                        {settings.smtp_last_test_status === 'success' ? '成功' : '失败'}
                      </Tag>
                    </div>
                  )}
                </Space>
              </Card>
*/

// ==========================================
// 2. 在安全配置面板 (Panel 5) 之后，添加缓存管理面板：
// ==========================================
/*
          {/* Panel 6: 缓存管理 *\/}
          {filteredSections.find((s) => s.key === 'cache') && (
            <Panel header="🗄️ 缓存管理" key="cache" className="settings-panel">
              <p className="panel-description">管理Redis缓存并查看统计信息</p>

              <Card size="small" style={{ marginBottom: 16 }}>
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                  <div>
                    <Button
                      icon={<DatabaseOutlined />}
                      onClick={fetchCacheStats}
                      style={{ marginRight: 8 }}
                    >
                      查看缓存统计
                    </Button>
                    <Text type="secondary">查看缓存命中率和性能指标</Text>
                  </div>

                  <Divider style={{ margin: '8px 0' }} />

                  <div>
                    <Text strong>清除缓存</Text>
                    <div style={{ marginTop: 8 }}>
                      <Space wrap>
                        <Button
                          danger
                          icon={<ClearOutlined />}
                          onClick={() => {
                            Modal.confirm({
                              title: '确认清除所有缓存？',
                              content: '此操作将清除Redis中的所有缓存数据',
                              onOk: () => handleClearCache(['all'])
                            });
                          }}
                        >
                          清除所有缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['videos:*'])}>
                          清除视频缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['categories:*'])}>
                          清除分类缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['users:*'])}>
                          清除用户缓存
                        </Button>
                        <Button onClick={() => handleClearCache(['system_settings'])}>
                          清除设置缓存
                        </Button>
                      </Space>
                    </div>
                  </div>
                </Space>
              </Card>
            </Panel>
          )}
*/

// ==========================================
// 3. 在缓存管理面板之后，添加备份恢复面板：
// ==========================================
/*
          {/* Panel 7: 备份与恢复 *\/}
          {filteredSections.find((s) => s.key === 'backup') && (
            <Panel header="💾 备份与恢复" key="backup" className="settings-panel">
              <p className="panel-description">导出和导入系统设置</p>

              <Card size="small">
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                  <div>
                    <Text strong style={{ fontSize: 16 }}>导出备份</Text>
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                        将当前所有设置导出为 JSON 文件
                      </Text>
                      <Button
                        type="primary"
                        icon={<DownloadOutlined />}
                        onClick={handleExportBackup}
                      >
                        下载备份文件
                      </Button>
                    </div>
                  </div>

                  <Divider style={{ margin: '8px 0' }} />

                  <div>
                    <Text strong style={{ fontSize: 16 }}>导入备份</Text>
                    <div style={{ marginTop: 8 }}>
                      <Text type="secondary" style={{ display: 'block', marginBottom: 8 }}>
                        从备份文件恢复设置（将覆盖当前设置）
                      </Text>
                      <Upload
                        accept=".json"
                        showUploadList={false}
                        beforeUpload={handleRestoreBackup}
                      >
                        <Button icon={<UploadOutlined />}>
                          选择备份文件
                        </Button>
                      </Upload>
                    </div>
                  </div>
                </Space>
              </Card>
            </Panel>
          )}
*/

// ==========================================
// 4. 在 Settings 组件的 return 语句末尾，</div> 之前添加模态框：
// ==========================================
/*
      {/* 邮件测试模态框 *\/}
      <Modal
        title="发送测试邮件"
        open={emailTestModalVisible}
        onCancel={() => setEmailTestModalVisible(false)}
        footer={null}
      >
        <Form onFinish={(values) => handleTestEmail(values.email)}>
          <Form.Item
            name="email"
            label="邮箱地址"
            rules={[
              { required: true, message: '请输入邮箱地址' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="输入测试邮箱地址" />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" loading={emailTestLoading}>
                发送测试
              </Button>
              <Button onClick={() => setEmailTestModalVisible(false)}>
                取消
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* 缓存统计模态框 *\/}
      <Modal
        title="缓存统计"
        open={cacheStatsModalVisible}
        onCancel={() => setCacheStatsModalVisible(false)}
        footer={null}
        width={800}
      >
        {cacheStats && (
          <>
            <Row gutter={16} style={{ marginBottom: 24 }}>
              <Col span={8}>
                <Statistic
                  title="总命中数"
                  value={cacheStats.summary.total_hits}
                  valueStyle={{ color: '#3f8600' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="总未命中数"
                  value={cacheStats.summary.total_misses}
                  valueStyle={{ color: '#cf1322' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="平均命中率"
                  value={cacheStats.summary.average_hit_rate}
                  suffix="%"
                  valueStyle={{ color: '#1890ff' }}
                  precision={2}
                />
              </Col>
            </Row>
            <Divider />
            <Text strong>最近 7 天统计：</Text>
            <div style={{ marginTop: 16 }}>
              {cacheStats.stats.map((stat: any) => (
                <div key={stat.date} style={{ marginBottom: 8 }}>
                  <Text>{stat.date}: </Text>
                  <Tag color="green">{stat.hits} 命中</Tag>
                  <Tag color="red">{stat.misses} 未命中</Tag>
                  <Tag color="blue">{stat.hit_rate}% 命中率</Tag>
                </div>
              ))}
            </div>
          </>
        )}
      </Modal>
*/

export default {};
