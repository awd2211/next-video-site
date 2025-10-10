# GPU加速完整指南

> **硬件加速转码** - 速度提升10倍

## 📋 GPU方案对比

| GPU | 编码器 | H.264 | H.265 | 性能 | 成本 |
|-----|--------|-------|-------|------|------|
| NVIDIA | NVENC | ✅ | ✅ | ⭐⭐⭐⭐⭐ | 高 |
| Intel | QSV | ✅ | ✅ | ⭐⭐⭐⭐ | 低 |
| AMD | VCE | ✅ | ✅ | ⭐⭐⭐ | 中 |

## 🎯 推荐方案: NVIDIA NVENC

### 硬件要求
- GPU: RTX 3060 或更高 (12GB显存)
- 驱动: >= 470.x
- CUDA: >= 11.0

### 安装FFmpeg (支持NVENC)

```bash
# Ubuntu 22.04
sudo apt-add-repository ppa:jonathonf/ffmpeg-4
sudo apt update
sudo apt install ffmpeg nvidia-cuda-toolkit

# 验证NVENC支持
ffmpeg -hwaccels  # 应显示 cuda
ffmpeg -encoders | grep nvenc  # 应显示 h264_nvenc, hevc_nvenc
```

### FFmpeg命令示例

#### 4K H.265 GPU编码
```bash
ffmpeg -hwaccel cuda -hwaccel_output_format cuda \
  -i input.mp4 \
  -c:v hevc_nvenc \
  -preset p4 \  # p1(fastest) 到 p7(slowest)
  -rc vbr \  # 可变码率
  -cq 23 \  # 质量 (低=高质量)
  -b:v 25M \
  -maxrate 30M \
  -bufsize 50M \
  -vf "scale_cuda=3840:2160" \
  -c:a aac -b:a 256k \
  output_4k.mp4
```

#### 2K H.265 GPU编码
```bash
ffmpeg -hwaccel cuda \
  -i input.mp4 \
  -c:v hevc_nvenc \
  -preset p4 \
  -cq 21 \
  -b:v 12M \
  -vf "scale_cuda=2560:1440" \
  -c:a aac -b:a 192k \
  output_2k.mp4
```

#### 1080p H.264 GPU编码
```bash
ffmpeg -hwaccel cuda \
  -i input.mp4 \
  -c:v h264_nvenc \
  -preset p4 \
  -cq 23 \
  -b:v 5M \
  -vf "scale_cuda=1920:1080" \
  -c:a aac -b:a 192k \
  output_1080p.mp4
```

### Python集成

```python
def transcode_with_gpu(input_path, output_path, resolution):
    """GPU加速转码"""
    cmd = [
        'ffmpeg',
        '-hwaccel', 'cuda',
        '-hwaccel_output_format', 'cuda',
        '-i', str(input_path),
        '-c:v', 'hevc_nvenc' if resolution in ['4K', '2K'] else 'h264_nvenc',
        '-preset', 'p4',
        '-cq', '23',
        '-b:v', PROFILES[resolution]['bitrate'],
        '-vf', f"scale_cuda={PROFILES[resolution]['resolution']}",
        '-c:a', 'aac',
        '-b:a', PROFILES[resolution]['audio_bitrate'],
        '-y',
        str(output_path)
    ]
    
    subprocess.run(cmd, check=True)
```

## 📊 性能对比

| 视频时长 | CPU (i7-9700K) | GPU (RTX 3060) | 提升 |
|---------|----------------|----------------|------|
| 10分钟 | 20分钟 | 2分钟 | 10x |
| 1小时 | 120分钟 | 10分钟 | 12x |
| 2小时 | 240分钟 | 20分钟 | 12x |

## 🔧 故障排查

### NVENC not found
```bash
# 检查GPU
nvidia-smi

# 检查CUDA
nvcc --version

# 重新编译FFmpeg with NVENC
# 参考: https://docs.nvidia.com/video-technologies/video-codec-sdk/ffmpeg-with-nvidia-gpu/
```

### 显存不足
```bash
# 降低并发数
CELERY_WORKER_CONCURRENCY = 4  # 从12降低到4

# 或使用更大显存的GPU (RTX 3090 24GB)
```

**文档版本**: 1.0.0
