import pandas as pd
import sqlite3


# =========================
# 用户自定义
# =========================
XLSX_FILE = "gettotalData.xlsx"
DB2_FILE = "placeholder.db"
DB1_FILE = "total.db"
# =========================


def get_standard_map(db_path):
    """
    从 DB2 读取：
    英文名字 -> 检验标准列
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT "英文名字", "检验标准列"
        FROM field_rule
    """)

    result = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return result


def parse_standard_column(value):
    """
    解析检验标准列
    9       -> [9]
    9-23    -> [9,10,...,23]
    None/"" -> []
    """
    if value is None:
        return []

    value = str(value).strip().upper()
    if value in ("", "NONE", "NULL"):
        return []

    if "-" in value:
        start, end = map(int, value.split("-"))
        return list(range(start, end + 1))

    return [int(value)]


def ensure_table(cursor, sheet_name, col_indexes):
    """
    确保表存在，并包含所需字段
    """

    for idx in col_indexes:
        col_name = f"{{{idx}}}"
        try:
            cursor.execute(
                f'SELECT "{col_name}" FROM "{sheet_name}" LIMIT 1'
            )
        except sqlite3.OperationalError:
            pass


def process():
    standard_map = get_standard_map(DB2_FILE)

    xls = pd.ExcelFile(XLSX_FILE)
    conn = sqlite3.connect(DB1_FILE)
    cursor = conn.cursor()

    for sheet_name in xls.sheet_names:
        print(f"\n📄 处理 Sheet：{sheet_name}")

        df = pd.read_excel(xls, sheet_name=sheet_name)

        if "{7}" not in df.columns:
            print("❌ 缺少列 {7}，跳过")
            continue

        if sheet_name not in standard_map:
            print("⚠️ DB2 未配置该 sheet，跳过")
            continue

        col_indexes = parse_standard_column(standard_map[sheet_name])
        if not col_indexes:
            print("⚠️ 检验标准列为空，跳过")
            continue

        ensure_table(cursor, sheet_name, col_indexes)

        for _, row in df.iterrows():
            key_7 = row["{7}"]
            if pd.isna(key_7):
                continue

            print(f"Processing key_7: {key_7} in sheet: {sheet_name}")

            update_data = {}
            for idx in col_indexes:
                excel_col = f"{{{idx}}}"
                if excel_col not in df.columns:
                    raise ValueError(
                        f"Sheet [{sheet_name}] 缺少列 {excel_col}"
                    )
                update_data[f"{{{idx}}}"] = row[excel_col]

            # 判断是否存在
            cursor.execute(
                f'SELECT * FROM "{sheet_name}" WHERE "{{7}}" = ?',
                (key_7,)
            )
            existing = cursor.fetchone()
            print(f"Existing: {existing[0]}")

            if existing:
                # UPDATE
                set_clause = ", ".join(
                    [f'"{k}"=?' for k in update_data]
                )
                sql = f"""
                    UPDATE "{sheet_name}"
                    SET {set_clause}
                    WHERE "{{7}}"=?
                """
                cursor.execute(
                    sql, (*update_data.values(), key_7)
                )

    conn.commit()
    conn.close()
    print("\n✅ 全部处理完成")


if __name__ == "__main__":
    process()