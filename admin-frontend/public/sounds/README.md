# 通知声音文件

这个目录用于存放管理后台的通知声音文件。

## 需要的文件

1. **notification.mp3** - 普通信息通知音效
2. **warning.mp3** - 警告通知音效
3. **error.mp3** - 错误通知音效
4. **critical.mp3** - 严重错误通知音效

## 音效要求

- 格式：MP3
- 时长：0.5-2 秒
- 音量：适中（代码中会自动调整）
- 文件大小：尽量小于 50KB

## 获取音效

可以从以下网站免费下载：

1. **Freesound** - https://freesound.org/
   - 搜索 "notification", "alert", "beep" 等关键词
   - 选择 CC0 或 CC-BY 授权的音效

2. **Mixkit** - https://mixkit.co/free-sound-effects/notification/
   - 提供免费商用音效
   - 无需注册即可下载

3. **Zapsplat** - https://www.zapsplat.com/
   - 注册后可免费下载
   - 音效质量较高

4. **Pixabay** - https://pixabay.com/sound-effects/
   - 免费商用音效
   - 无需注册

## 临时解决方案

如果暂时没有音效文件，可以创建静音文件作为占位符：

```bash
# 创建 1 秒的静音 MP3 文件（需要 ffmpeg）
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -acodec libmp3lame notification.mp3
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -acodec libmp3lame warning.mp3
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -acodec libmp3lame error.mp3
ffmpeg -f lavfi -i anullsrc=r=44100:cl=mono -t 1 -acodec libmp3lame critical.mp3
```

或者使用代码禁用声音功能直到音效文件准备好。

## 使用说明

音效会在以下情况自动播放：

- **notification.mp3** - 普通信息通知（info 级别）
- **warning.mp3** - 警告通知（warning 级别）
- **error.mp3** - 错误通知（error 级别）
- **critical.mp3** - 严重错误通知（critical 级别）

音量会根据严重程度自动调整：
- info: 0.5
- warning: 0.5
- error: 0.7
- critical: 0.8
