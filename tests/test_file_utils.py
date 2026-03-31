import pytest
import os
import tempfile
from moto_ocr.file_utils import get_unique_filename


class TestGetUniqueFilename:
    def test_nonexistent_file_returns_original(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "new_file.xlsx")
            result = get_unique_filename(path)
            assert result == path

    def test_existing_file_gets_suffix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "file.xlsx")
            with open(path, "w") as f:
                f.write("test")
            
            result = get_unique_filename(path)
            assert result == os.path.join(tmpdir, "file1.xlsx")

    def test_multiple_conflicts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "file.xlsx")
            with open(base, "w") as f:
                f.write("test")
            with open(os.path.join(tmpdir, "file1.xlsx"), "w") as f:
                f.write("test")
            
            result = get_unique_filename(base)
            assert result == os.path.join(tmpdir, "file2.xlsx")

    def test_max_attempts_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base = os.path.join(tmpdir, "file.xlsx")
            # Create base file + all numbered variants
            with open(base, "w") as f:
                f.write("test")
            for i in range(1, 101):
                with open(os.path.join(tmpdir, f"file{i}.xlsx"), "w") as f:
                    f.write("test")
            
            with pytest.raises(RuntimeError, match="无法生成唯一文件名"):
                get_unique_filename(base, max_attempts=100)
