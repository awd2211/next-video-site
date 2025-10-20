#!/usr/bin/env python3
"""
Fix Series/EpisodeManager.tsx hardcoded text
Only update zh-CN and en-US
"""

import re
import json
from pathlib import Path

# Translation mapping
EPISODE_TRANSLATIONS = {
    # Page title and sections
    '剧集管理': {'key': 'episode.title', 'en': 'Episode Management'},
    '基本设置': {'key': 'episode.sections.basic', 'en': 'Basic Settings'},
    '片头片尾': {'key': 'episode.sections.openingEnding', 'en': 'Opening & Ending'},

    # Table columns
    '集号': {'key': 'episode.table.episodeNumber', 'en': 'Episode No.'},
    '标题': {'key': 'episode.table.title', 'en': 'Title'},
    '简介': {'key': 'episode.table.description', 'en': 'Description'},
    '状态': {'key': 'episode.table.status', 'en': 'Status'},
    '权限': {'key': 'episode.table.permission', 'en': 'Permission'},
    '点赞': {'key': 'episode.table.likes', 'en': 'Likes'},
    '评论': {'key': 'episode.table.comments', 'en': 'Comments'},
    '创建时间': {'key': 'episode.table.createTime', 'en': 'Created At'},
    '操作': {'key': 'common.actions', 'en': 'Actions'},

    # Status
    '草稿': {'key': 'episode.status.draft', 'en': 'Draft'},
    '已发布': {'key': 'episode.status.published', 'en': 'Published'},
    '已归档': {'key': 'episode.status.archived', 'en': 'Archived'},

    # Permission
    '免费': {'key': 'episode.permission.free', 'en': 'Free'},
    '免费观看': {'key': 'episode.permission.freeWatch', 'en': 'Free Watch'},
    'VIP专享': {'key': 'episode.permission.vipOnly', 'en': 'VIP Only'},
    '推荐': {'key': 'episode.recommended', 'en': 'Recommended'},

    # Form labels
    '标题前缀': {'key': 'episode.form.titlePrefix', 'en': 'Title Prefix'},
    '标题后缀': {'key': 'episode.form.titleSuffix', 'en': 'Title Suffix'},
    '起始集号': {'key': 'episode.form.startNumber', 'en': 'Start Episode Number'},
    '集': {'key': 'episode.unit.episode', 'en': ' '},
    '第': {'key': 'episode.prefix.episode', 'en': 'Episode '},
    '剧集简介': {'key': 'episode.form.description', 'en': 'Episode Description'},
    '关联视频ID': {'key': 'episode.form.videoId', 'en': 'Video ID'},
    '片头结束时间（秒）': {'key': 'episode.form.openingEndTime', 'en': 'Opening End Time (seconds)'},
    '片尾开始时间（秒）': {'key': 'episode.form.endingStartTime', 'en': 'Ending Start Time (seconds)'},

    # Placeholders
    '如：90': {'key': 'episode.placeholder.openingTime', 'en': 'e.g.: 90'},
    '如：2700': {'key': 'episode.placeholder.endingTime', 'en': 'e.g.: 2700'},
    '如：10': {'key': 'episode.placeholder.episodeNumber', 'en': 'e.g.: 10'},
    '请输入视频ID': {'key': 'episode.placeholder.videoId', 'en': 'Enter video ID'},

    # Buttons and actions
    '添加': {'key': 'common.add', 'en': 'Add'},
    '保存': {'key': 'common.save', 'en': 'Save'},
    '取消': {'key': 'common.cancel', 'en': 'Cancel'},
    '确定': {'key': 'common.confirm', 'en': 'Confirm'},
    '删除': {'key': 'common.delete', 'en': 'Delete'},
    '刷新': {'key': 'common.refresh', 'en': 'Refresh'},
    '批量删除': {'key': 'episode.actions.batchDelete', 'en': 'Batch Delete'},
    '选择视频': {'key': 'episode.actions.selectVideo', 'en': 'Select Video'},
    '创建剧集': {'key': 'episode.actions.createEpisode', 'en': 'Create Episode'},
    '自动生成标题': {'key': 'episode.actions.autoGenerateTitle', 'en': 'Auto Generate Title'},

    # Messages
    '创建成功': {'key': 'episode.message.createSuccess', 'en': 'Created successfully'},
    '保存失败': {'key': 'episode.message.saveFailed', 'en': 'Save failed'},
    '删除成功': {'key': 'episode.message.deleteSuccess', 'en': 'Deleted successfully'},
    '删除失败': {'key': 'episode.message.deleteFailed', 'en': 'Delete failed'},
    '加载失败': {'key': 'episode.message.loadFailed', 'en': 'Load failed'},
    '加载视频列表失败': {'key': 'episode.message.loadVideosFailed', 'en': 'Failed to load video list'},
    '批量删除失败': {'key': 'episode.message.batchDeleteFailed', 'en': 'Batch delete failed'},
    '批量发布失败': {'key': 'episode.message.batchPublishFailed', 'en': 'Batch publish failed'},
    '设置失败': {'key': 'episode.message.setFailed', 'en': 'Setting failed'},
    '请选择要删除的剧集': {'key': 'episode.message.selectToDelete', 'en': 'Please select episodes to delete'},
    '请选择要发布的剧集': {'key': 'episode.message.selectToPublish', 'en': 'Please select episodes to publish'},
    '集号必须大于0': {'key': 'episode.validation.numberGreaterThanZero', 'en': 'Episode number must be greater than 0'},

    # Status indicators
    '已设置': {'key': 'episode.status.set', 'en': 'Set'},
    '未设置': {'key': 'episode.status.notSet', 'en': 'Not Set'},

    # Template strings
    '第 {num} 集': {'key': 'episode.template.episodeNum', 'en': 'Episode {num}'},
    '将对选中的 {selectedRowKeys.length} 集设置相同的片头片尾标记': {
        'key': 'episode.message.batchSetOpeningEnding',
        'en': 'Will set the same opening/ending markers for {count} selected episodes'
    },
}

