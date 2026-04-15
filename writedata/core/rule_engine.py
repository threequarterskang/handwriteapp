import re
import random
import math
from strategies.gb2828 import STRATEGY_MAP

def get_number(expr: str) -> float:
    """从字符串中提取第一个数字，如 '760±10' -> 760.0"""
    m = re.search(r"[\d.]+", expr)
    if not m:
        raise ValueError(f"无法从 '{expr}' 中提取数字")
    return float(m.group())

def extract_plus_minus(expr: str):
    """解析 ± 表达式，如 '67±3%' 或 '760±10'"""
    m = re.match(r"([\d.]+)\s*±\s*([\d.]+)%?", expr)
    if not m:
        raise ValueError(f"无法解析 ± 表达式: {expr}")
    return float(m.group(1)), float(m.group(2))

def eval_condition(cond: str, row: dict) -> bool:
    """评估条件表达式，如 gt({8}, 1)"""
    if cond.startswith("gt("):
        m = re.match(r"gt\((\{\d+\}),\s*([\d.]+)\)", cond)
        col, val = m.groups()
        return float(row[col]) > float(val)
    if cond.startswith("lt("):
        m = re.match(r"lt\((\{\d+\}),\s*([\d.]+)\)", cond)
        col, val = m.groups()
        return float(row[col]) < float(val)
    if cond.startswith("eq("):
        m = re.match(r"eq\((\{\d+\}),\s*([\d.]+)\)", cond)
        col, val = m.groups()
        return float(row[col]) == float(val)
    if cond.startswith("lte("):
        m = re.match(r"lte\((\{\d+\}),\s*([\d.]+)\)", cond)
        col, val = m.groups()
        return float(row[col]) <= float(val)
    if cond.startswith("contains("):            # CAP方案使用
        m = re.match(r"contains\((\{\d+\}),\s*'(.*?)'\)", cond)
        col, sub = m.groups()
        return sub in str(row.get(col, ""))
    if cond.startswith("not_contains("):
        return not eval_condition(cond.replace("not_contains", "contains"), row)
    if cond.startswith("not_empty("):
        m = re.match(r"not_empty\((.+?)\)", cond)
        col = m.group(1)
        return str(row.get(col, "")).strip() != ""
    if cond.startswith("empty("):
        m = re.match(r"empty\((.+?)\)", cond)
        col = m.group(1)
        return str(row.get(col, "")).strip() == ""
    if cond == "always_true()":
        return True
    raise ValueError(f"未知条件: {cond}")

