import os
import tempfile
from pathlib import Path

import pytest

# Writer feature testing requires writer feature
pytest.importorskip("fastexcel_rw", reason="fastexcel_rw writer not available")

try:
    from fastexcel_rw import create_writer, read_excel

    WRITER_AVAILABLE = True
except ImportError:
    WRITER_AVAILABLE = False


@pytest.mark.skipif(not WRITER_AVAILABLE, reason="Writer feature not available")
class TestExcelWriter:
    """Test Excel writing functionality"""

    def test_create_writer(self):
        """Test creating writer"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)
            assert writer is not None
            assert writer.is_open()
            assert writer.file_path == tmp_path
            writer.close()
            assert not writer.is_open()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_write_simple_data(self):
        """Test writing simple data and verify content"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            # Prepare test data
            data = [["Alice", 25, True], ["Bob", 30, False], ["Charlie", 35, True]]
            headers = ["Name", "Age", "Active"]

            # Write data
            writer.write_sheet_data(data, "Sheet1", headers)
            writer.save()

            # Verify file was created
            assert os.path.exists(tmp_path)
            assert os.path.getsize(tmp_path) > 0

            # Read back and verify content
            excel_reader = read_excel(tmp_path)
            assert excel_reader.sheet_names == ["Sheet1"]

            sheet = excel_reader.load_sheet(0)
            df = sheet.to_pandas()

            # Verify headers
            assert list(df.columns) == ["Name", "Age", "Active"]

            # Verify data
            assert df["Name"].tolist() == ["Alice", "Bob", "Charlie"]
            assert df["Age"].tolist() == [25.0, 30.0, 35.0]
            assert df["Active"].tolist() == [True, False, True]

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_write_multiple_sheets(self):
        """Test writing multiple worksheets and verify content"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            # First worksheet
            data1 = [["A", 1], ["B", 2]]
            writer.write_sheet_data(data1, "Sheet1", ["Letter", "Number"])

            # Second worksheet
            data2 = [["X", 10], ["Y", 20]]
            writer.write_sheet_data(data2, "Sheet2", ["Letter", "Value"])

            writer.save()

            # Verify file
            assert os.path.exists(tmp_path)

            # Read back and verify content
            excel_reader = read_excel(tmp_path)
            assert excel_reader.sheet_names == ["Sheet1", "Sheet2"]

            # Verify Sheet1
            sheet1 = excel_reader.load_sheet(0)
            df1 = sheet1.to_pandas()
            assert list(df1.columns) == ["Letter", "Number"]
            assert df1["Letter"].tolist() == ["A", "B"]
            assert df1["Number"].tolist() == [1.0, 2.0]

            # Verify Sheet2
            sheet2 = excel_reader.load_sheet(1)
            df2 = sheet2.to_pandas()
            assert list(df2.columns) == ["Letter", "Value"]
            assert df2["Letter"].tolist() == ["X", "Y"]
            assert df2["Value"].tolist() == [10.0, 20.0]

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_write_different_data_types(self):
        """Test writing different data types and verify content"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            # Data with different types
            data = [["Text", 42, 3.14, True, None], ["Another", -10, 0.0, False, "Not None"]]
            headers = ["String", "Integer", "Float", "Boolean", "Nullable"]

            writer.write_sheet_data(data, "Mixed Types", headers)
            writer.save()

            assert os.path.exists(tmp_path)

            # Read back and verify
            excel_reader = read_excel(tmp_path)
            sheet = excel_reader.load_sheet(0)
            df = sheet.to_pandas()

            # Verify headers
            assert list(df.columns) == ["String", "Integer", "Float", "Boolean", "Nullable"]

            # Verify data types and values
            assert df["String"].tolist() == ["Text", "Another"]
            assert df["Integer"].tolist() == [42.0, -10.0]
            assert df["Float"].tolist() == [3.14, 0.0]
            assert df["Boolean"].tolist() == [True, False]
            # None becomes NaN, "Not None" stays as string
            import pandas as pd

            assert pd.isna(df["Nullable"].iloc[0])
            assert df["Nullable"].iloc[1] == "Not None"

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_path_object(self):
        """Test using Path object"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            writer = create_writer(tmp_path)

            data = [["Test", "Data"]]
            writer.write_sheet_data(data, "PathTest", ["Col1", "Col2"])
            writer.save()

            assert tmp_path.exists()

            # Read back and verify
            excel_reader = read_excel(tmp_path)
            sheet = excel_reader.load_sheet(0)
            df = sheet.to_pandas()
            assert list(df.columns) == ["Col1", "Col2"]
            assert df["Col1"].tolist() == ["Test"]
            assert df["Col2"].tolist() == ["Data"]

        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    def test_sheet_names_property(self):
        """Test sheet_names getter"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)
            assert writer.sheet_names == []

            writer.write_sheet_data([["A", 1]], "FirstSheet", ["Col1", "Col2"])
            assert writer.sheet_names == ["FirstSheet"]

            writer.write_sheet_data([["B", 2]], "SecondSheet", ["Col1", "Col2"])
            assert writer.sheet_names == ["FirstSheet", "SecondSheet"]

            writer.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_empty_data_error(self):
        """Test that empty data raises error"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            with pytest.raises(ValueError, match="Data cannot be empty"):
                writer.write_sheet_data([], "Sheet1", ["Col1"])

            writer.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_empty_sheet_name_error(self):
        """Test that empty sheet name raises error"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            with pytest.raises(ValueError, match="Sheet name cannot be empty"):
                writer.write_sheet_data([["A", 1]], "", ["Col1"])

            writer.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_duplicate_sheet_name_error(self):
        """Test that duplicate sheet names raise error"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            writer.write_sheet_data([["A", 1]], "Sheet1", ["Col1"])

            with pytest.raises(ValueError, match="Sheet 'Sheet1' already exists"):
                writer.write_sheet_data([["B", 2]], "Sheet1", ["Col1"])

            writer.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_empty_headers_error(self):
        """Test that empty headers list raises error"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            with pytest.raises(ValueError, match="Headers list cannot be empty if provided"):
                writer.write_sheet_data([["A", 1]], "Sheet1", [])

            writer.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)


@pytest.mark.skipif(WRITER_AVAILABLE, reason="Writer feature is available")
def test_writer_not_available():
    """Test error handling when writer feature is not available"""
    with pytest.raises(ImportError, match="Writing functionality is not available"):
        create_writer("test.xlsx")