def set_nested_key(data: dict, key_path: str, value: str):
    """Set value in nested dict using dot notation"""
    parts = key_path.split('.')
    current = data
    for part in parts[:-1]:
        if part not in current:
            current[part] = {}
        elif not isinstance(current[part], dict):
            return False
        current = current[part]
    if parts[-1] not in current or isinstance(current.get(parts[-1]), str):
        current[parts[-1]] = value
        return True
    return False

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

def update_translations():
    """Update only zh-CN and en-US"""
    print("📝 更新翻译文件（仅中英双语）...")

    zh_cn = load_locale('zh-CN')
    en_us = load_locale('en-US')

    added = 0
    skipped = 0

    for chinese_text, trans_data in EPISODE_TRANSLATIONS.items():
        key = trans_data['key']
        en_text = trans_data['en']

        if set_nested_key(zh_cn, key, chinese_text):
            added += 1
        else:
            skipped += 1

        if set_nested_key(en_us, key, en_text):
            added += 1
        else:
            skipped += 1

    save_locale('zh-CN', zh_cn)
    save_locale('en-US', en_us)

    print(f"✅ 添加了 {added} 个翻译条目")
    if skipped > 0:
        print(f"⚪ 跳过了 {skipped} 个已存在的键")
    print(f"⚪ 未修改其他语言文件")

    return added

def fix_file():
    """Fix EpisodeManager.tsx"""
    file_path = Path('/home/eric/video/admin-frontend/src/pages/Series/EpisodeManager.tsx')

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # 1. Add useTranslation import if not present
    if 'useTranslation' not in content:
        import_line = "import { useTranslation } from 'react-i18next'"
        # Find React import and add after it
        react_import = re.search(r"import.*from ['\"]react['\"]", content)
        if react_import:
            insert_pos = react_import.end()
            content = content[:insert_pos] + '\n' + import_line + content[insert_pos:]

    # 2. Add t hook initialization
    if not re.search(r'const\s+{\s*t\s*}\s*=\s*useTranslation\(\)', content):
        # Find component function start
        component_match = re.search(r'const\s+EpisodeManager[^{]*{', content)
        if component_match:
            insert_pos = component_match.end()
            content = content[:insert_pos] + '\n  const { t } = useTranslation()\n' + content[insert_pos:]

    # 3. Replace hardcoded text
    replacements = 0
    sorted_map = sorted(EPISODE_TRANSLATIONS.items(), key=lambda x: len(x[0]), reverse=True)

    for chinese_text, trans_data in sorted_map:
        key = trans_data['key']

        # Skip template strings for now
        if '{' in chinese_text:
            continue

        patterns = [
            # Regular strings
            (f'"{chinese_text}"', f't(\'{key}\')'),
            (f"'{chinese_text}'", f"t('{key}')"),

            # JSX attributes
            (f'title="{chinese_text}"', f'title={{t(\'{key}\')}}'),
            (f'label="{chinese_text}"', f'label={{t(\'{key}\')}}'),
            (f'placeholder="{chinese_text}"', f'placeholder={{t(\'{key}\')}}'),

            # JSX children
            (f'>{chinese_text}<', f'>{{t(\'{key}\')}}<'),

            # Table column titles
            (f"title: '{chinese_text}'", f"title: t('{key}')"),
            (f'title: "{chinese_text}"', f"title: t('{key}')"),

            # Select.Option
            (f'<Select.Option value="draft">{chinese_text}</Select.Option>',
             f'<Select.Option value="draft">{{t(\'{key}\')}}</Select.Option>' if chinese_text == '草稿' else ''),
            (f'<Select.Option value="published">{chinese_text}</Select.Option>',
             f'<Select.Option value="published">{{t(\'{key}\')}}</Select.Option>' if chinese_text == '已发布' else ''),
        ]

        for old_pattern, new_replacement in patterns:
            if old_pattern and old_pattern in content:
                content = content.replace(old_pattern, new_replacement)
                replacements += 1

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 修复了 EpisodeManager.tsx: {replacements} 处替换")
        return replacements
    else:
        print("⚠️  没有需要修复的内容")
        return 0

def main():
    print("="*80)
    print("修复 Series/EpisodeManager.tsx 硬编码文本（仅中英双语）")
    print("="*80)
    print()

    # Update translations
    added = update_translations()
    print()

    # Fix file
    replacements = fix_file()
    print()

    print("="*80)
    print("✅ 修复完成!")
    print(f"   - 新增翻译键: {len(EPISODE_TRANSLATIONS)} 个")
    print(f"   - 代码替换: {replacements} 处")
    print(f"   - 修改文件: 3 个 (EpisodeManager.tsx, zh-CN.json, en-US.json)")
    print(f"   - 未修改: 4 个语言文件")
    print("="*80)

if __name__ == '__main__':
    main()