def eval_rule_value(expr: str, row: dict):
    """评估生成表达式"""
    # 1. 固定字符串
    if expr.startswith("'"):
        return expr.strip("'")

    # 2. 简单函数
    if expr.startswith("get_number("):
        col = re.search(r"\{(.+?)\}", expr).group(1)
        return get_number(row[f"{{{col}}}"])

    # 3. 随机范围 (min, max, precision, suffix)
    if expr.startswith("random_range("):
        m = re.match(r"random_range\(([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*'(.*?)'\)", expr)
        lo, hi, prec, suffix = m.groups()
        val = random.uniform(float(lo), float(hi))
        valmin = round(val, int(prec))
        return f"({valmin}~{round(random.uniform(float(valmin), float(hi)), int(prec))}){suffix}"

    # 4. 带后缀的随机范围 (min, max, suffix)
    if expr.startswith("random_range_with_suffix("):
        m = re.match(r"random_range_with_suffix\(([\d.]+),\s*([\d.]+),\s*'(.*?)', \s*([\d.]+)\)", expr)
        lo, hi, suffix, decimal_places = m.groups()
        lo, hi = float(lo), float(hi)
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        if decimal_places.isdigit() and int(decimal_places) == 0:
            return f"({int(round(a))}~{int(round(b))}){suffix}"
        else:
            return f"({round(a, int(decimal_places))}~{round(b, int(decimal_places))}){suffix}"

    # 5. 从列生成随机范围
    if expr.startswith("random_range_from_col("):
        col = re.search(r"\{(.+?)\}", expr).group(1)
        val = row[f"{{{col}}}" ]
        base, delta = extract_plus_minus(val)
        lo, hi = base - delta, base + delta
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"{int(round(a, 1))}~{int(round(b, 1))}"

    # 6. 从百分比列生成
    if expr.startswith("random_range_from_percent("):
        col = re.search(r"\{(.+?)\}", expr).group(1)
        val = row[f"{{{col}}}" ]
        num1, pct = extract_plus_minus(val.replace('%', ''))
        lo, hi = num1 * (1 - pct / 100), num1 * (1 + pct / 100)
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"{round(a, 1)}~{round(b, 1)}"

    # 7. 带条件存在的百分比随机
    if expr.startswith("random_range_from_percent_if_exists("):
        col = re.search(r"\{(.+?)\}", expr).group(1)
        val = row[f"{{{col}}}"]
        if val == "/":
            return "/"
        else:
            num1, pct = extract_plus_minus(val)
            lo, hi = num1 * (1 - pct / 100), num1 * (1 + pct / 100)
            a = random.uniform(lo, hi)
            if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
            b = random.uniform(lo, hi)
            if int(b) <= int(a): b = random.uniform(a, hi)
            return f"{int(round(a, 2))}~{int(round(b, 2))}"

    # 8. 从固定集合选两个
    if expr.startswith("random_select_two("):
        m = re.match(r"random_select_two\((.+)\)", expr)
        args = [p.strip() for p in m.group(1).split(",")]
        nums = list(map(float, args[:-1]))
        suffix = args[-1]
        a, b = random.sample(nums, 2)
        if a > b: a, b = b, a
        return f"({a}~{b}){suffix}"

    # 9. 基于基数的成对生成
    if expr.startswith("random_pair_from_base("):
        m = re.match(r"random_pair_from_base\((\{\d+\}),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)\)", expr)
        col, s1, s2, s3 = m.groups()
        base = random.uniform(1.0, float(row[col]))
        nums = [base + float(s1), base + float(s2), base + float(s3)]
        max_val = max(nums)
        first = random.choice([n for n in nums if n < max_val])
        second = random.choice([n for n in nums if n > first])
        return f"{round(first, 1)}~{round(second, 1)}"

    # 10. 带步进的成对生成
    if expr.startswith("random_pair_from_range_with_steps("):
        m = re.match(r"random_pair_from_range_with_steps\((\{\d+\}),\s*(\{\d+\}),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+),\s*([\d.]+)\)", expr)
        col1, col2, s1, s2, s3, s4 = m.groups()
        low, high = float(row[col1]), float(row[col2])
        base = random.uniform(low, high)
        steps = [base + float(s1), base + float(s2), base + float(s3), base + float(s4)]
        max_val = max(steps)
        first = random.choice([n for n in steps if n < max_val])
        second = random.choice([n for n in steps if n > first])
        return f"{round(first, 1)}~{round(second, 1)}"

    # 11. 从列提取 ~ 左侧
    if expr.startswith("extract_left_of_tilde_percentage("):
        col = re.search(r"\{(.+?)\}", expr).group(1)
        val = row[f"{{{col}}}"]
        if not val or val.strip() == "" or val == "/":
            return "/"
        num1, pct = extract_plus_minus(val)
        lo, hi = num1 * (1 - pct / 100), num1 * (1 + pct / 100)
        a = random.uniform(lo, hi)
        return f"{int(round(a, 1))}"

    # 11.1
    if expr.startswith("extract_left_of_tilde_nopercentage("):
        col = re.search(r"\{(.+?)\}", expr).group(1)
        val = row[f"{{{col}}}"]
        base, delta = extract_plus_minus(val)
        lo, hi = base - delta, base + delta
        a = random.uniform(lo, hi)
        return f"{int(round(a, 1))}"

    # 12. 从列提取 ~ 左侧并加后缀
    if expr.startswith("electrical_strengthvalue_from_fixed_set_and_add_suffix("):
        args = re.findall(r"([\d.]+)", expr)
        suffix = re.search(r"'(.*?)'", expr).group(1)
        vals = list(map(float, args))
        a = random.choice([v for v in vals if v != max(vals)])
        return f"{a}{suffix}"

    # 13. 条件非空
    if expr.startswith("if_not_empty("):
        m = re.match(r"if_not_empty\((\{\d+\}),\s*'(.*?)'\s*,\s*'(.*?)'\)", expr)
        col, true_val, false_val = m.groups()
        return true_val if row.get(col, "").strip() else false_val

    # 14. 从范围列生成数列
    if "_series" in expr:
        return eval_series_expression(expr, row)

    # 15. 按数量填充区间
    if expr.startswith("fill_range_by_count("):
        return fill_range_by_count(expr, row)

    # 16. 带条件的按数量填充
    if expr.startswith("fill_range_by_count_if("):
        return fill_range_by_count_if(expr, row)

    # 17. 从固定集合生成成对值
    if expr.startswith("random_pair_from_fixed_set("):
        args = re.findall(r"([\d.]+)", expr)
        vals = list(map(float, args[:-1]))
        suffix = re.findall(r"'(.*?)'", expr)[0]
        a = random.choice([v for v in vals if v != max(vals)])
        b = random.choice([v for v in vals if v > a])
        return f"({a}~{b}){suffix}"

    # 18. 从范围排除最大值生成成对值
    if expr.startswith("random_pair_from_range_exclusive("):
        m = re.match(r"random_pair_from_range_exclusive\(([\d.]+),\s*([\d.]+),\s*'(.*?)'\)", expr)
        lo, hi, suffix = m.groups()
        lo, hi = float(lo), float(hi)
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"({int(round(a, 2))}~{int(round(b, 2))}){suffix}"

    # 19. 带前缀的破折号范围
    if expr.startswith("random_pair_from_dash_range_with_prefix("):
        m = re.match(r"random_pair_from_dash_range_with_prefix\((\{\d+\}),\s*'(.*?)'\)", expr)
        col, prefix = m.groups()
        val = row[col]
        left, right = map(float, val.split('~'))
        a = random.uniform(left, right)
        if abs(a - right) < 1e-6: a = random.uniform(left, right)
        b = random.uniform(left, right)
        if b <= a: b = random.uniform(a, right)
        return f"{prefix}({round(a, 2)}~{round(b, 2)})%"

    # 20. GB2828 策略调用
    if expr.startswith("gb2828_"):
        func_name = expr.split('(')[0]
        if func_name not in STRATEGY_MAP:
            raise ValueError(f"未知的 GB2828 策略: {func_name}")
        qty = int(row.get('{8}', 0))
        return STRATEGY_MAP[func_name](qty)
    
    # 21. TR 特例：根据数量生成随机范围（如 0.55~0.75mA）
    if expr.startswith("tr_random_range_with_suffix("):
        m = re.match(r"tr_random_range_with_suffix\(([\d.]+),\s*([\d.]+),\s*'(.+?)',\s*([\d.]+)\)", expr)
        lo, hi, suffix, decimal_places = m.groups()
        lo, hi = float(lo), float(hi)
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"({round(a, int(decimal_places))}+{round(b, int(decimal_places))})/2){suffix}"
    
    # 22. TR 
    if expr.startswith("tr_extract_left_of_tilde("):
        m = re.match(r"tr_extract_left_of_tilde\((\{\d+\})\)", expr)
        if not m:
            raise ValueError(f"无效的 TR 表达式: {expr}")
        col = m.group(1)
        val = row.get(col, "")
        base, delta = extract_plus_minus(val)
        lo, hi = base - delta, base + delta
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"{int(round(a, 1))}"
    
    # 23. TR
    if expr.startswith("tr_unload_current("):
        m = re.match(r"tr_unload_current\((\{\d+\})\)", expr)
        if not m:            
            raise ValueError(f"无效的 TR 表达式: {expr}")
        col = m.group(1)
        base = random.uniform(1.0, float(row[col]))
        nums = [base + float(0.1), base + float(0.2), base + float(0.3)]
        max_val = max(nums)
        first = random.choice([n for n in nums if n < max_val])
        return f"{round(first, 1)}"

    # 24. TR
    if expr.startswith("tr_extract_left_of_tilde_withpercent("):
        m = re.match(r"tr_extract_left_of_tilde_withpercent\((\{\d+\})\)", expr)
        if not m:            
            raise ValueError(f"无效的 TR 表达式: {expr}")
        col = m.group(1)
        val = row.get(col, "")
        base, delta = extract_plus_minus(val.replace('%', ''))
        lo, hi = base * (1 - delta / 100), base * (1 + delta / 100)
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"{round(a, 1)}" 

    # 25. TR
    if expr.startswith("single_phase_short_resistant("):
        m = re.match(r"single_phase_short_resistant\((\{\d+\}),\s*(\{\d+\})\)", expr)
        if not m:            
            raise ValueError(f"无效的 TR 表达式: {expr}")
        col1, col2 = m.groups()
        low, high = float(row[col1]), float(row[col2])
        base = random.uniform(low, high)
        steps = [base + float(0.1), base + float(0.2), base + float(0.3), base + float(0.4)]
        max_val = max(steps)
        first = random.choice([n for n in steps if n < max_val])
        return f"{round(first, 1)}"
    
    # 26. IND
    if expr.startswith("random_pair_from_percent_range_with_prefix("):
        m = re.match(r"random_pair_from_percent_range_with_prefix\((\{\d+\}),\s*'(.*?)'\)", expr)
        col, prefix = m.groups()
        val = row[col]
        num1, pct = extract_plus_minus(val.replace('%', ''))
        lo, hi = num1 * (1 - pct / 100), num1 * (1 + pct / 100)
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"{prefix}({round(a, 2)}~{round(b, 2)})mH"

    # 27. IND
    if expr.startswith("insulation_resistancevalue_from_fixed_set_and_add_suffix("):
        args = re.match(r"insulation_resistancevalue_from_fixed_set_and_add_suffix\((\d+),\s*(\d+),\s*'(.*?)'\)", expr)
        if not args:
            raise ValueError(f"无效的 IND 表达式: {expr}")
        val1, val2, suffix = args.groups()
        a = random.uniform(int(val1), int(val2))
        return f"{int(a)}{suffix}"
                       
    # 28. IND
    if expr.startswith("inductancevalue_and_add_suffix("):
        m = re.match(r"inductancevalue_and_add_suffix\((\{\d+\}),\s*'(.*?)'\)", expr)
        if not m:
            raise ValueError(f"无效的 IND 表达式: {expr}")
        col, suffix = m.groups()
        val = row[col]
        num1, pct = extract_plus_minus(val.replace('%', ''))
        lo, hi = num1 * (1 - pct / 100), num1 * (1 + pct / 100)
        a = random.uniform(lo, hi)
        if abs(a - hi) < 1e-6: a = random.uniform(lo, hi)
        b = random.uniform(lo, hi)
        if b <= a: b = random.uniform(a, hi)
        return f"A、B、C    {round(a, 1)}{suffix}"
    
    # 29. IND
    if expr.startswith("impendance_voltagevalue_and_add_suffix("):
        m = re.match(r"impendance_voltagevalue_and_add_suffix\((\{\d+\}),\s*'(.*?)'\)", expr)
        if not m:
            raise ValueError(f"无效的 IND 表达式: {expr}")
        col, prefix = m.groups()
        val = row[col]
        left, right = map(float, val.split('~'))
        a = random.uniform(left, right)
        if abs(a - right) < 1e-6: a = random.uniform(left, right)
        b = random.uniform(left, right)
        if b <= a: b = random.uniform(a, right)
        return f"A、B、C    {round(a, 2)}{prefix}"
    
    raise ValueError(f"未知表达式: {expr}")

