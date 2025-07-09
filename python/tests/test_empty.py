import fastexcel_rw
import pytest

from utils import path_for_fixture


@pytest.mark.parametrize("path", ("empty.ods", "empty.xlsx"))
def test_empty(path: str) -> None:
    excel_reader = fastexcel_rw.read_excel(path_for_fixture(path))
    sheet = excel_reader.load_sheet_by_idx(0)

    assert sheet.to_pandas().empty
    assert sheet.to_polars().is_empty()
