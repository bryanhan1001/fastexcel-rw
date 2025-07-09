import os
import tempfile
from pathlib import Path

import pytest

# Writer feature testing requires writer feature
pytest.importorskip("fastexcel_rw", reason="fastexcel_rw writer not available")

try:
    from fastexcel_rw import create_writer

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
            writer.close()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_write_simple_data(self):
        """测试写入简单数据"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            # 准备测试数据
            data = [["Alice", 25, True], ["Bob", 30, False], ["Charlie", 35, True]]
            headers = ["Name", "Age", "Active"]

            # 写入数据
            writer.write_sheet_data(data, "Sheet1", headers)
            writer.save()

            # 验证文件是否创建
            assert os.path.exists(tmp_path)
            assert os.path.getsize(tmp_path) > 0

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_write_multiple_sheets(self):
        """测试写入多个工作表"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            # 第一个工作表
            data1 = [["A", 1], ["B", 2]]
            writer.write_sheet_data(data1, "Sheet1", ["Letter", "Number"])

            # 第二个工作表
            data2 = [["X", 10], ["Y", 20]]
            writer.write_sheet_data(data2, "Sheet2", ["Letter", "Value"])

            writer.save()

            # 验证文件
            assert os.path.exists(tmp_path)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_write_different_data_types(self):
        """测试写入不同数据类型"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            writer = create_writer(tmp_path)

            # 包含不同数据类型的数据
            data = [["Text", 42, 3.14, True, None], ["Another", -10, 0.0, False, "Not None"]]
            headers = ["String", "Integer", "Float", "Boolean", "Nullable"]

            writer.write_sheet_data(data, "Mixed Types", headers)
            writer.save()

            assert os.path.exists(tmp_path)

        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    def test_path_object(self):
        """测试使用 Path 对象"""
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            writer = create_writer(tmp_path)

            data = [["Test", "Data"]]
            writer.write_sheet_data(data, "PathTest", ["Col1", "Col2"])
            writer.save()

            assert tmp_path.exists()

        finally:
            if tmp_path.exists():
                tmp_path.unlink()


@pytest.mark.skipif(WRITER_AVAILABLE, reason="Writer feature is available")
def test_writer_not_available():
    """测试在没有写入功能时的错误处理"""
    with pytest.raises(ImportError, match="Writing functionality is not available"):
        create_writer("test.xlsx")