# --- 辅助函数 ---
def eval_series_expression(expr: str, row: dict):
    """处理 BAT/SCR 的 series 规则"""
    # BAT generate_series({22}, {15}, {16}, 32, 38)
    m = re.match(r"(\w+)\((\{\d+\}),\s*(\{\d+\}),\s*(\{\d+\}),\s*([\d.]+),\s*([\d.]+)\)", expr)
    if m:
        func_name, count_key, range_key1, range_key2, start1, start2 = m.groups()
        count = extract_before_bracket(row[count_key])
        low1, high1 = extract_two_numbers(row[range_key1])
        low2, high2 = extract_two_numbers(row[range_key2])

        start1, start2 = int(start1), int(start2)

        series_a = generate_one_bat_series(start1, count, low1, high1)
        series_b = generate_one_bat_series(start2, count, low2, high2)

        updates = {}
        for idx, val in enumerate(series_a):
            updates[f"{{{32 + idx}}}"] = str(val)
        for idx, val in enumerate(series_b):
            updates[f"{{{38 + idx}}}"] = str(val)

        return updates
    
    elif (m := re.match(r"(\w+)\((\{\d+\}),\s*(\{\d+\}),\s*([\d.]+),\s*([\d.]+)\)", expr)):
        func_name, count_key, range_key, start1, start2 = m.groups()

        if func_name == "generate_bt_series":   
            # BT PATTERN
            count = extract_before_bracket(row[count_key])
            low, high = extract_two_numbers(row[range_key])

            start1, start2 = int(start1), int(start2)

            series_a = generate_one_scrbt_series(96, start1, low, high)
            series_b = generate_one_scrbt_series(96, start2, low, high)

            updates = {}
            
            if count <= len(series_a):
                updates[f"{{{start1}}}"] = str(series_a[0])
                for i in range(1, count):
                    val = series_a[i]
                    col = i % 5
                    row = i // 5
                    if col == 0:
                        position  = start1 + row * 12
                    else:
                        position = start1 + 12 * row + col
                    updates[f"{{{position}}}"] = str(val)
                return updates

            else:
                updates[f"{{{start1}}}"] = str(series_a[0])
                for i in range(1, 40):
                    val = series_a[i]
                    col = i % 5
                    row = i // 5
                    if col == 0:
                        position  = start1 + row * 12
                    else:
                        position = start1 + 12 * row + col
                    updates[f"{{{position}}}"] = str(val)
                updates[f"{{{start2}}}"] = str(series_b[0])
                for i in range(1, count-40):
                    val = series_b[i]
                    col = i % 5
                    row = i // 5
                    if col == 0:
                        position  = start2 + row * 12
                    else:
                        position = start2 + 12 * row + col
                    updates[f"{{{position}}}"] = str(val)
                return updates

        elif func_name == "generate_scr_series":
            # SCR PATTERN
            count = extract_before_bracket(row[count_key])
            low, high = extract_two_numbers(row[range_key])

            start1, start2 = int(start1), int(start2)

            series_a = generate_one_scrbt_series(156, start1, low, high)
            series_b = generate_one_scrbt_series(156, start2, low, high)

            updates = {}
            
            if count <= len(series_a):
                updates[f"{{{start1}}}"] = str(series_a[0])
                for i in range(1, count):
                    val = series_a[i]
                    col = i % 5
                    row = i // 5
                    if col == 0:
                        position  = start1 + row * 12
                    else:
                        position = start1 + 12 * row + col
                    updates[f"{{{position}}}"] = str(val)
                return updates

            else:
                updates[f"{{{start1}}}"] = str(series_a[0])
                for i in range(1, 65):
                    val = series_a[i]
                    col = i % 5
                    row = i // 5
                    if col == 0:
                        position  = start1 + row * 12
                    else:
                        position = start1 + 12 * row + col
                    updates[f"{{{position}}}"] = str(val)
                updates[f"{{{start2}}}"] = str(series_b[0])
                for i in range(1, count-65):
                    val = series_b[i]
                    col = i % 5
                    row = i // 5
                    if col == 0:
                        position  = start2 + row * 12
                    else:
                        position = start2 + 12 * row + col
                    updates[f"{{{position}}}"] = str(val)
                return updates
        
        else:
            return None

