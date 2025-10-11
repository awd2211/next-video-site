#!/usr/bin/env python3
"""检查所有后端代码的类型安全问题"""

import os
import re
from collections import defaultdict

def check_directory(directory):
    scalar_issues = defaultdict(list)
    column_issues = defaultdict(list)
    pages_issues = defaultdict(list)
    
    for root, dirs, files in os.walk(directory):
        # 跳过 venv 和 alembic
        if 'venv' in root or 'alembic' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines, 1):
                            # 查找 scalar() 但没有 or 0
                            if '.scalar()' in line and 'or 0' not in line and 'scalar_one' not in line and '# type:' not in line:
                                scalar_issues[filepath].append((i, line.strip()))
                            
                            # 查找 count += 或 count -= 但没有 type: ignore
                            if re.search(r'\w+\s*[+\-]=\s*\d+', line) and 'count' in line and 'type: ignore' not in line:
                                column_issues[filepath].append((i, line.strip()))
                            
                            # 查找分页计算但没有 total > 0 检查
                            if 'math.ceil' in line and '/' in line and 'total' in line:
                                if 'and total > 0' not in line and 'or 0' not in line:
                                    pages_issues[filepath].append((i, line.strip()))
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
    
    return scalar_issues, column_issues, pages_issues

# 检查所有目录
directories = ['app/admin', 'app/utils', 'app/models', 'app/tasks', 'app/middleware']

print("=" * 80)
print("检查所有后端代码的类型安全问题")
print("=" * 80)

total_scalar = 0
total_column = 0
total_pages = 0

for directory in directories:
    if os.path.exists(directory):
        print(f"\n📂 检查 {directory}...")
        scalar_issues, column_issues, pages_issues = check_directory(directory)
        
        if scalar_issues:
            print(f"\n  ⚠️  scalar() 问题 ({sum(len(v) for v in scalar_issues.values())} 处):")
            for filepath, issues in sorted(scalar_issues.items()):
                print(f"    {filepath}:")
                for line_no, line in issues[:3]:  # 只显示前3个
                    print(f"      Line {line_no}: {line[:80]}")
                if len(issues) > 3:
                    print(f"      ... 还有 {len(issues) - 3} 处")
        
        if column_issues:
            print(f"\n  ⚠️  Column 赋值问题 ({sum(len(v) for v in column_issues.values())} 处):")
            for filepath, issues in sorted(column_issues.items()):
                print(f"    {filepath}:")
                for line_no, line in issues[:3]:
                    print(f"      Line {line_no}: {line[:80]}")
                if len(issues) > 3:
                    print(f"      ... 还有 {len(issues) - 3} 处")
        
        if pages_issues:
            print(f"\n  ⚠️  分页计算问题 ({sum(len(v) for v in pages_issues.values())} 处):")
            for filepath, issues in sorted(pages_issues.items()):
                print(f"    {filepath}:")
                for line_no, line in issues[:3]:
                    print(f"      Line {line_no}: {line[:80]}")
                if len(issues) > 3:
                    print(f"      ... 还有 {len(issues) - 3} 处")
        
        total_scalar += sum(len(v) for v in scalar_issues.values())
        total_column += sum(len(v) for v in column_issues.values())
        total_pages += sum(len(v) for v in pages_issues.values())

print("\n" + "=" * 80)
print(f"📊 总计:")
print(f"  - scalar() 问题: {total_scalar} 处")
print(f"  - Column 赋值问题: {total_column} 处")
print(f"  - 分页计算问题: {total_pages} 处")
print(f"  - 总计: {total_scalar + total_column + total_pages} 处")
print("=" * 80)

