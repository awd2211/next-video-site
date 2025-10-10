# VideoSite 技术文档

> **完整的技术文档索引** - 快速找到您需要的文档

---

## 📚 文档导航

### 🎬 核心功能

#### [视频转码系统](./features/video-transcoding/) ⭐ 重点推荐
完整的视频转码解决方案,支持2K/4K高清、并行转码、GPU加速
- [系统总览](./features/video-transcoding/README.md)
- [视频悬停预览](./features/video-transcoding/hover-preview.md) - 🆕 YouTube/Netflix风格预览

#### [推荐系统](./features/RECOMMENDATION_SYSTEM.md)
智能视频推荐算法 (协同过滤 + 内容过滤)

#### [搜索增强](./features/SEARCH_ENHANCEMENT.md)
5维度高级搜索和过滤功能

#### [验证码系统](./features/captcha-system.md)
滑动验证码防bot方案

#### [邮件系统](./features/email-system.md)
SMTP邮件发送和模板管理

#### [字幕管理系统](./features/subtitle-management.md) 🆕
多语言字幕支持 (SRT/VTT/ASS)、AI自动生成、在线编辑

#### [视频加密系统](./features/video-encryption.md) 🆕
HLS AES-128加密防盗链 + 完整安全方案

#### [企业级DRM](./features/drm-integration.md) 🆕
Widevine/PlayReady/FairPlay多DRM集成指南

#### [开源视频解码方案对比](./features/video-decoder-comparison.md) 🆕
FFmpeg/dav1d/libvpx/WebCodecs等主流解码方案全面对比

---

### 🛠️ 开发指南

- [开发环境配置](./guides/dev-setup.md) - 快速搭建开发环境
- [快速开始](./guides/quick-start.md) - 5分钟运行项目
- [测试指南](./guides/testing.md) - 单元测试和集成测试

---

### 📊 项目状态

- [开发进度](./status/progress.md) - 当前95%完成度
- [已完成任务](./status/completed-tasks.md) - 功能清单
- [平台状态](./status/platform-status.md) - 系统运行状态
- [开发状态](./status/development-status.md) - 详细状态报告

---

## 🔥 快速链接

| 我想... | 查看文档 |
|---------|----------|
| 了解视频转码如何工作 | [视频转码系统](./features/video-transcoding/) |
| 实现视频hover预览 | [视频悬停预览](./features/video-transcoding/hover-preview.md) |
| 配置GPU加速 | [GPU加速指南](./features/video-transcoding/gpu-acceleration.md) |
| 添加视频字幕 | [字幕管理系统](./features/subtitle-management.md) 🆕 |
| 加密保护视频 | [视频加密系统](./features/video-encryption.md) 🆕 |
| 集成DRM保护 | [企业级DRM](./features/drm-integration.md) 🆕 |
| 选择解码方案 | [开源解码方案对比](./features/video-decoder-comparison.md) 🆕 |
| 搭建开发环境 | [开发环境配置](./guides/dev-setup.md) |
| 运行项目 | [快速开始](./guides/quick-start.md) |
| 查看进度 | [开发进度](./status/progress.md) |

---

## 📖 文档结构

```
docs/
├── README.md                    # 本文档(主索引)
│
├── features/                    # 功能设计文档
│   ├── video-transcoding/       # 视频转码系统(完整)
│   │   ├── README.md            # 转码系统总览 ✅
│   │   ├── hover-preview.md     # 视频悬停预览 ✅
│   │   ├── architecture.md      # 系统架构 ✅
│   │   ├── gpu-acceleration.md  # GPU加速 ✅
│   │   ├── upload-workflow.md   # 边上传边转码 ✅
│   │   └── database-schema.md   # 数据库设计 ✅
│   │
│   ├── subtitle-management.md   # 字幕管理系统 ✅ 🆕
│   ├── video-encryption.md      # 视频加密系统 ✅ 🆕
│   ├── drm-integration.md       # 企业级DRM ✅ 🆕
│   ├── video-decoder-comparison.md  # 开源解码方案对比 ✅ 🆕
│   │
│   ├── RECOMMENDATION_SYSTEM.md # 推荐系统
│   ├── SEARCH_ENHANCEMENT.md    # 搜索增强
│   ├── captcha-system.md        # 验证码系统
│   └── email-system.md          # 邮件系统
│
├── guides/                      # 开发指南
│   ├── dev-setup.md             # 开发环境配置
│   ├── quick-start.md           # 快速开始
│   └── testing.md               # 测试指南
│
├── architecture/                # 架构文档(待创建)
│   ├── overview.md              # 系统总体架构
│   ├── backend.md               # 后端架构
│   ├── frontend.md              # 前端架构
│   └── infrastructure.md        # 基础设施
│
└── status/                      # 项目状态报告
    ├── progress.md              # 开发进度
    ├── completed-tasks.md       # 已完成任务
    ├── platform-status.md       # 平台状态
    └── development-status.md    # 开发状态
```

---

## ⚡ 新增特性 (最近更新)

### 2025-10-10

🔐 **视频安全与解码系统文档** (🆕 今日新增)
- [字幕管理系统](./features/subtitle-management.md) - 多语言字幕、AI生成、在线编辑
- [视频加密系统](./features/video-encryption.md) - HLS AES-128加密防盗链完整方案
- [企业级DRM](./features/drm-integration.md) - Widevine/PlayReady/FairPlay集成指南
- [开源解码方案对比](./features/video-decoder-comparison.md) - FFmpeg/Google/VideoLAN等主流方案全面对比

### 2025-10-09

✨ **视频转码系统文档**
- [视频悬停预览](./features/video-transcoding/hover-preview.md) - YouTube/Netflix风格预览
- [系统架构](./features/video-transcoding/architecture.md) - 完整并行转码架构
- [GPU加速](./features/video-transcoding/gpu-acceleration.md) - NVIDIA NVENC硬件加速
- [上传工作流](./features/video-transcoding/upload-workflow.md) - 边上传边转码
- [数据库设计](./features/video-transcoding/database-schema.md) - 完整Schema

✨ **文档重组**
- 创建专业docs目录结构
- 按功能/指南/状态分类
- 改善文档可维护性

---

## 🤝 贡献指南

### 添加新文档

1. 选择合适的目录 (`features/`, `guides/`, `architecture/`, `status/`)
2. 创建Markdown文档
3. 更新本README索引
4. 提交Pull Request

### 文档规范

- 使用Markdown格式
- 添加目录导航
- 包含代码示例
- 注明最后更新日期

---

## 📞 联系方式

- **项目仓库**: https://github.com/your-repo/videosite
- **问题反馈**: https://github.com/your-repo/videosite/issues
- **维护团队**: Claude AI + 开发团队

---

**最后更新**: 2025-10-10
**文档版本**: 2.1.0
**平台完成度**: 95%
