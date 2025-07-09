from __future__ import annotations

import pytest
from fastexcel_rw import (
    CannotRetrieveCellDataError,
    ColumnNotFoundError,
    InvalidParametersError,
    SheetNotFoundError,
    UnsupportedColumnTypeCombinationError,
)

from utils import path_for_fixture


def test_cannot_retrieve_data_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    # The following lines were used in tests but are now errors
    # since 0.8.0. This test is preserved to ensure that an error
    # is returned
    with pytest.raises(
        CannotRetrieveCellDataError,
        match="The requested sheet does not contain data, and was opened for exploration purposes only",
    ):
        excel_reader.load_sheet(
            0,
            n_rows=0,
        ).to_arrow()


def test_column_not_found_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    with pytest.raises(
        ColumnNotFoundError,
        match="Column 'NotExisting' not found",
    ):
        excel_reader.load_sheet(
            0,
            use_columns=["NotExisting"],
        )


def test_column_not_found_error_by_int() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    with pytest.raises(
        ColumnNotFoundError,
        match="Column '11' not found",
    ):
        excel_reader.load_sheet(
            0,
            use_columns=[11],
        )


def test_sheet_not_found_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    with pytest.raises(
        SheetNotFoundError,
        match="Sheet 'NotExisting' was not found",
    ):
        excel_reader.load_sheet("NotExisting")


def test_sheet_not_found_error_by_int() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    with pytest.raises(
        SheetNotFoundError,
        match="Sheet '40' was not found",
    ):
        excel_reader.load_sheet(40)


def test_invalid_parameters_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    with pytest.raises(
        InvalidParametersError,
        match="header_row can not be defined if column_names is provided",
    ):
        excel_reader.load_sheet(
            0,
            header_row=0,
            column_names=["test"],
        )


def test_unsupported_column_dtype_combination_error() -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture("fixture.xlsx"))

    with pytest.raises(
        UnsupportedColumnTypeCombinationError,
        match="Columns \\['int_col'\\] are using unsupported dtypes",
    ):
        excel_reader.load_sheet(
            0,
            dtypes={"int_col": "duration"},
        )
