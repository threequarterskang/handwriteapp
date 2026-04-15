# core/processor.py
import sqlite3
from typing import Dict, Any

from .rule_engine import eval_condition, eval_rule_value
from .loader import load_field_rule
from .utils import parse_range

def process_field_driven_sample_plan(
    conn1: sqlite3.Connection,
    conn2: sqlite3.Connection,  # ✅ 统一使用 main 传入的 conn2
    row: Dict[str, Any],
    cfg: Dict[str, Any],
    table_name: str  # ✅ 传入表名以便执行 UPDATE
) -> Dict[str, Any]:
    """
    处理 field_driven_sample_plan 类型的模板。
    
    支持：
    1. NORMAL（通过 fields + field_rule 表，含不良数填充）
    2. CAP（通过 rules 数组 + when 条件，支持 DB1 列判断）
    3. BAT / SCR（通过 rules 字典 + _series）
    """
    updates: Dict[str, Any] = {}
    field_rule = None
    
    if "lookup_table" in cfg:
        field_name = row.get("英文名")
        if field_name:
        # ✅ 从 placeholder.db 读取规则（含 inspect_cols / sample_cols / fail_num_cols）
            field_rule = load_field_rule(conn2, cfg, field_name)
            if not field_rule:
                raise ValueError("模板必须配置 lookup_table")

    # ---------- 1. NORMAL 模板（依赖 field_rule 表）----------
    if "fields" in cfg:
        if not field_name or field_name not in cfg["fields"]:
            raise ValueError(f"未知英文字段名: {field_name} for NORMAL template")

        field_cfg = cfg["fields"][field_name]
        strategy_name = field_cfg.get("sample_strategy")
        if not strategy_name:
            raise ValueError("NORMAL 模板的字段必须包含 sample_strategy")

        # ✅ 解析列区间（来自 field_rule 表）
        inspect_cols = parse_range(field_rule["inspect_cols"])
        sample_cols = parse_range(field_rule["sample_cols"])
        fail_num_cols = parse_range(field_rule["fail_num_cols"])  # 如 "17-17"
        check_name_date_cols = parse_range(field_rule["check_name_date_cols"]) 

        # 填充「检验结果」列（如 {9}-{12} = "Ҫ"）
        for col in inspect_cols:
            updates[col] = cfg["inspect_result_value"]

        # 执行 GB2828 策略（如 {13}-{16} = gb2828_LBL({8}) 的结果）
        sample_values = eval_rule_value(f"{strategy_name}({8})", row)
        for col, val in zip(sample_cols, sample_values):
            updates[col] = val

        # ✅ 填充「不良数」（来自 field_rule，固定为 0）
        # 对应你之前“在 field_rule 表中新增不良数=0”的要求
        for col in fail_num_cols:
            updates[col] = cfg["fail_result_num"]
        
        # 填充检验员、审核员、及日期
        inspector_values = [
            row.get("检验员", ""),
            row.get("审核员", ""),
            row.get("日期", "")
        ]
        
        for col, val in zip(check_name_date_cols, inspector_values):
            updates[col] = val
        
        return updates

    # ---------- 2. CAP / IND / TR（rules 是数组，支持 DB1 条件）----------
    # ✅ 匹配【文档1】CAP.json 的 rules 数组结构
    # ✅ 支持 contains({2}, '') 和 not_empty({X}) / empty({X})
    if "rules" in cfg and isinstance(cfg["rules"], list):
        if field_rule:
            strategy_name = cfg.get("sample_strategy")
            if not strategy_name:
                raise ValueError("NORMAL 模板的字段必须包含 sample_strategy")

        # ✅ 解析列区间（来自 field_rule 表）
            inspect_cols = parse_range(field_rule["inspect_cols"])
            sample_cols = parse_range(field_rule["sample_cols"])
            fail_num_cols = parse_range(field_rule["fail_num_cols"])  # 如 "17-17"
            check_name_date_cols = parse_range(field_rule["check_name_date_cols"]) 

            # 填充「检验结果」列（如 {9}-{12} = "Ҫ"）
            for col in inspect_cols:
                updates[col] = cfg["inspect_result_value"]

            # 执行 GB2828 策略（如 {13}-{16} = gb2828_LBL({8}) 的结果）
            sample_values = eval_rule_value(f"{strategy_name}({8})", row)
            for col, val in zip(sample_cols, sample_values):
                updates[col] = val

            # ✅ 填充「不良数」（来自 field_rule，固定为 0）
            # 对应你之前“在 field_rule 表中新增不良数=0”的要求
            for col in fail_num_cols:
                updates[col] = cfg["fail_result_num"]
            
            # 填充检验员、审核员、及日期
            inspector_values = [
                row.get("检验员", ""),
                row.get("审核员", ""),
                row.get("日期", "")
            ]
            
            for col, val in zip(check_name_date_cols, inspector_values):
                updates[col] = val
            
        for rule in cfg.get("rules", []):
            if rule.get("stage") != "base":
                continue
            if not eval_condition(rule.get("when"), row):
                continue
            for col, expr in rule.get("then", {}).items():
                updates[col] = eval_rule_value(expr, row)

        if updates:
            set_sql = ", ".join([f'"{k}" = ?' for k in updates])
            values = list(updates.values()) + [row["rowid"]]
            conn1.execute(
                f"UPDATE {table_name} SET {set_sql} WHERE rowid = ?",
                values
            )
            conn1.commit()
        
        cursor = conn1.cursor()
        
        cursor.execute(
            f"SELECT * , rowid FROM {table_name} WHERE rowid = ?",
            (row["rowid"],)
        )

        row_fetched = cursor.fetchone()
        if not row_fetched:
            raise ValueError(f"Row with rowid {row['rowid']} not found in {table_name} after update")
        row = dict(row_fetched)

        updates.clear()

        # second stage rules
        for rule in cfg.get("rules", []):
            if rule.get("stage") != "series":
                continue
            if not eval_condition(rule.get("when"), row):
                continue
            for col, expr in rule.get("then", {}).items():
                if "_" in col and ("series" in col or "_" in col):
                    updates.update(eval_rule_value(expr, row))
                else:
                    updates[col] = eval_rule_value(expr, row)
        
        return updates

    # useless, can be negelcted, but keep for safety
    if "rules" in cfg and isinstance(cfg["rules"], dict):
        then_clause = cfg["rules"].get("then", {})
        for col, expr in then_clause.items():
            if "_" in col and "series" in col:
                updates.update(eval_rule_value(expr, row))
            else:
                updates[col] = eval_rule_value(expr, row)
        return updates

    # 兜底：理论上不应到达此处
    return updates