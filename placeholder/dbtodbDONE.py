import sqlite3

# ================== 配置 ==================
db1_path = "total.db"
db2_path = "placeholder.db"
source_table = "total"

# db1 中的完整字段（12 列）
FIELDS = [
    "英文名",
    "供应商",
    "物料名称",
    "规格型号",
    "检验日期",
    "批号",
    "采购订单",
    "物料代码",
    "数量",
    "检验员",		
    "审核员",
    "日期",
    "是否需要焊接",
    "模板名",
    "所属项目名"
]

# 映射到 db2 表中的 {1} ~ {8}
MAP_FIELDS = [
    "供应商",
    "物料名称",
    "规格型号",
    "检验日期",
    "批号",
    "采购订单",
    "物料代码",
    "数量"
]

# ================== 数据库连接 ==================
conn1 = sqlite3.connect(db1_path)
conn2 = sqlite3.connect(db2_path)

cur1 = conn1.cursor()
cur2 = conn2.cursor()

# ================== 读取 db1 数据 ==================
cur1.execute(
    f"SELECT {', '.join([f'\"{f}\"' for f in FIELDS])} FROM \"{source_table}\""
)
rows = cur1.fetchall()

for row in rows:
    data = dict(zip(FIELDS, row))
    table_name = data["英文名"]

    # ================== 检查 db2 是否存在该表 ==================
    cur2.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    if not cur2.fetchone():
        print(f"跳过：db2 中不存在表 {table_name}")
        continue

    # ================== 如果 db1 不存在该表 → 创建 ==================
    cur1.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    if not cur1.fetchone():

        # 读取 db2 表结构
        cur2.execute(f"PRAGMA table_info(\"{table_name}\")")
        schema = cur2.fetchall()

        # 构建字段定义（统一加引号，防止关键字冲突）
        col_defs = [f'"{col[1]}" {col[2]}' for col in schema]

        # ✅ 在最前面插入“英文名”
        col_defs.insert(0, '"英文名" TEXT')

        # ✅ 追加额外字段
        col_defs += [
            '"检验员" TEXT',		
            '"审核员" TEXT',
            '"日期" TEXT',
            '"是否需要焊接" TEXT',
            '"模板名" TEXT',
            '"所属项目名" TEXT'
        ]

        create_sql = f"CREATE TABLE \"{table_name}\" ({', '.join(col_defs)})"
        print("创建表 SQL：\n", create_sql)

        cur1.execute(create_sql)

    # ================== 构建插入数据 ==================
    insert_data = {}

    # ✅ 插入“英文名”（第一列）
    insert_data["英文名"] = data["英文名"]

    # 映射到 {1}, {2}, ...
    for i, field in enumerate(MAP_FIELDS):
        insert_data[f"{{{i+1}}}"] = data[field]

    # 附加字段
    insert_data["检验员"] = data["检验员"]
    insert_data["审核员"] = data["审核员"]
    insert_data["日期"] = data["日期"]
    insert_data["是否需要焊接"] = data["是否需要焊接"]
    insert_data["模板名"] = data["模板名"]
    insert_data["所属项目名"] = data["所属项目名"]

    # ================== 执行插入 ==================
    cols = ", ".join([f'"{c}"' for c in insert_data.keys()])
    placeholders = ", ".join(["?"] * len(insert_data))

    insert_sql = f"INSERT OR IGNORE INTO \"{table_name}\" ({cols}) VALUES ({placeholders})"

    cur1.execute(insert_sql, list(insert_data.values()))

# ================== 提交并关闭 ==================
conn1.commit()
conn1.close()
conn2.close()

print("\n✅ 全部完成（支持 {num} 列名 / 自动建表 / 防重复插入 / 首列为英文名）")
