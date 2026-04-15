# core/utils.py
import re
from typing import List

def parse_range(spec: str) -> List[str]:
    """
    解析列区间字符串（如 "9-12"），
    返回 ["{9}", "{10}", "{11}", "{12}"]。
    """
    match = re.fullmatch(r"(\d+)-(\d+)", spec.strip())
    if not match:
        raise ValueError(f"无效的列区间格式: {spec}")

    start, end = map(int, match.groups())
    if start > end:
        raise ValueError(f"无效的列区间: {spec}")

    return [f"{{{i}}}" for i in range(start, end + 1)]