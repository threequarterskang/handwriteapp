import os
import pandas as pd

# =========================
# 配置区（按需修改）
# =========================
xlsx_dir = "./xlsx_files"     # 存放所有 xlsx 文件的目录
output_dir = "./output_txt"   # 输出 txt 文件的目录
# =========================


# 创建输出目录（如果不存在）
os.makedirs(output_dir, exist_ok=True)


# 使用 set 来存储字符，天然去重
chinese = set()    # 中文字符
numbers = set()    # 数字
english = set()    # 英文字母
others = set()     # 其他字符（符号、标点等）


def classify_char(ch):
    """
    判断单个字符的类型，并加入对应的集合
    """
    # 判断是否为汉字（Unicode 中文范围）
    if '\u4e00' <= ch <= '\u9fff':
        chinese.add(ch)

    # 判断是否为数字
    elif ch.isdigit():
        numbers.add(ch)

    # 判断是否为英文字母（包含大小写）
    elif ch.isalpha():
        english.add(ch)

    # 其他字符（符号、空格、标点等）
    else:
        others.add(ch)


# 遍历 xlsx 目录下的所有文件
for fname in os.listdir(xlsx_dir):

    # 只处理 xlsx 文件
    if fname.endswith(".xlsx"):
        file_path = os.path.join(xlsx_dir, fname)

        try:
            # 读取 Excel 中所有 sheet（sheet_name=None）
            sheets = pd.read_excel(file_path, sheet_name=None)

            # 遍历每一个 sheet
            for sheet_df in sheets.values():

                # 遍历每一列
                for col in sheet_df.columns:

                    # 去除空值 → 转为字符串 → 对每个单元格执行操作
                    sheet_df[col].dropna().astype(str).apply(
                        # 对单元格中的每个字符进行分类
                        lambda cell: [classify_char(char) for char in cell]
                    )

        except Exception as e:
            # 如果某个文件读取失败，打印错误信息并继续
            print(f"读取失败: {fname}, 错误信息: {e}")


# =========================
# 将分类后的字符写入 txt
# 使用 sorted() 让字符顺序固定
# =========================

with open(os.path.join(output_dir, "chinese.txt"), "w", encoding="utf-8") as f:
    f.write("".join(sorted(chinese)))

with open(os.path.join(output_dir, "numbers.txt"), "w", encoding="utf-8") as f:
    f.write("".join(sorted(numbers)))

with open(os.path.join(output_dir, "english.txt"), "w", encoding="utf-8") as f:
    f.write("".join(sorted(english)))

with open(os.path.join(output_dir, "others.txt"), "w", encoding="utf-8") as f:
    f.write("".join(sorted(others)))


# 程序结束提示
print("✅ 去重逐字拆分完成")
print("📁 输出目录:", output_dir)