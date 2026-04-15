from pathlib import Path
from excel_to_sqlite import import_excel_with_partial_schema

WORKBOOK_PATH = Path(__file__).with_name("placeholder.xlsx")
DATABASE_PATH = Path(__file__).with_name("placeholder.db")
EXCEL_OBJECT_NAME = "field_rule"
SQLITE_TABLE_NAME = "field_rule"

COLUMN_TYPES = {
    "数值列": "INTEGER",
    "数据最大范围": "INTEGER"
}

DATE_COLUMNS = [""]

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