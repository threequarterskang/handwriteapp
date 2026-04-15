# core/loader.py
import json
import os
import sqlite3
from typing import Optional, Dict, Any
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR.parent / "config"
DB2_PATH = BASE_DIR.parent / "placeholder.db"

def load_template(name: str) -> Dict[str, Any]:
    """
    加载模板 JSON（保持原样）
    """
    path = os.path.join(CONFIG_DIR, f"{name.lower()}.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def load_field_rule(
    conn2: sqlite3.Connection,  # ✅ 使用 main 传入的 conn2
    template_cfg: Dict[str, Any],
    field_name: str
) -> Optional[Dict[str, str]]:
    """
    从 placeholder.db 的 field_rule 表读取规则。
    
    对应文档中的：
    - lookup_table: 表名（如 "field_rule"）
    - key_column: 查询键（如 "Ӣֶ" / "英文字段名"）
    
    新增：
    - 不良数：固定为 "0"（与 CAP.json 的 failResultNum 一致）
    """
    if "lookup_table" not in template_cfg or "key_column" not in template_cfg:
        return None  # 模板不需要查 field_rule

    table = template_cfg["lookup_table"]
    key_col = template_cfg["key_column"]

    cursor = conn2.cursor()
    
    # ✅ 查询字段增加「不良数」
    cursor.execute(
        f"""
        SELECT 检验结果, 抽检方案, 不良数, 检验员到日期
        FROM {table}
        WHERE {key_col} = ?
        """,
        (field_name,)
    )
    rule = cursor.fetchone()

    if not rule:
        raise ValueError(
            f"未在 {DB2_PATH} 的 {table} 表中找到 "
            f"{key_col}={field_name}"
        )

    # ✅ 返回结构新增 fail_num
    return {
        "inspect_cols": rule[0],  # 如 "9-12"
        "sample_cols": rule[1],   # 如 "13-16"
        "fail_num_cols": rule[2],         # ✅ 固定为 "0"
        "check_name_date_cols": rule[3] # 如 "30-32"
    }