def extract_before_bracket(expr: str) -> int:
    m = re.match(r"(\d+)", expr)
    return int(m.group()) if m else 1

def fill_range_by_count(expr: str, row: dict):
    m = re.match(r"fill_range_by_count\((\{\d+\}),\s*(\{\d+\}),\s*(\d+),\s*(\d+),\s*(\d+)\)", expr)
    count_col, source_col, start_col, end_col, decimal_places = m.groups()
    count = int(float(row[count_col]))
    rng = row[source_col]
    left, right = map(float, re.findall(r"[\d.]+", rng)[:2])
    if decimal_places.isdigit() and int(decimal_places) == 0:
        values = [str(int(round(random.uniform(left, right), int(decimal_places)))) for _ in range(count)]
        values_left = int(left)
        values_right = int(right)
    else:
        values = [str(round(random.uniform(left, right), int(decimal_places))) for _ in range(count)]
        values_left = left
        values_right = right
    updates = {}
    for i, val in enumerate(values):
        col = int(start_col) + i
        if col <= int(end_col):
            updates[f"{{{col}}}"] = val

    updates[f"{{{int(start_col)}}}"] = values_left
    updates[f"{{{int(start_col)+1}}}"] = values_right

    return updates

def fill_range_by_count_if(expr: str, row: dict):
    m = re.match(r"fill_range_by_count_if\((\{\d+\}),\s*(\{\d+\}),\s*(\d+),\s*(\d+),\s*(\{\d+\}),\s*(\d+)\)", expr)
    count_col, source_col, start_col, end_col, cond_col, decimal_places = m.groups()
    if row[cond_col] == "/":
        return {}
    else:
        return fill_range_by_count(f"fill_range_by_count({count_col}, {source_col}, {start_col}, {end_col}, {decimal_places})", row)

