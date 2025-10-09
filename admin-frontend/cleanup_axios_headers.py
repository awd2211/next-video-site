#!/usr/bin/env python3
"""
清理所有 .tsx 和 .ts 文件中不必要的 token 获取和 headers 传递
因为我们已经在 axios 拦截器中自动添加了 token
"""

import re
import os
from pathlib import Path

def cleanup_file(filepath):
    """清理单个文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. 移除 const token = localStorage.getItem('admin_access_token')
    content = re.sub(
        r'\s*const token = localStorage\.getItem\([\'"]admin_access_token[\'"]\)\s*\n',
        '',
        content
    )

    # 2. 移除 axios 请求中的 headers 参数
    # 匹配模式: axios.get('/api/...', {\n      headers: { Authorization: `Bearer ${token}` },\n    })
    # 替换为: axios.get('/api/...')

    # Pattern 1: 带headers的请求 (GET/DELETE)
    content = re.sub(
        r'(axios\.(get|delete)\([^,]+),\s*\{\s*headers:\s*\{\s*Authorization:\s*`Bearer\s*\$\{token\}`\s*\},?\s*\}',
        r'\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )

    # Pattern 2: POST/PUT/PATCH请求,可能有data参数
    # 先处理只有headers的情况
    content = re.sub(
        r'(axios\.(post|put|patch)\([^,]+,\s*[^,]+),\s*\{\s*headers:\s*\{\s*Authorization:\s*`Bearer\s*\$\{token\}`\s*\},?\s*\}',
        r'\1',
        content,
        flags=re.MULTILINE | re.DOTALL
    )

    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

def main():
    """主函数"""
    src_dir = Path('src')
    changed_files = []

    # 遍历所有 .tsx 和 .ts 文件
    for ext in ['*.tsx', '*.ts']:
        for filepath in src_dir.rglob(ext):
            # 跳过 node_modules
            if 'node_modules' in str(filepath):
                continue

            # 跳过 axios.ts 本身
            if filepath.name == 'axios.ts':
                continue

            try:
                if cleanup_file(filepath):
                    changed_files.append(filepath)
                    print(f'✓ 清理: {filepath}')
            except Exception as e:
                print(f'✗ 错误 {filepath}: {e}')

    print(f'\n完成! 共清理 {len(changed_files)} 个文件')

if __name__ == '__main__':
    main()
