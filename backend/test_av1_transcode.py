"""
测试AV1转码功能

这个脚本用于验证:
1. AV1Transcoder类功能
2. SVT-AV1编码器配置
3. HLS切片生成
4. 文件大小对比
"""
import sys
from pathlib import Path
import tempfile
import shutil

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.av1_transcoder import AV1Transcoder, format_size


def create_test_video(output_path: Path, duration: int = 10):
    """
    创建测试视频 (使用FFmpeg生成)

    Args:
        output_path: 输出路径
        duration: 时长(秒)
    """
    import subprocess

    print(f"📹 生成{duration}秒测试视频...")

    cmd = [
        'ffmpeg', '-y',
        '-f', 'lavfi',
        '-i', f'testsrc=duration={duration}:size=1280x720:rate=30',
        '-f', 'lavfi',
        '-i', f'sine=frequency=1000:duration={duration}',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '128k',
        str(output_path)
    ]

    subprocess.run(cmd, check=True, capture_output=True)
    print(f"✅ 测试视频已生成: {output_path}")
    print(f"   文件大小: {format_size(output_path.stat().st_size)}")


def test_video_info():
    """测试视频元数据提取"""
    print("\n" + "="*60)
    print("测试 1: 视频元数据提取")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_video = tmpdir / 'test.mp4'

        # 创建测试视频
        create_test_video(test_video, duration=5)

        # 提取元数据
        print("\n📊 提取视频元数据...")
        info = AV1Transcoder.get_video_info(test_video)

        print(f"  分辨率: {info['width']}x{info['height']}")
        print(f"  时长: {info['duration']:.2f}秒")
        print(f"  编解码器: {info['codec']}")
        print(f"  比特率: {info['bitrate']} kbps")

        print("✅ 元数据提取测试通过")


def test_av1_transcoding():
    """测试AV1转码"""
    print("\n" + "="*60)
    print("测试 2: AV1转码 (480p HLS)")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        test_video = tmpdir / 'test.mp4'
        output_dir = tmpdir / 'av1_output'
        output_dir.mkdir()

        # 创建测试视频
        create_test_video(test_video, duration=10)
        original_size = test_video.stat().st_size

        # 转码为AV1 HLS (480p, 小分辨率快速测试)
        print("\n🔄 开始AV1转码 (480p)...")
        print("   编码器: SVT-AV1")
        print("   格式: HLS (6秒切片)")

        try:
            m3u8_path = AV1Transcoder.transcode_to_hls_av1(
                test_video,
                output_dir,
                resolution='480p',
                segment_time=6
            )

            print(f"✅ 转码完成: {m3u8_path}")

            # 检查输出文件
            files = list(output_dir.glob('*'))
            print(f"\n📁 生成的文件 ({len(files)}个):")

            m3u8_files = [f for f in files if f.suffix == '.m3u8']
            ts_files = [f for f in files if f.suffix == '.ts']

            print(f"  - M3U8 playlist: {len(m3u8_files)}个")
            print(f"  - TS segments: {len(ts_files)}个")

            if m3u8_files:
                print(f"\n📄 Playlist内容预览:")
                print("-" * 50)
                content = m3u8_files[0].read_text()
                for i, line in enumerate(content.split('\n')[:10]):
                    print(f"  {line}")
                if len(content.split('\n')) > 10:
                    print("  ...")

            # 计算文件大小
            total_size = sum(f.stat().st_size for f in files)

            print(f"\n📊 文件大小对比:")
            print(f"  原始视频 (H.264): {format_size(original_size)}")
            print(f"  转码后 (AV1):    {format_size(total_size)}")

            if total_size < original_size:
                savings = ((original_size - total_size) / original_size) * 100
                print(f"  节省空间:        {format_size(original_size - total_size)} ({savings:.1f}%)")

            print("\n✅ AV1转码测试通过")

        except Exception as e:
            print(f"❌ 转码失败: {str(e)}")
            raise


def test_master_playlist():
    """测试Master Playlist生成"""
    print("\n" + "="*60)
    print("测试 3: Master Playlist生成")
    print("="*60)

    # 模拟多分辨率HLS URL
    hls_urls = {
        '1080p': 'videos/123/av1/1080p/index.m3u8',
        '720p': 'videos/123/av1/720p/index.m3u8',
        '480p': 'videos/123/av1/480p/index.m3u8',
    }

    print("\n🔄 生成Master Playlist...")
    master_content = AV1Transcoder.create_master_playlist(
        video_id=123,
        resolutions=hls_urls,
        format_type='av1'
    )

    print(f"\n📄 Master Playlist内容:")
    print("-" * 50)
    print(master_content)
    print("-" * 50)

    # 验证内容
    assert '#EXTM3U' in master_content
    assert '1080p' in master_content
    assert '720p' in master_content
    assert '480p' in master_content

    print("✅ Master Playlist生成测试通过")


def test_file_comparison():
    """测试文件大小对比"""
    print("\n" + "="*60)
    print("测试 4: 文件大小对比工具")
    print("="*60)

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # 创建两个测试文件
        h264_file = tmpdir / 'h264.mp4'
        av1_file = tmpdir / 'av1.mp4'

        h264_file.write_bytes(b'x' * 2_250_000_000)  # 2.25GB (模拟H.264)
        av1_file.write_bytes(b'x' * 990_000_000)     # 990MB (模拟AV1)

        print("\n📊 对比文件大小...")
        comparison = AV1Transcoder.compare_file_sizes(h264_file, av1_file)

        print(f"  H.264文件: {format_size(comparison['h264_size'])}")
        print(f"  AV1文件:   {format_size(comparison['av1_size'])}")
        print(f"  节省:      {format_size(comparison['savings_bytes'])} ({comparison['savings_percent']:.1f}%)")

        # 验证计算
        assert comparison['savings_percent'] > 50
        assert comparison['savings_percent'] < 60

        print("✅ 文件大小对比测试通过")


def main():
    """运行所有测试"""
    print("\n" + "🎬" * 30)
    print("AV1转码功能测试套件")
    print("🎬" * 30)

    tests = [
        ("视频元数据提取", test_video_info),
        ("AV1转码", test_av1_transcoding),
        ("Master Playlist生成", test_master_playlist),
        ("文件大小对比", test_file_comparison),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ 测试失败: {name}")
            print(f"   错误: {str(e)}")
            failed += 1
            import traceback
            traceback.print_exc()

    # 总结
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    print(f"✅ 通过: {passed}/{len(tests)}")
    print(f"❌ 失败: {failed}/{len(tests)}")

    if failed == 0:
        print("\n🎉 所有测试通过! AV1转码系统已准备就绪")
        return 0
    else:
        print(f"\n⚠️  {failed}个测试失败,请检查错误信息")
        return 1


if __name__ == '__main__':
    sys.exit(main())