# ------------SCR:156\BT:96---------------

def generate_one_scrbt_series(max, start_j, low, high):                
    j = start_j
    end_j = start_j + max
    result = []

    while j <= end_j:
        for i in range(0, 5):
            j = j + 1
            val = round(random.uniform(low, high), 1)
            result.append(val)
        j += 8

    # ✅ 确保至少包含 low 和 high
    result[0] = low
    result[1] = high

    return result

"""
    # ✅ 打乱顺序，避免固定在首尾
    random.shuffle(result)
"""
# ------------BAT---------------
# def generate_bat_series(row, count_key, range_key1, range_key2, start1, start2):

def extract_two_numbers(expr: str):
    nums = re.findall(r"[\d.]+", expr)
    return float(nums[0]), float(nums[1])

def generate_one_bat_series(start_j, count, low, high):
    j = start_j
    result = []

    while len(result) < count and j < 180:
        for i in range(1, 5):
            j += i
        j += 8
        if low <= j <= high:
            result.append(j)

    # 不足则随机补
    while len(result) < count:
        result.append(random.randint(int(low), int(high)))

    return result
    
# ------------BT---------------
# def generate_bt_series(row, range_key, start1, start2):

def random_select_two(*args, suffix=""):
    nums = list(map(float, args[:-1]))
    suffix = args[-1].strip("'")

    a, b = random.sample(nums, 2)
    if a > b:
        a, b = b, a

    return f"({a}~{b}){suffix}"
