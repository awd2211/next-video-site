#!/usr/bin/env python3
"""
自动化i18n修复工具
自动将硬编码中文替换为t()调用
"""

import re
import json
from pathlib import Path
from typing import Dict, Set, Tuple
import hashlib

class I18nFixer:
    def __init__(self, locales_dir: str):
        self.locales_dir = Path(locales_dir)
        self.translations = {}
        self.load_translations()

    def load_translations(self):
        """加载所有语言的翻译文件"""
        for lang_file in self.locales_dir.glob('*.json'):
            lang_code = lang_file.stem
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations[lang_code] = json.load(f)

    def save_translations(self):
        """保存所有语言的翻译文件"""
        for lang_code, data in self.translations.items():
            lang_file = self.locales_dir / f'{lang_code}.json'
            with open(lang_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    def generate_key_name(self, text: str, context: str = 'common') -> str:
        """根据文本内容生成翻译键名"""
        # 移除特殊字符
        clean_text = re.sub(r'[^\w\u4e00-\u9fff]', '', text)

        # 根据内容推断上下文
        if any(word in text for word in ['成功', '失败', '错误', '警告']):
            context = 'message'
        elif any(word in text for word in ['确认', '取消', '删除', '保存', '编辑']):
            context = 'common'
        elif any(word in text for word in ['设置', '配置']):
            context = 'settings'

        # 生成简短的键名
        if len(clean_text) <= 6:
            key_name = clean_text
        else:
            # 使用hash生成唯一键
            hash_suffix = hashlib.md5(text.encode()).hexdigest()[:6]
            key_name = f"{clean_text[:6]}_{hash_suffix}"

        return f"{context}.{key_name}"

    def find_or_create_key(self, text: str) -> str:
        """查找或创建翻译键"""
        # 先在中文翻译中查找是否已存在
        zh_cn = self.translations.get('zh-CN', {})

        def search_in_dict(d, prefix=''):
            for k, v in d.items():
                current_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, dict):
                    result = search_in_dict(v, current_key)
                    if result:
                        return result
                elif v == text:
                    return current_key
            return None

        existing_key = search_in_dict(zh_cn)
        if existing_key:
            return existing_key

        # 不存在则创建新键
        new_key = self.generate_key_name(text)

        # 添加到所有语言（暂时只添加中文，其他语言需要翻译）
        parts = new_key.split('.')
        for lang_code in self.translations:
            current = self.translations[lang_code]
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            # 只有中文使用实际文本，其他语言标记为TODO
            if lang_code == 'zh-CN':
                current[parts[-1]] = text
            else:
                current[parts[-1]] = f"TODO: {text}"

        return new_key

    def extract_hardcoded_chinese(self, content: str) -> Set[str]:
        """提取所有硬编码的中文字符串"""
        patterns = [
            r'"([^"]*[\u4e00-\u9fff][^"]*)"',
            r"'([^']*[\u4e00-\u9fff][^']*)'",
            r'`([^`]*[\u4e00-\u9fff][^`]*)`',
        ]

        chinese_texts = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                # 排除已经使用t()的
                if not (f"t('{match}')" in content or f't("{match}")' in content):
                    chinese_texts.add(match)

        return chinese_texts

    def fix_file(self, filepath: str) -> Tuple[int, int]:
        """修复单个文件"""
        filepath = Path(filepath)

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # 1. 确保导入useTranslation
        if 'useTranslation' not in content:
            # 查找react导入行
            import_match = re.search(r"(import.*from ['`\"]react['`\"];)", content)
            if import_match:
                content = content.replace(
                    import_match.group(1),
                    import_match.group(1) + "\nimport { useTranslation } from 'react-i18next';"
                )

        # 2. 确保初始化hook（查找组件定义）
        if not re.search(r'const\s+{\s*t\s*}\s*=\s*useTranslation\(\)', content):
            # 查找函数组件定义
            component_patterns = [
                r'(const\s+\w+\s*=\s*\(\)\s*=>\s*{)',
                r'(function\s+\w+\s*\(\)\s*{)',
                r'(export\s+default\s+function\s+\w+\s*\(\)\s*{)',
            ]
            for pattern in component_patterns:
                match = re.search(pattern, content)
                if match:
                    content = content.replace(
                        match.group(1),
                        match.group(1) + '\n  const { t } = useTranslation();'
                    )
                    break

        # 3. 提取并替换硬编码中文
        chinese_texts = self.extract_hardcoded_chinese(content)
        replacements = 0

        for text in sorted(chinese_texts, key=len, reverse=True):
            # 获取或创建翻译键
            key = self.find_or_create_key(text)

            # 替换所有出现的地方
            old_patterns = [
                f'"{text}"',
                f"'{text}'",
                f'`{text}`',
            ]

            for old in old_patterns:
                if old in content:
                    content = content.replace(old, f"t('{key}')")
                    replacements += 1

        # 4. 保存文件
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return len(chinese_texts), replacements

        return 0, 0

def main():
    print("="*80)
    print("自动化 i18n 修复工具")
    print("="*80)
    print()

    # 初始化
    fixer = I18nFixer('/home/eric/video/admin-frontend/src/i18n/locales')

    # 要修复的文件列表（优先级顺序）
    files_to_fix = [
        '/home/eric/video/admin-frontend/src/pages/Settings.tsx',
        # 可以添加更多文件
    ]

    total_texts = 0
    total_replacements = 0

    for filepath in files_to_fix:
        print(f"修复文件: {Path(filepath).name}")
        print("-" * 80)

        texts, replacements = fixer.fix_file(filepath)
        total_texts += texts
        total_replacements += replacements

        print(f"  发现硬编码: {texts} 个")
        print(f"  执行替换: {replacements} 次")
        print()

    # 保存翻译文件
    print("保存翻译文件...")
    fixer.save_translations()

    print("="*80)
    print(f"修复完成!")
    print(f"  总硬编码数: {total_texts}")
    print(f"  总替换次数: {total_replacements}")
    print(f"  修复文件数: {len(files_to_fix)}")
    print("="*80)
    print()
    print("⚠️  注意:")
    print("  1. 非中文语言的翻译标记为 'TODO: xxx'")
    print("  2. 需要人工翻译或使用翻译API")
    print("  3. 建议检查生成的代码和翻译键")

if __name__ == '__main__':
    main()
