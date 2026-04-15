import sqlite3
import pandas as pd

# ========== 配置区 ==========
PLACEHOLDER_DB = "placeholder.db"
DB1_PATH = "total.db"        # 你的 DB1 数据库路径
OUTPUT_FILE = "gettotalData.xlsx"

IGNORE_TEMPLATE = "NORMAL"  # 用户指定要忽略的模板名
# ============================

def main():
    # 1️⃣ 读取 placeholder.db 的 field_rule
    conn_placeholder = sqlite3.connect(PLACEHOLDER_DB)
    df_rule = pd.read_sql(
        "SELECT 英文名字, 套用模板 FROM field_rule",
        conn_placeholder
    )
    conn_placeholder.close()

    # 2️⃣ 过滤掉忽略的模板
    df_rule = df_rule[df_rule["套用模板"] != IGNORE_TEMPLATE]

    # 3️⃣ 连接 DB1
    conn_db1 = sqlite3.connect(DB1_PATH)

    # 用于存储所有 sheet 的数据
    sheets_data = {}

    # 4️⃣ 遍历每条规则
    for _, row in df_rule.iterrows():
        tableName = row["英文名字"]
        templateName = row["套用模板"]

        try:
            # 5️⃣ 查询 DB1 中对应表
            base_cols = ['{2}', '{3}', '{7}']
            if templateName != "NORMAL":
                extra_cols = [f'{{{i}}}' for i in range(9, 31)]
                cols = ', '.join(quote_col(c) for  c in base_cols + extra_cols)
            else:
                cols = ', '.join(quote_col(base_cols))

            sql = f"SELECT {cols} FROM [{tableName}]"
            df = pd.read_sql(sql, conn_db1)

            # 6️⃣ 写入 sheet
            sheet_name = templateName
            if sheet_name not in sheets_data:
                sheets_data[sheet_name] = []

            sheets_data[sheet_name].append(df)

        except Exception as e:
            print(f"⚠️ 表 [{tableName}] 查询失败：{e}")

    conn_db1.close()

    # 7️⃣ 导出 Excel
    with pd.ExcelWriter(OUTPUT_FILE, engine="openpyxl") as writer:
        for sheet_name, dfs in sheets_data.items():
            final_df = pd.concat(dfs, ignore_index=True)
            final_df.to_excel(writer, sheet_name=sheet_name, index=False)

    print(f"✅ 完成，已生成 {OUTPUT_FILE}")

def quote_col(col):
    return f'"{col}"'

if __name__ == "__main__":
    main()