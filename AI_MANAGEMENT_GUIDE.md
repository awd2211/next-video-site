# AI管理模块使用指南

## 概览

AI管理模块允许您在管理后台中集中管理和测试多个AI提供商(OpenAI、Grok、Google AI)的配置。

## 功能特性

### ✅ 支持的AI提供商
- **OpenAI**: GPT-4 Turbo, GPT-4, GPT-3.5 Turbo, GPT-4o, GPT-4o Mini
- **Grok (xAI)**: Grok Beta, Grok 2 Latest, Grok 2 (2024-12-12)
- **Google AI**: Gemini Pro, Gemini Pro Vision, Gemini 1.5 Pro, Gemini 1.5 Flash

### ✅ 核心功能
- 🔧 **配置管理**: 添加、编辑、删除AI提供商配置
- 🧪 **连接测试**: 实时测试API连接状态
- 💬 **聊天测试**: 在管理界面直接与AI对话
- 📊 **使用统计**: 查看请求次数和令牌使用情况
- 🎛️ **参数调节**: 灵活配置temperature、max_tokens等参数
- 🔐 **安全存储**: API密钥加密存储
- 🌍 **多语言**: 支持中英文切换

## 快速开始

### 1. 访问AI管理页面

1. 登录管理后台 (http://localhost:3001)
2. 在左侧菜单找到"系统"分组
3. 点击"AI管理"(带机器人图标🤖)

### 2. 添加AI提供商

#### OpenAI配置示例

1. 点击"添加提供商"按钮
2. 填写配置信息:
   ```
   名称: GPT-4 Production
   提供商类型: OpenAI
   描述: 生产环境使用的GPT-4配置
   API密钥: sk-xxxxxxxxxxxxxxxxxxxxx
   基础URL: (留空使用默认) 或 https://api.openai.com/v1
   模型: GPT-4 Turbo
   最大令牌数: 4096
   温度: 0.7 (0=更确定性，2=更创造性)
   ```
3. 点击"创建"保存

#### Grok (xAI) 配置示例

1. 点击"添加提供商"按钮
2. 填写配置信息:
   ```
   名称: Grok Production
   提供商类型: Grok (xAI)
   API密钥: xai-xxxxxxxxxxxxxxxxxxxxx
   基础URL: https://api.x.ai/v1 (或留空)
   模型: Grok 2 Latest
   ```
3. 点击"创建"保存

#### Google AI配置示例

1. 点击"添加提供商"按钮
2. 填写配置信息:
   ```
   名称: Gemini Production
   提供商类型: Google AI
   API密钥: AIzaSyxxxxxxxxxxxxxxxxxxxxx
   模型: Gemini 1.5 Pro
   ```
3. 点击"创建"保存

### 3. 测试连接

1. 在提供商列表中找到您添加的配置
2. 点击"测试"按钮(闪电图标⚡)
3. 在弹出的测试面板中:
   - 点击"测试"按钮进行连接测试
   - 查看连接状态和延迟时间

### 4. 聊天测试

1. 点击提供商的"测试"按钮
2. 在测试面板的"聊天测试"区域:
   - 在输入框中输入您的消息
   - 点击"发送"按钮
   - 查看AI的回复
   - 查看令牌使用量和响应延迟

### 5. 查看使用统计

在页面顶部的统计卡片中可以看到:
- **总请求数**: 所有提供商的累计请求次数
- **总令牌数**: 所有提供商的累计令牌使用量
- **活跃提供商**: 已启用的提供商数量

## 模型参数说明

### Temperature (温度)
- **范围**: 0.0 - 2.0
- **0.0**: 输出更确定、一致,适合事实性任务
- **1.0**: 平衡的创造性和确定性
- **2.0**: 输出更随机、创造性,适合创意写作

### Max Tokens (最大令牌数)
- 控制AI响应的最大长度
- 不同模型有不同的上限:
  - GPT-3.5: 4,096
  - GPT-4: 8,192
  - GPT-4 Turbo: 128,000
  - Gemini 1.5 Pro: 1,000,000

### Top P
- **范围**: 0.0 - 1.0
- 核采样参数,控制输出的多样性
- **1.0**: 考虑所有可能的令牌
- **0.9**: 只考虑累积概率为90%的令牌

### Frequency Penalty (频率惩罚)
- **范围**: -2.0 - 2.0
- 降低重复使用相同词语的倾向
- 正值减少重复,负值增加重复

### Presence Penalty (存在惩罚)
- **范围**: -2.0 - 2.0
- 增加讨论新话题的倾向
- 正值鼓励新话题,负值保持当前话题

## 获取API密钥

### OpenAI
1. 访问 https://platform.openai.com/api-keys
2. 登录您的OpenAI账户
3. 点击"Create new secret key"
4. 复制并保存密钥(仅显示一次)

### Grok (xAI)
1. 访问 https://console.x.ai/
2. 登录您的xAI账户
3. 在API Keys部分创建新密钥
4. 复制并保存密钥

### Google AI
1. 访问 https://makersuite.google.com/app/apikey
2. 登录Google账户
3. 点击"Create API Key"
4. 复制并保存密钥

## 最佳实践

### 1. 安全性
- ✅ API密钥会自动加密存储
- ✅ 不要在代码或日志中暴露API密钥
- ✅ 定期轮换API密钥
- ✅ 为不同环境使用不同的密钥

### 2. 性能优化
- 根据使用场景选择合适的模型
- 对于简单任务使用较小的模型(如GPT-3.5)
- 对于复杂任务使用较大的模型(如GPT-4)
- 合理设置max_tokens以控制成本

### 3. 成本控制
- 监控使用统计,及时发现异常使用
- 为不同用途创建不同的配置
- 使用temperature参数控制输出质量
- 考虑使用更经济的模型用于测试环境

### 4. 配置管理
- 为不同环境(开发/测试/生产)创建独立配置
- 使用描述字段记录配置用途
- 启用"设为默认"功能快速切换常用配置
- 定期测试配置确保可用性

## 故障排查

### 连接测试失败
1. 检查API密钥是否正确
2. 确认网络可以访问API端点
3. 检查API配额是否用尽
4. 验证基础URL是否正确

### 聊天失败
1. 确保提供商已启用
2. 检查max_tokens设置
3. 验证模型名称是否正确
4. 查看错误消息了解具体原因

### 使用统计不更新
- 统计数据仅在成功调用后更新
- 测试连接不计入使用统计
- 刷新页面查看最新数据

## API端点文档

如需在其他应用中使用AI管理API,请参考以下端点:

```
GET    /api/v1/admin/ai/providers       - 获取提供商列表
POST   /api/v1/admin/ai/providers       - 创建提供商
PUT    /api/v1/admin/ai/providers/{id}  - 更新提供商
DELETE /api/v1/admin/ai/providers/{id}  - 删除提供商
POST   /api/v1/admin/ai/providers/{id}/test - 测试连接
POST   /api/v1/admin/ai/chat             - 聊天完成
GET    /api/v1/admin/ai/models/{type}   - 获取可用模型
GET    /api/v1/admin/ai/usage            - 获取使用统计
```

完整API文档请访问: http://localhost:8000/api/docs

## 技术架构

### 后端
- FastAPI REST API
- SQLAlchemy ORM
- PostgreSQL数据库
- Redis缓存
- 异步处理

### 前端
- React 18 + TypeScript
- Ant Design UI
- TanStack Query (数据管理)
- react-markdown (Markdown渲染)

## 更新日志

### v1.0.0 (2025-10-13)
- ✨ 首次发布
- ✅ 支持OpenAI、Grok、Google AI
- ✅ 连接测试和聊天测试
- ✅ 使用统计追踪
- ✅ 多语言支持(中英文)

## 支持

如遇到问题或需要帮助,请:
1. 查看本文档的故障排查部分
2. 查看API文档获取技术细节
3. 检查浏览器控制台的错误信息
4. 查看后端日志获取详细错误

---

**祝您使用愉快! 🚀**
