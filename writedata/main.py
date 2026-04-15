# main.py
import sqlite3
import sys
sys.path.append('.')

from core.dispatcher import DISPATCHER
from core.loader import load_template

DB1 = "total.db"
DB2 = "placeholder.db"
#table_name = "DIO"

def main(table_name: str):
    conn1 = sqlite3.connect(DB1)
    conn2 = sqlite3.connect(DB2)  # ✅ 唯一创建点
    conn1.row_factory = sqlite3.Row

    cursor = conn1.cursor()
    cursor.execute("""
        SELECT name FROM sqlite_master WHERE type='table' AND name=?""", (table_name,))

    if cursor.fetchone():
        cursor.execute(f"SELECT *, rowid FROM {table_name}")
    else:
        print(f"表不存在: {table_name}")

    print(f'{table_name} is in processing......')

    for row in cursor.fetchall():
        template_name = row["模板名"].lower()
        cfg = load_template(template_name)

        processor = DISPATCHER.get(cfg.get("type"))
        if not processor:
            raise ValueError(f"未知模板类型: {cfg.get('type')}")

        # ✅ 同时传入 conn1 和 conn2
        updates = processor(conn1, conn2, dict(row), cfg, table_name)

        if updates:
            set_sql = ", ".join([f'"{k}" = ?' for k in updates])
            values = list(updates.values()) + [row["rowid"]]
            cursor.execute(
                f"UPDATE {table_name} SET {set_sql} WHERE rowid = ?",
                values
            )

    conn1.commit()
    conn1.close()
    conn2.close()
    print(f'{table_name}.....处理完成')

if __name__ == "__main__":
    conn3 = sqlite3.connect(DB2)
    conn3.row_factory = sqlite3.Row

    cursor = conn3.cursor()
    
    res = cursor.execute(
        'SELECT "英文名字" FROM field_rule'
    )

    for tbn in res:
        table_name = tbn["英文名字"]
        main(table_name)
    
    conn3.commit()
    conn3.close()
    print("ALL Done")
