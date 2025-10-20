#!/usr/bin/env python3
"""
自动修复 Settings.tsx 中的硬编码文本
"""

import re
import json
from pathlib import Path

# 硬编码文本到翻译键的映射
TRANSLATION_MAP = {
    # 通用消息
    '保存失败': 'message.saveFailed',
    '所有设置已保存': 'message.allSettingsSaved',
    '请检查表单填写': 'message.checkForm',
    '已重置为默认值': 'settings.resetSuccess',
    '确定要重置所有设置为默认值吗？此操作不可恢复。': 'settings.actions.confirmReset',
    '测试邮件发送成功！请检查收件箱。': 'settings.email.testSuccess',
    '测试邮件发送失败': 'settings.email.testFailed',

    # 缓存相关
    '已清除缓存': 'settings.cache.cleared',
    '清除缓存失败': 'settings.cache.clearFailed',
    '获取缓存统计失败': 'settings.cache.statsFailed',
    '缓存统计': 'settings.cache.stats',

    # 备份相关
    '导出成功': 'settings.backup.exportSuccess',
    '导出失败': 'settings.backup.exportFailed',
    '导入成功': 'settings.backup.importSuccess',
    '导入失败': 'settings.backup.importFailed',
    '确认恢复备份？': 'settings.backup.confirmRestore',

    # 按钮和操作
    '保存所有': 'settings.actions.saveAll',
    '重置默认': 'settings.actions.reset',
    '测试连接': 'settings.actions.testConnection',
    '清除缓存': 'settings.actions.clearCache',
    '导出备份': 'settings.actions.exportBackup',
    '导入备份': 'settings.actions.importBackup',
    '发送测试邮件': 'settings.actions.sendTestEmail',

    # 标签和标题
    '网站信息': 'settings.tabs.siteInfo',
    '功能设置': 'settings.tabs.features',
    '邮件配置': 'settings.tabs.email',
    '缓存设置': 'settings.tabs.cache',
    '备份恢复': 'settings.tabs.backup',
    '高级设置': 'settings.tabs.advanced',

    # 表单字段
    '网站名称': 'settings.fields.siteName',
    '网站描述': 'settings.fields.siteDescription',
    '网站关键词': 'settings.fields.siteKeywords',
    '网站Logo': 'settings.fields.siteLogo',
    'ICP备案号': 'settings.fields.icp',
    '版权信息': 'settings.fields.copyright',

    # 邮件设置
    'SMTP服务器': 'settings.email.smtpServer',
    'SMTP端口': 'settings.email.smtpPort',
    '发件人邮箱': 'settings.email.senderEmail',
    '发件人名称': 'settings.email.senderName',
    'SMTP用户名': 'settings.email.username',
    'SMTP密码': 'settings.email.password',
    '启用SSL': 'settings.email.enableSSL',

    # 缓存设置
    'Redis地址': 'settings.cache.redisHost',
    'Redis端口': 'settings.cache.redisPort',
    'Redis密码': 'settings.cache.redisPassword',
    '缓存过期时间': 'settings.cache.ttl',

    # 功能开关
    '启用评论': 'settings.features.enableComments',
    '启用用户注册': 'settings.features.enableRegistration',
    '启用邮件通知': 'settings.features.enableEmailNotification',
    '启用搜索': 'settings.features.enableSearch',

    # 状态和提示
    '启用': 'common.enabled',
    '禁用': 'common.disabled',
    '保存中...': 'common.saving',
    '加载中...': 'common.loading',
    '搜索设置...': 'settings.searchPlaceholder',
}

def read_file(filepath):
    """读取文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    """写入文件"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def ensure_translation_import(content):
    """确保导入了useTranslation"""
    if 'useTranslation' in content:
        return content

    # 在import部分添加
    import_pattern = r"(import.*from 'react';)"
    replacement = r"\1\nimport { useTranslation } from 'react-i18next';"
    return re.sub(import_pattern, replacement, content)

def ensure_translation_hook(content):
    """确保初始化了useTranslation hook"""
    # 检查是否已经有 const { t } = useTranslation();
    if re.search(r'const\s+{\s*t\s*}\s*=\s*useTranslation\(\)', content):
        return content

    # 在函数组件开始处添加
    # 找到 const Settings = () => { 后面
    pattern = r'(const Settings = \(\) => {)'
    replacement = r'\1\n  const { t } = useTranslation();'
    return re.sub(pattern, replacement, content)

def replace_hardcoded_text(content):
    """替换硬编码文本"""
    replacements = 0

    # 按长度降序排序，优先替换长的字符串
    sorted_map = sorted(TRANSLATION_MAP.items(), key=lambda x: len(x[0]), reverse=True)

    for chinese_text, translation_key in sorted_map:
        # 匹配各种引号包裹的中文
        patterns = [
            (f"'{chinese_text}'", f"t('{translation_key}')"),
            (f'"{chinese_text}"', f"t('{translation_key}')"),
            (f'`{chinese_text}`', f"t('{translation_key}')"),
        ]

        for pattern, replacement in patterns:
            if pattern in content:
                content = content.replace(pattern, replacement)
                replacements += 1

    return content, replacements

def main():
    settings_file = Path('/home/eric/video/admin-frontend/src/pages/Settings.tsx')

    print("="*80)
    print("修复 Settings.tsx 硬编码文本")
    print("="*80)
    print()

    # 读取文件
    print("1. 读取文件...")
    content = read_file(settings_file)
    original_content = content

    # 确保导入useTranslation
    print("2. 检查 useTranslation 导入...")
    content = ensure_translation_import(content)

    # 确保初始化hook
    print("3. 检查 useTranslation hook...")
    content = ensure_translation_hook(content)

    # 替换硬编码文本
    print("4. 替换硬编码文本...")
    content, replacements = replace_hardcoded_text(content)

    # 写入文件
    if content != original_content:
        write_file(settings_file, content)
        print(f"\n✅ 修复完成！")
        print(f"📊 替换了 {replacements} 处硬编码文本")
        print(f"📄 文件: {settings_file}")
    else:
        print("\n⚠️  没有发现需要修复的内容")

    print("\n" + "="*80)
    print("下一步：检查翻译文件是否包含所有需要的键")

if __name__ == '__main__':
    main()
