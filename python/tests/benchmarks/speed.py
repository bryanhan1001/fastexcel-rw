"""
Compare read performance with fastexcel, xlrd and different openpyxl options
"""

from __future__ import annotations

import fastexcel_rw
import pandas as pd
import polars as pl
import pytest

from utils import path_for_fixture


def fastexcel_read(file_path: str) -> pl.DataFrame:
    """Read Excel file using fastexcel_rw"""
    return fastexcel_rw.read_excel(file_path).load_sheet(0).to_polars()


def pd_read_excel(file_path: str) -> pd.DataFrame:
    """Read Excel file using pandas"""
    return pd.read_excel(file_path)


def pl_read_excel(file_path: str) -> pl.DataFrame:
    """Read Excel file using polars"""
    return pl.read_excel(file_path)


@pytest.fixture
def plain_data_xls():
    return "./python/tests/benchmarks/fixtures/plain_data.xls"


@pytest.fixture
def plain_data_xlsx():
    return "./python/tests/benchmarks/fixtures/plain_data.xlsx"


@pytest.fixture
def formula_xlsx():
    return "./python/tests/benchmarks/fixtures/formulas.xlsx"


@pytest.mark.benchmark(group="xlsx")
def test_pyxl(benchmark, plain_data_xlsx):
    benchmark(pyxl_read, plain_data_xlsx)


@pytest.mark.benchmark(group="xls")
def test_xlrd(benchmark, plain_data_xls):
    benchmark(xlrd_read, plain_data_xls)


@pytest.mark.benchmark(group="xls")
def test_fastexcel_xls(benchmark, plain_data_xls):
    benchmark(fastexcel_read, plain_data_xls)


@pytest.mark.benchmark(group="xlsx")
def test_fastexcel_xlsx(benchmark, plain_data_xlsx):
    benchmark(fastexcel_read, plain_data_xlsx)


@pytest.mark.benchmark(group="xlsx")
def test_pyxl_with_formulas(benchmark, formula_xlsx):
    benchmark(pyxl_read, formula_xlsx)


@pytest.mark.benchmark(group="xlsx")
def test_fastexcel_with_formulas(benchmark, formula_xlsx):
    benchmark(fastexcel_read, formula_xlsx)
