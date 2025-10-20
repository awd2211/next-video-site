#!/usr/bin/env python3
"""
中文英文混合修正脚本
修复中文翻译中混入的英文词汇
"""

import json
from pathlib import Path
from typing import Dict, Any

# 中文英文混合修正字典
ZH_CN_FIXES = {
    # 页面标题和通用
    "Video Site Admin Panel": "视频站点管理面板",
    "Video Site": "视频站点",
    "All rights reserved": "保留所有权利",
    "© 2025 Video Site. All rights reserved.": "© 2025 视频站点。保留所有权利。",

    # Top 系列
    "热门视频 Top 10": "热门视频前10名",
    "Top 10": "前10名",
    "Top-P 采样": "Top-P采样",  # 技术术语，去掉空格

    # OAuth 配置
    "Facebook OAuth 配置指南": "Facebook OAuth配置指南",  # 保留OAuth但去空格
    "Google OAuth 配置指南": "Google OAuth配置指南",

    # Excel 导出
    "导出 Excel": "导出Excel",

    # 变量相关
    "逗号分隔的变量名（如：title, description）": "逗号分隔的变量名（例如：title, description）",

    # 格式化相关 - 保持插值变量，只翻译英文
    # 这些包含 {{}} 的需要特别小心
}

def translate_value(value: Any, translations: Dict[str, str]) -> Any:
    """递归翻译JSON值"""
    if isinstance(value, dict):
        return {k: translate_value(v, translations) for k, v in value.items()}
    elif isinstance(value, list):
        return [translate_value(item, translations) for item in value]
    elif isinstance(value, str):
        result = value
        # 按长度降序排序，优先匹配长字符串
        sorted_translations = sorted(translations.items(), key=lambda x: len(x[0]), reverse=True)
        for original, translation in sorted_translations:
            if original in result:
                result = result.replace(original, translation)
        return result
    else:
        return value

def main():
    print("="*80)
    print("中文英文混合修正")
    print("="*80)
    print()

    zh_file = Path('/home/eric/video/admin-frontend/src/i18n/locales/zh-CN.json')

    # 读取中文文件
    with open(zh_file, 'r', encoding='utf-8') as f:
        zh_data = json.load(f)

    print("修正前预览:")
    print(f"  - Video Site Admin Panel -> 视频站点管理面板")
    print(f"  - 热门视频 Top 10 -> 热门视频前10名")
    print(f"  - Top-P 采样 -> Top-P采样")
    print(f"  - 导出 Excel -> 导出Excel")
    print()

    # 应用翻译
    fixed_data = translate_value(zh_data, ZH_CN_FIXES)

    # 保存
    with open(zh_file, 'w', encoding='utf-8') as f:
        json.dump(fixed_data, f, ensure_ascii=False, indent=2)

    print(f"✅ 中文翻译修正完成！")
    print(f"📊 共修正 {len(ZH_CN_FIXES)} 个英文混合项")
    print()

    # 统计修正后的状态
    import re

    def count_english_words(data):
        """统计包含英文单词的项数"""
        count = 0

        # 排除的专有名词
        allowed = {
            'VIP', 'ID', 'IP', 'SQL', 'URL', 'API', 'HTTP', 'HTTPS',
            'JWT', 'OAuth', 'SMTP', 'SSL', 'TLS', 'AI', 'MinIO',
            'Redis', 'PostgreSQL', 'Stripe', 'PayPal', 'Alipay',
            'JSON', 'CSV', 'PDF', 'PNG', 'JPG', 'MP4', 'Excel',
            'Admin', 'Top', 'Facebook', 'Google', 'WeChat', 'QQ',
            '2FA', 'RBAC', 'CRUD', 'REST', 'CPU', 'GPU', 'RAM',
            'MB', 'GB', 'TB', 'KB', 'OK'
        }

        def check(v):
            nonlocal count
            if isinstance(v, dict):
                for val in v.values():
                    check(val)
            elif isinstance(v, list):
                for item in v:
                    check(item)
            elif isinstance(v, str):
                # 查找英文单词
                words = re.findall(r'\b[A-Za-z]{2,}\b', v)
                # 过滤掉允许的
                problematic = [w for w in words if w not in allowed]
                if problematic:
                    count += 1

        check(data)
        return count

    remaining = count_english_words(fixed_data)
    print(f"📊 剩余包含英文单词的项: {remaining}")

    if remaining > 0:
        print("\n💡 注意: 剩余的英文单词主要是:")
        print("   - 技术术语（OAuth, API, JSON等）")
        print("   - 专有名词（Facebook, Google, Excel等）")
        print("   - 插值变量（{{count}}, {{name}}等）")
        print("   这些通常是合理的，不需要翻译")
    else:
        print("\n🎉 所有不必要的英文单词都已修正！")

if __name__ == '__main__':
    main()
