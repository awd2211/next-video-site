#!/usr/bin/env python3
"""
添加多语言字段到数据库
直接使用SQL，避免alembic复杂性
"""
from sqlalchemy import text

from app.database import SessionLocal


def add_multilingual_fields():
    """添加多语言字段"""
    db = SessionLocal()

    try:
        print("=" * 60)
        print("🔧 添加多语言字段到数据库")
        print("=" * 60)

        # 1. Category 多语言
        print("\n1️⃣ 添加 Category 多语言字段...")
        db.execute(
            text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS name_en VARCHAR(100)")
        )
        db.execute(
            text("ALTER TABLE categories ADD COLUMN IF NOT EXISTS description_en TEXT")
        )
        print("   ✅ categories.name_en")
        print("   ✅ categories.description_en")

        # 2. Tag 多语言
        print("\n2️⃣ 添加 Tag 多语言字段...")
        db.execute(text("ALTER TABLE tags ADD COLUMN IF NOT EXISTS name_en VARCHAR(100)"))
        print("   ✅ tags.name_en")

        # 3. Country 多语言
        print("\n3️⃣ 添加 Country 多语言字段...")
        db.execute(
            text("ALTER TABLE countries ADD COLUMN IF NOT EXISTS name_en VARCHAR(100)")
        )
        print("   ✅ countries.name_en")

        # 4. Announcement 多语言
        print("\n4️⃣ 添加 Announcement 多语言字段...")
        db.execute(
            text(
                "ALTER TABLE announcements ADD COLUMN IF NOT EXISTS title_en VARCHAR(200)"
            )
        )
        db.execute(
            text("ALTER TABLE announcements ADD COLUMN IF NOT EXISTS content_en TEXT")
        )
        print("   ✅ announcements.title_en")
        print("   ✅ announcements.content_en")

        db.commit()
        print("\n✅ 字段添加完成！")

        # 5. 填充默认数据
        print("\n🔄 填充默认数据（复制中文到英文）...")
        db.execute(
            text("UPDATE categories SET name_en = name WHERE name_en IS NULL OR name_en = ''")
        )
        db.execute(
            text(
                "UPDATE categories SET description_en = description WHERE description_en IS NULL OR description_en = ''"
            )
        )
        db.execute(text("UPDATE tags SET name_en = name WHERE name_en IS NULL OR name_en = ''"))
        db.execute(
            text("UPDATE countries SET name_en = name WHERE name_en IS NULL OR name_en = ''")
        )
        db.execute(
            text("UPDATE announcements SET title_en = title WHERE title_en IS NULL OR title_en = ''")
        )
        db.execute(
            text(
                "UPDATE announcements SET content_en = content WHERE content_en IS NULL OR content_en = ''"
            )
        )

        db.commit()
        print("✅ 数据填充完成！")

        # 6. 验证结果
        print("\n" + "=" * 60)
        print("🔍 验证结果")
        print("=" * 60)

        print("\n📋 Categories:")
        result = db.execute(text("SELECT name, name_en FROM categories LIMIT 3"))
        for row in result.fetchall():
            print(f"   中文: {row[0]:<15} 英文: {row[1]}")

        print("\n📋 Tags:")
        result = db.execute(text("SELECT name, name_en FROM tags LIMIT 3"))
        for row in result.fetchall():
            print(f"   中文: {row[0]:<15} 英文: {row[1]}")

        print("\n📋 Countries:")
        result = db.execute(text("SELECT name, name_en FROM countries LIMIT 3"))
        for row in result.fetchall():
            print(f"   中文: {row[0]:<15} 英文: {row[1]}")

        print("\n" + "=" * 60)
        print("🎉 多语言字段添加成功！")
        print("=" * 60)

        print("\n💡 下一步:")
        print("   1. 更新 Models（添加name_en等字段）")
        print("   2. 创建 LanguageHelper 工具类")
        print("   3. 更新 API 支持语言参数")
        print("   4. 翻译英文内容")

    except Exception as e:
        db.rollback()
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    add_multilingual_fields()

