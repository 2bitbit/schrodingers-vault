# tests/conftest.py
import pytest
from pathlib import Path
from my_package import _config
import datetime

# 定义一个固定的日期，用于测试，以确保可重复性
FIXED_DATETIME = datetime.datetime(2025, 9, 13)
FIXED_TAG_NAME = FIXED_DATETIME.strftime("%Y-%m-%d")


@pytest.fixture
def mock_configs(monkeypatch, tmp_path):
    """
    Mock all configurations to use temporary paths and fixed dates.
    这个 fixture 会模拟所有在 _config.py 中定义的路径和动态变量。
    """

    # 1. 模拟 datetime
    class MockDateTime(datetime.datetime):
        @classmethod
        def now(cls, tz=None):
            return FIXED_DATETIME

    monkeypatch.setattr(datetime, "datetime", MockDateTime)

    # 2. 模拟路径
    # 使用 tmp_path 创建一个临时的、安全的文件系统结构
    thisrepo_dir = tmp_path / "ThisREPO"
    notesrepo_dir = tmp_path / "Notes"
    sevenzip_path = tmp_path / "7-Zip" / "7z.exe"
    zip_path = thisrepo_dir / f"{FIXED_TAG_NAME}.7z"

    thisrepo_dir.mkdir()
    notesrepo_dir.mkdir()
    sevenzip_path.parent.mkdir()
    sevenzip_path.touch()  # 创建一个空的 7z.exe 文件以通过检查

    # 3. 修改的必须是原模块中的对象，而不是import到我的命名空间的对象
    monkeypatch.setattr("my_package._init.THISREPO_DIR", thisrepo_dir)
    monkeypatch.setattr("my_package._init.NOTESREPO_DIR", notesrepo_dir)
    monkeypatch.setattr("my_package._init.SEVENZIP_PATH", sevenzip_path)
    monkeypatch.setattr("my_package._init.ZIP_PATH", zip_path)
    # 4. 返回模拟的路径以便在测试中断言
    return {
        "thisrepo_dir": thisrepo_dir,
        "notesrepo_dir": notesrepo_dir,
        "sevenzip_path": sevenzip_path,
        "zip_path": zip_path,
        "tag_name": FIXED_TAG_NAME,
    }
