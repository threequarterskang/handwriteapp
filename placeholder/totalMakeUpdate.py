from pathlib import Path
from excel_to_sqlite import import_excel_with_partial_schema

WORKBOOK_PATH = Path(__file__).with_name("total.xlsx")
DATABASE_PATH = Path(__file__).with_name("total.db")
EXCEL_OBJECT_NAME = "total"
SQLITE_TABLE_NAME = "total"

COLUMN_TYPES = {
    "检验日期": "DATE",
    "数量": "INTEGER",
    "日期": "DATE"
}

DATE_COLUMNS = ["检验日期", "日期"]

if __name__ == "__main__":
    row_count, column_count = import_excel_with_partial_schema(
        WORKBOOK_PATH,
        DATABASE_PATH,
        EXCEL_OBJECT_NAME,
        SQLITE_TABLE_NAME,
        COLUMN_TYPES,
        date_columns=DATE_COLUMNS
    )

    print(
        f"Imported {row_count} rows and {column_count} columns "
        f"from {WORKBOOK_PATH.name}:{EXCEL_OBJECT_NAME} into {DATABASE_PATH.name}:{SQLITE_TABLE_NAME}."
    )