#!/usr/bin/env python3
"""
Скрипт миграции базы данных для добавления поля username
"""
import sqlite3
import os
from pathlib import Path


def migrate_database():
    """Добавляет поле username в таблицу clients если его нет"""
    db_path = Path("./data/bot.db")
    
    if not db_path.exists():
        print("База данных не найдена, создание новой...")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, есть ли поле username
        cursor.execute("PRAGMA table_info(clients)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'username' not in columns:
            print("Добавляем поле username в таблицу clients...")
            cursor.execute("ALTER TABLE clients ADD COLUMN username TEXT")
            conn.commit()
            print("✅ Поле username успешно добавлено!")
        else:
            print("✅ Поле username уже существует")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")


if __name__ == "__main__":
    migrate_database()
