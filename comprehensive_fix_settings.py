#!/usr/bin/env python3
"""
Comprehensive fix for Settings.tsx hardcoded text
Generates proper English translation keys and handles JSX syntax correctly
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Comprehensive translation mapping for Settings.tsx
# Format: Chinese text -> English translation key
COMPREHENSIVE_MAP = {
    # Messages already in TRANSLATION_MAP (from fix_hardcoded_settings.py)
    '保存失败': 'message.saveFailed',
    '所有设置已保存': 'message.allSettingsSaved',
    '请检查表单填写': 'message.checkForm',
    '已重置为默认值': 'settings.resetSuccess',
    '确定要重置所有设置为默认值吗？此操作不可恢复。': 'settings.actions.confirmReset',
    '测试邮件发送成功！请检查收件箱。': 'settings.email.testSuccess',
    '测试邮件发送失败': 'settings.email.testFailed',
    '已清除缓存': 'settings.cache.cleared',
    '清除缓存失败': 'settings.cache.clearFailed',
    '获取缓存统计失败': 'settings.cache.statsFailed',

    # Additional messages found in Settings.tsx
    '所有缓存已清除': 'settings.cache.allCleared',
    '备份文件已下载': 'settings.backup.downloaded',
    '导出备份失败': 'settings.backup.exportFailed',
    '设置恢复成功': 'settings.backup.restoreSuccess',
    '恢复设置失败': 'settings.backup.restoreFailed',
    '备份文件格式错误': 'settings.backup.invalidFormat',

    # Modal and confirmation dialogs
    '确认恢复设置？': 'settings.backup.confirmRestoreTitle',
    '此操作将覆盖当前设置，是否继续？': 'settings.backup.confirmRestoreContent',
    '邮箱地址': 'settings.email.address',
    '输入测试邮箱地址': 'settings.email.enterTestAddress',

    # Section headers
    '🌐 网站与 SEO': 'settings.sections.siteAndSeo',
    '📹 视频与上传': 'settings.sections.videoAndUpload',
    '💬 用户与社区': 'settings.sections.userAndCommunity',
    '📧 邮件服务': 'settings.sections.emailService',
    '🔒 安全配置': 'settings.sections.security',
    '🔔 通知设置': 'settings.sections.notifications',
    '🗄️ 缓存管理': 'settings.sections.cacheManagement',
    '💾 备份与恢复': 'settings.sections.backupAndRestore',
    '💳 支付网关配置': 'settings.sections.paymentGateway',
    '⚙️ 其他设置': 'settings.sections.otherSettings',

    # Section descriptions
    '配置网站基本信息和搜索引擎优化设置': 'settings.descriptions.siteAndSeo',
    '配置视频审核、清晰度、转码和上传限制': 'settings.descriptions.videoAndUpload',
    '配置用户注册、验证和评论功能': 'settings.descriptions.userAndCommunity',
    '配置 SMTP 或 Mailgun 邮件服务': 'settings.descriptions.emailService',
    '配置登录安全、验证码、会话超时等': 'settings.descriptions.security',
    '配置通知方式、声音、桌面通知和免打扰时段': 'settings.descriptions.notifications',
    '管理Redis缓存并查看统计信息': 'settings.descriptions.cacheManagement',
    '导出和导入系统设置': 'settings.descriptions.backupAndRestore',
    '配置 Stripe、PayPal、支付宝等支付网关': 'settings.descriptions.paymentGateway',
    '维护模式、统计代码、自定义样式等': 'settings.descriptions.otherSettings',

    # Form labels
    '网站简介': 'settings.placeholders.siteIntro',
    '关键词': 'settings.labels.keywords',
    '视频,在线观看,电影': 'settings.placeholders.keywordsExample',
    '覆盖默认标题': 'settings.placeholders.overrideDefaultTitle',
    '搜索引擎描述': 'settings.placeholders.seDescription',
    '关键词1,关键词2,关键词3': 'settings.placeholders.keywordsComma',

    # Video settings
    '需要人工审核': 'settings.labels.requireManualReview',
    '开启后新上传的视频自动通过审核': 'settings.tooltips.autoApproveUploads',
    '默认清晰度': 'settings.labels.defaultQuality',
    '启用转码': 'settings.labels.enableTranscoding',
    '转码格式': 'settings.labels.transcodeFormats',
    '选择需要转码的格式': 'settings.placeholders.selectTranscodeFormats',
    '视频最大大小 (MB)': 'settings.labels.maxVideoSize',
    '图片最大大小 (MB)': 'settings.labels.maxImageSize',
    '允许的视频格式': 'settings.labels.allowedVideoFormats',
    '输入格式后按回车': 'settings.placeholders.enterFormatAndEnter',
    '允许的图片格式': 'settings.labels.allowedImageFormats',

    # User settings
    '需要邮箱验证': 'settings.labels.requireEmailVerification',
    '默认头像 URL': 'settings.labels.defaultAvatarUrl',
    '最大收藏数': 'settings.labels.maxFavorites',
    '启用评论功能': 'settings.labels.enableComments',
    '评论需要审核': 'settings.labels.commentsRequireReview',
    '开启后评论需要管理员审核才能显示': 'settings.tooltips.commentsModeration',
    '允许游客评论': 'settings.labels.allowGuestComments',
    '评论最大长度': 'settings.labels.maxCommentLength',
    '字符': 'settings.units.characters',

    # Email settings
    '发送测试邮件以验证 SMTP 配置是否正确': 'settings.descriptions.sendTestEmail',
    '最后测试: ': 'settings.labels.lastTest',

    # Security settings
    '开启后登录时需要输入验证码': 'settings.tooltips.enableCaptcha',
    '登录最大尝试次数': 'settings.labels.maxLoginAttempts',
    '锁定时长 (分钟)': 'settings.labels.lockoutDuration',
    '会话超时 (秒)': 'settings.labels.sessionTimeout',
    '秒': 'settings.units.seconds',

    # Cache management
    '查看缓存命中率和性能指标': 'settings.descriptions.viewCacheStats',
    '总命中数': 'settings.labels.totalHits',
    '总未命中数': 'settings.labels.totalMisses',
    '平均命中率': 'settings.labels.avgHitRate',
    '命中': 'settings.labels.hits',
    '未命中': 'settings.labels.misses',
    '命中率': 'settings.labels.hitRate',

    # Maintenance
    '开启后前台将显示维护页面': 'settings.tooltips.maintenanceMode',
    '维护提示信息': 'settings.labels.maintenanceMessage',
    '网站正在维护中，请稍后访问': 'settings.placeholders.maintenanceMessage',
    '统计代码 (Google Analytics 等)': 'settings.labels.analyticsCode',
    '自定义 CSS': 'settings.labels.customCss',
    '自定义 JavaScript': 'settings.labels.customJs',

    # Status labels
    '已保存': 'common.saved',

    # Template strings with variables
    '已清除 ${response.data.cleared_keys} 个缓存键': 'settings.cache.clearedCount',
}

# English translations
EN_TRANSLATIONS = {
    'message.saveFailed': 'Save failed',
    'message.allSettingsSaved': 'All settings saved',
    'message.checkForm': 'Please check form fields',
    'settings.resetSuccess': 'Reset to default values',
    'settings.actions.confirmReset': 'Are you sure you want to reset all settings to default? This cannot be undone.',
    'settings.email.testSuccess': 'Test email sent successfully! Please check your inbox.',
    'settings.email.testFailed': 'Test email failed',
    'settings.cache.cleared': 'Cache cleared',
    'settings.cache.clearFailed': 'Failed to clear cache',
    'settings.cache.statsFailed': 'Failed to get cache statistics',
    'settings.cache.allCleared': 'All cache cleared',
    'settings.backup.downloaded': 'Backup file downloaded',
    'settings.backup.exportFailed': 'Export backup failed',
    'settings.backup.restoreSuccess': 'Settings restored successfully',
    'settings.backup.restoreFailed': 'Failed to restore settings',
    'settings.backup.invalidFormat': 'Invalid backup file format',
    'settings.backup.confirmRestoreTitle': 'Confirm restore settings?',
    'settings.backup.confirmRestoreContent': 'This will overwrite current settings. Continue?',
    'settings.email.address': 'Email Address',
    'settings.email.enterTestAddress': 'Enter test email address',

    'settings.sections.siteAndSeo': '🌐 Site & SEO',
    'settings.sections.videoAndUpload': '📹 Video & Upload',
    'settings.sections.userAndCommunity': '💬 User & Community',
    'settings.sections.emailService': '📧 Email Service',
    'settings.sections.security': '🔒 Security',
    'settings.sections.notifications': '🔔 Notifications',
    'settings.sections.cacheManagement': '🗄️ Cache Management',
    'settings.sections.backupAndRestore': '💾 Backup & Restore',
    'settings.sections.paymentGateway': '💳 Payment Gateway',
    'settings.sections.otherSettings': '⚙️ Other Settings',

    'settings.descriptions.siteAndSeo': 'Configure site information and SEO settings',
    'settings.descriptions.videoAndUpload': 'Configure video review, quality, transcoding and upload limits',
    'settings.descriptions.userAndCommunity': 'Configure user registration, verification and comment features',
    'settings.descriptions.emailService': 'Configure SMTP or Mailgun email service',
    'settings.descriptions.security': 'Configure login security, captcha, session timeout',
    'settings.descriptions.notifications': 'Configure notification methods, sounds, desktop notifications and quiet hours',
    'settings.descriptions.cacheManagement': 'Manage Redis cache and view statistics',
    'settings.descriptions.backupAndRestore': 'Export and import system settings',
    'settings.descriptions.paymentGateway': 'Configure payment gateways like Stripe, PayPal, Alipay',
    'settings.descriptions.otherSettings': 'Maintenance mode, analytics code, custom styles',

    'settings.placeholders.siteIntro': 'Site introduction',
    'settings.labels.keywords': 'Keywords',
    'settings.placeholders.keywordsExample': 'video,watch online,movies',
    'settings.placeholders.overrideDefaultTitle': 'Override default title',
    'settings.placeholders.seDescription': 'Search engine description',
    'settings.placeholders.keywordsComma': 'keyword1,keyword2,keyword3',

    'settings.labels.requireManualReview': 'Require manual review',
    'settings.tooltips.autoApproveUploads': 'Auto-approve new uploaded videos when enabled',
    'settings.labels.defaultQuality': 'Default Quality',
    'settings.labels.enableTranscoding': 'Enable Transcoding',
    'settings.labels.transcodeFormats': 'Transcode Formats',
    'settings.placeholders.selectTranscodeFormats': 'Select formats to transcode',
    'settings.labels.maxVideoSize': 'Max Video Size (MB)',
    'settings.labels.maxImageSize': 'Max Image Size (MB)',
    'settings.labels.allowedVideoFormats': 'Allowed Video Formats',
    'settings.placeholders.enterFormatAndEnter': 'Enter format and press Enter',
    'settings.labels.allowedImageFormats': 'Allowed Image Formats',

    'settings.labels.requireEmailVerification': 'Require email verification',
    'settings.labels.defaultAvatarUrl': 'Default Avatar URL',
    'settings.labels.maxFavorites': 'Max Favorites',
    'settings.labels.enableComments': 'Enable Comments',
    'settings.labels.commentsRequireReview': 'Comments require review',
    'settings.tooltips.commentsModeration': 'Comments need admin approval before display when enabled',
    'settings.labels.allowGuestComments': 'Allow guest comments',
    'settings.labels.maxCommentLength': 'Max Comment Length',
    'settings.units.characters': 'characters',

    'settings.descriptions.sendTestEmail': 'Send test email to verify SMTP configuration',
    'settings.labels.lastTest': 'Last test: ',

    'settings.tooltips.enableCaptcha': 'Require captcha on login when enabled',
    'settings.labels.maxLoginAttempts': 'Max Login Attempts',
    'settings.labels.lockoutDuration': 'Lockout Duration (minutes)',
    'settings.labels.sessionTimeout': 'Session Timeout (seconds)',
    'settings.units.seconds': 'seconds',

    'settings.descriptions.viewCacheStats': 'View cache hit rate and performance metrics',
    'settings.labels.totalHits': 'Total Hits',
    'settings.labels.totalMisses': 'Total Misses',
    'settings.labels.avgHitRate': 'Avg Hit Rate',
    'settings.labels.hits': 'hits',
    'settings.labels.misses': 'misses',
    'settings.labels.hitRate': 'hit rate',

    'settings.tooltips.maintenanceMode': 'Display maintenance page when enabled',
    'settings.labels.maintenanceMessage': 'Maintenance Message',
    'settings.placeholders.maintenanceMessage': 'Website is under maintenance, please visit later',
    'settings.labels.analyticsCode': 'Analytics Code (Google Analytics, etc.)',
    'settings.labels.customCss': 'Custom CSS',
    'settings.labels.customJs': 'Custom JavaScript',

    'common.saved': 'Saved',
    'settings.cache.clearedCount': 'Cleared ${count} cache keys',
}

def load_locale(lang_code: str) -> dict:
    """Load locale file"""
    locale_path = Path(f'/home/eric/video/admin-frontend/src/i18n/locales/{lang_code}.json')
    with open(locale_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_locale(lang_code: str, data: dict):
    """Save locale file"""
    locale_path = Path(f'/home/eric/video/admin-frontend/src/i18n/locales/{lang_code}.json')
    with open(locale_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def set_nested_key(data: dict, key_path: str, value: str):
    """Set value in nested dict using dot notation"""
    parts = key_path.split('.')
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        current = current[part]
    current[parts[-1]] = value

def add_translations_to_locales():
    """Add all translation keys to all locale files"""
    print("Adding translation keys to locale files...")

    # Load all locale files
    locales = {}
    for lang in ['zh-CN', 'en-US', 'de-DE', 'fr-FR', 'ja-JP', 'zh-TW']:
        locales[lang] = load_locale(lang)

    # Add translations
    added_count = 0
    for chinese_text, key in COMPREHENSIVE_MAP.items():
        # Chinese
        if not key_exists(locales['zh-CN'], key):
            set_nested_key(locales['zh-CN'], key, chinese_text)
            added_count += 1

        # English
        if not key_exists(locales['en-US'], key):
            set_nested_key(locales['en-US'], key, EN_TRANSLATIONS.get(key, f'TODO: {chinese_text}'))
            added_count += 1

        # Other languages (mark as TODO for now)
        for lang in ['de-DE', 'fr-FR', 'ja-JP', 'zh-TW']:
            if not key_exists(locales[lang], key):
                set_nested_key(locales[lang], key, f'TODO: {chinese_text}')
                added_count += 1

    # Save all locale files
    for lang, data in locales.items():
        save_locale(lang, data)

    print(f"✅ Added {added_count} translation entries across {len(locales)} locale files")
    return added_count

def key_exists(data: dict, key_path: str) -> bool:
    """Check if key exists in nested dict"""
    parts = key_path.split('.')
    current = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return False
        current = current[part]
    return True

def fix_settings_file():
    """Fix Settings.tsx file"""
    settings_path = Path('/home/eric/video/admin-frontend/src/pages/Settings.tsx')

    with open(settings_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    replacements = 0

    # Sort by length (longest first) to avoid partial replacements
    sorted_map = sorted(COMPREHENSIVE_MAP.items(), key=lambda x: len(x[0]), reverse=True)

    for chinese_text, translation_key in sorted_map:
        # Special handling for template strings with variables
        if '${' in chinese_text:
            # Handle template literals with variables
            pattern = chinese_text.replace('${response.data.cleared_keys}', r'\$\{response\.data\.cleared_keys\}')
            # Replace in template literal context
            old_pattern = f'`{pattern}`'
            new_replacement = f'`{{{translation_key.replace(".clearedCount", ".clearedCount", )}}}`'.replace(
                '${count}', '${response.data.cleared_keys}'
            )
            if old_pattern in content:
                # For template strings with variables, use t() with variable substitution
                content = content.replace(
                    f'message.success(`{pattern}`)',
                    f'message.success(t(\'{translation_key}\', {{ count: response.data.cleared_keys }}))'
                )
                replacements += 1
            continue

        # Regular string replacements
        patterns = [
            (f'"{chinese_text}"', f't(\'{translation_key}\')'),  # Regular string in code
            (f'placeholder="{chinese_text}"', f'placeholder={{t(\'{translation_key}\')}}'),  # JSX attribute
            (f'label="{chinese_text}"', f'label={{t(\'{translation_key}\')}}'),  # JSX attribute
            (f'header="{chinese_text}"', f'header={{t(\'{translation_key}\')}}'),  # JSX attribute
            (f'title="{chinese_text}"', f'title={{t(\'{translation_key}\')}}'),  # JSX attribute
            (f'tooltip="{chinese_text}"', f'tooltip={{t(\'{translation_key}\')}}'),  # JSX attribute
            (f'content="{chinese_text}"', f'content={{t(\'{translation_key}\')}}'),  # JSX attribute
            (f'addonAfter="{chinese_text}"', f'addonAfter={{t(\'{translation_key}\')}}'),  # JSX attribute
            (f'>{chinese_text}<', f'>{{t(\'{translation_key}\')}}<'),  # JSX children
        ]

        for old_pattern, new_replacement in patterns:
            if old_pattern in content:
                content = content.replace(old_pattern, new_replacement)
                replacements += 1

    # Save file if changes were made
    if content != original_content:
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Fixed Settings.tsx: {replacements} replacements")
        return replacements
    else:
        print("⚠️  No changes needed in Settings.tsx")
        return 0

def main():
    print("="*80)
    print("Comprehensive Settings.tsx i18n Fix")
    print("="*80)
    print()

    # Step 1: Add translations to locale files
    print("Step 1: Adding translations to locale files...")
    add_translations_to_locales()
    print()

    # Step 2: Fix Settings.tsx
    print("Step 2: Fixing Settings.tsx...")
    replacements = fix_settings_file()
    print()

    print("="*80)
    print("✅ Fix complete!")
    print(f"   Total replacements: {replacements}")
    print("="*80)
    print()
    print("Next steps:")
    print("1. Review the changes in Settings.tsx")
    print("2. Test the settings page in all languages")
    print("3. Translate the TODO entries in non-Chinese locale files")

if __name__ == '__main__':
    main()
