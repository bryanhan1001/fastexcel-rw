
from datetime import date, datetime, timedelta

import pyarrow as pa

import fastexcel_rw

from utils import path_for_fixture


def test_eager_loading() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    sheet = excel_reader.load_sheet_eager(0)
    assert isinstance(sheet, pa.RecordBatch)


def test_lazy_loading() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    sheet = excel_reader.load_sheet(0)
    assert hasattr(sheet, "to_arrow")


def test_both_methods_are_equivalent() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    sheet_eager = excel_reader.load_sheet_eager(0)
    sheet_lazy = excel_reader.load_sheet(0).to_arrow()

    assert sheet_eager.equals(sheet_lazy)


def test_columns_are_not_applied_eagerly() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    # These should not do anything in an eager context
    sheet = excel_reader.load_sheet_eager(0)
    sheet_2 = excel_reader.load_sheet_eager(0, use_columns=[0, 1])

    assert sheet.equals(sheet_2)


def test_tables_are_eager_by_default() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture-tables.xlsx"))

    table = excel_reader.load_table("Table1")
    assert isinstance(table, pa.RecordBatch)
