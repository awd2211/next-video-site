#!/usr/bin/env python3
"""获取缺失的翻译键"""
import json
from pathlib import Path


def get_all_keys(obj: dict, prefix: str = "") -> set:
    """递归获取JSON对象中的所有键路径"""
    keys = set()
    for key, value in obj.items():
        full_key = f"{prefix}.{key}" if prefix else key
        keys.add(full_key)
        if isinstance(value, dict):
            keys.update(get_all_keys(value, full_key))
    return keys


admin_i18n = Path("/home/eric/video/admin-frontend/src/i18n/locales")
base_file = admin_i18n / "en-US.json"
de_file = admin_i18n / "de-DE.json"

with open(base_file, 'r', encoding='utf-8') as f:
    base_data = json.load(f)
with open(de_file, 'r', encoding='utf-8') as f:
    de_data = json.load(f)

base_keys = get_all_keys(base_data)
de_keys = get_all_keys(de_data)
missing = sorted(base_keys - de_keys)

print(f"缺失的 {len(missing)} 个键:\n")
for key in missing:
    print(key)
