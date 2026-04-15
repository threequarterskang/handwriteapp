#!/usr/bin/env python3
# -*- conding: utf-8 -*-

import sqlite3

DB_PATH = "placeholder.db"

def build_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT 英文名字, 数据最大范围 FROM field_rule"
    )
    rows = cur.fetchall()

    for tablename, col_count in rows:
        columns = ", ".join([f'"{ "{" + str(i) + "}" }" TEXT' for i in range(1, col_count + 1)])

        create_sql = f"""
        CREATE TABLE IF NOT EXISTS {tablename} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            {columns}
        );
        """

        try:
            cur.execute(create_sql)
            print(f"✅ 表已创建: {tablename}")
        except sqlite3.OperationalError as e:
            print(f"❌ 创建表失败 {tablename}: {e}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    build_tables()