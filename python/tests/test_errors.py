from __future__ import annotations

import fastexcel_rw
import pytest
from fastexcel_rw import (
    ColumnNotFoundError,
    InvalidParametersError,
    SheetNotFoundError,
    UnsupportedColumnTypeCombinationError,
)

from utils import path_for_fixture

# test_cannot_retrieve_data_error was removed as this error type is no longer raised in
# current version


def test_column_not_found_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture-single-sheet.xlsx"))

    with pytest.raises(
        ColumnNotFoundError,
        match='column with name "NotExisting" not found',
    ):
        excel_reader.load_sheet(
            0,
            use_columns=["NotExisting"],
        )


def test_column_not_found_error_by_int() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture-single-sheet.xlsx"))

    with pytest.raises(
        ColumnNotFoundError,
        match="column at index 11 not found",
    ):
        excel_reader.load_sheet(
            0,
            use_columns=[11],
        )


def test_sheet_not_found_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture-single-sheet.xlsx"))

    with pytest.raises(
        SheetNotFoundError,
        match='sheet with name "NotExisting" not found',
    ):
        excel_reader.load_sheet("NotExisting")


def test_sheet_not_found_error_by_int() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture-single-sheet.xlsx"))

    with pytest.raises(
        SheetNotFoundError,
        match="sheet at index 40 not found",
    ):
        excel_reader.load_sheet(40)


def test_invalid_parameters_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture-single-sheet.xlsx"))

    with pytest.raises(
        InvalidParametersError,
        match="Too many rows skipped. Max height is 3",
    ):
        excel_reader.load_sheet(
            0,
            skip_rows=1000000,
            header_row=None,
            column_names=["Month", "Year"],
        )


def test_unsupported_column_dtype_combination_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture-multi-dtypes-columns.xlsx"))

    with pytest.raises(
        UnsupportedColumnTypeCombinationError,
        match="type coercion is strict",
    ):
        excel_reader.load_sheet(
            0,
            dtype_coercion="strict",
        )
