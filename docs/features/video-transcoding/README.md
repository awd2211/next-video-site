# 视频转码和多分辨率系统

> **完整的视频转码解决方案** - 支持2K/4K高清、并行处理、边上传边转码、GPU加速

---

## 📋 概述

VideoSite的视频转码系统是一个企业级的视频处理解决方案,提供从上传到播放的完整工作流。

### 核心特性

- ✅ **多分辨率支持**: 360p → 480p → 720p → 1080p → 2K → 4K (6档)
- ✅ **并行转码**: 同时处理8-20个视频,无需排队
- ✅ **边上传边转码**: 上传完成立即开始转码,零延迟
- ✅ **GPU加速**: NVIDIA/Intel/AMD GPU支持,速度提升10倍
- ✅ **智能分辨率**: 根据源视频自动选择转码档位
- ✅ **H.265编码**: 节省50%带宽和存储成本
- ✅ **HLS流媒体**: 自适应码率,流畅播放
- ✅ **视频预览**: 鼠标悬停动态预览(类似YouTube/Netflix)

### 技术栈

| 组件 | 技术 | 用途 |
|------|------|------|
| 视频处理 | FFmpeg 4.4+ | 转码、切片、缩略图生成 |
| 任务队列 | Celery + Redis | 异步并发处理 |
| 对象存储 | MinIO (S3兼容) | 视频文件存储 |
| 数据库 | PostgreSQL | 任务状态追踪 |
| 流媒体 | HLS (HTTP Live Streaming) | 自适应码率播放 |
| 前端播放器 | Video.js | 支持4K + 清晰度切换 |

---

## 📚 文档导航

### 1. [系统架构](./architecture.md) ⭐
完整的系统架构设计,包括:
- 并行转码架构图
- 边上传边转码流程
- 数据流和时间线示例
- Celery任务队列配置

### 2. [GPU加速指南](./gpu-acceleration.md) 🚀
GPU硬件加速配置:
- NVIDIA NVENC (H.264/H.265)
- Intel Quick Sync Video
- AMD VCE
- 性能对比和基准测试

### 3. [边上传边转码](./upload-workflow.md) ⚡
管理员上传工作流集成:
- 上传完成钩子
- Celery任务触发
- 实时进度推送
- 管理后台UI集成

### 4. [视频悬停预览](./hover-preview.md) 🎬
鼠标hover动态预览功能:
- YouTube/Netflix风格预览
- 预览视频生成
- React组件实现
- 懒加载优化

### 5. [数据库设计](./database-schema.md) 💾
数据库表结构:
- `transcoding_tasks` 表(含15+新字段)
- `videos` 表扩展
- 索引和性能优化

### 6. [FFmpeg命令参考](./ffmpeg-commands.md) 🛠️
完整的FFmpeg命令示例:
- 2K/4K转码命令
- HLS切片生成
- 缩略图和预览生成
- GPU加速命令

### 7. [成本估算](./cost-estimation.md) 💰
资源和成本分析:
- 4K视频存储成本
- CPU vs GPU转码成本
- 带宽成本估算
- 推荐服务器配置

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装FFmpeg (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y ffmpeg

# 检查版本 (需要 >= 4.4)
ffmpeg -version

# 检查GPU支持 (NVIDIA)
ffmpeg -hwaccels | grep cuda

# 安装Python依赖
cd backend
pip install celery[redis] flower
```

### 2. 启动Celery Worker

```bash
# 开发环境 (单worker)
celery -A app.tasks.transcoding worker \
  --concurrency=8 \
  --loglevel=INFO

# 生产环境 (多worker + GPU)
celery -A app.tasks.transcoding multi start \
  worker1 worker2 worker3 \
  --concurrency=12 \
  --loglevel=INFO \
  -Q high_priority,normal,low_priority
```

### 3. 监控转码任务

```bash
# 启动Flower监控界面
celery -A app.tasks.transcoding flower --port=5555

# 访问: http://localhost:5555
```

### 4. 测试转码

```bash
# 通过管理后台上传视频
# URL: http://localhost:3001/videos/upload

# 或使用API测试
curl -X POST http://localhost:8000/api/v1/admin/upload/init-multipart \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "filename=test.mp4" \
  -F "file_size=1073741824" \
  -F "file_type=video/mp4"
```

---

## 📊 性能指标

### 转码速度 (1小时1080p视频)

| 方案 | 硬件 | 转码时间 | 并发数 | 成本 |
|------|------|---------|--------|------|
| CPU单核 | Intel i5 | ~2小时 | 1 | 低 |
| CPU 8核 | Intel i7 | ~30分钟 | 4 | 中 |
| GPU | NVIDIA RTX 3060 | ~10分钟 | 12 | 高 |
| GPU集群 | 3x RTX 3060 | ~3分钟 | 36 | 很高 |

### 存储需求 (1小时视频)

| 分辨率 | 编码 | 码率 | 文件大小 | 占比 |
|--------|------|------|----------|------|
| 4K | HEVC | 25Mbps | ~11GB | 44% |
| 2K | HEVC | 12Mbps | ~5.4GB | 22% |
| 1080p | H.264 | 5Mbps | ~2.2GB | 9% |
| 720p | H.264 | 2.5Mbps | ~1.1GB | 4% |
| 480p | H.264 | 1Mbps | ~450MB | 2% |
| 360p | H.264 | 600kbps | ~270MB | 1% |
| **总计** | - | - | **~25GB** | **100%** |

---

## 🔧 故障排除

### 常见问题

**Q: 转码任务一直pending不开始?**
```bash
# 检查Celery worker是否运行
celery -A app.tasks.transcoding inspect active

# 检查Redis连接
redis-cli ping

# 查看worker日志
tail -f /var/log/celery/worker1.log
```

**Q: FFmpeg报错 "codec not found"?**
```bash
# 检查编码器是否可用
ffmpeg -codecs | grep -E "h264|hevc"

# 重新编译FFmpeg with NVENC支持
# 参考: docs/guides/ffmpeg-installation.md
```

**Q: GPU加速不工作?**
```bash
# 检查NVIDIA驱动
nvidia-smi

# 检查FFmpeg GPU支持
ffmpeg -hwaccels

# 测试GPU编码
ffmpeg -hwaccel cuda -i test.mp4 -c:v h264_nvenc output.mp4
```

---

## 📖 相关文档

- [开发环境配置](../../guides/dev-setup.md)
- [快速开始指南](../../guides/quick-start.md)
- [测试指南](../../guides/testing.md)
- [项目总体架构](../../architecture/overview.md)

---

## 🤝 贡献

如果您发现文档错误或有改进建议,请:

1. 提交Issue: https://github.com/your-repo/issues
2. 创建Pull Request
3. 联系维护者

---

## 📝 更新日志

### v2.0.0 (2025-10-09)
- ✨ 新增2K和4K分辨率支持
- ✨ 新增并行转码能力 (8-20并发)
- ✨ 新增边上传边转码
- ✨ 新增GPU加速支持
- ✨ 新增视频悬停预览功能
- 🔧 优化H.265编码节省50%带宽

### v1.0.0 (2025-09-01)
- 🎉 初始版本
- 基础转码功能 (360p-1080p)
- HLS流媒体支持

---

**文档维护**: Claude AI + 开发团队
**最后更新**: 2025-10-09
**版本**: 2.0.0
