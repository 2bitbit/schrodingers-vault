import pytest
from unittest.mock import MagicMock
from pathlib import Path
import sys
import importlib
from my_package import _init
import re


def test_is_env_ok_success(mock_configs):
    """
    测试 is_env_ok 在环境配置正确时能成功返回 True。
    """
    # 创建 .env 文件
    (mock_configs["thisrepo_dir"] / ".env").touch()

    assert _init.is_env_ok() is True


def test_is_env_ok_raises_error_if_dir_missing(mock_configs, mocker):
    """
    测试当目录不存在时 is_env_ok 抛出异常。
    """
    original_is_dir = Path.is_dir

    # 定义一个 side_effect 函数，实现精确控制
    def custom_is_dir(path_instance: Path):
        print(f"dealing with {path_instance}")
        # 只让我们关心的 notesrepo_dir 返回 False
        if str(path_instance) == str(mock_configs["notesrepo_dir"]):
            print(f"Mocking: Path('{path_instance}').is_dir() -> False")
            return False

        print(f"Calling original is_dir for: '{path_instance}'")
        return original_is_dir(path_instance)

    # 使用 mocker.patch 和 side_effect 来应用我们的精确逻辑
    mocker.patch("pathlib.Path.is_dir", side_effect=custom_is_dir, autospec=True)

    # 准备预期的错误消息
    expected_msg = f".*{re.escape(str(mock_configs['notesrepo_dir']))}不存在或不是目录.*"
    print(f"mlgb{expected_msg}")
    with pytest.raises(Exception, match=expected_msg):
        _init.is_env_ok()


def test_is_env_ok_raises_error_if_7z_missing(mock_configs, mocker):
    """
    测试当 7z.exe 不存在时 is_env_ok 抛出异常。
    """
    original_is_file = Path.is_file

    # 模拟 7z.exe 不是文件的情况
    # 定义一个 side_effect 函数，实现精确控制
    def custom_is_file(path_instance: Path):
        # 只让我们关心的 sevenzip_path 返回 False
        print(f"dealing with {path_instance}")
        if path_instance == mock_configs["sevenzip_path"]:
            print(f"Mocking: Path('{path_instance}').is_file() -> False")
            return False
        # 其他所有 is_file 调用都返回 True，避免干扰
        print(f"Calling original is_file for: '{path_instance}'")
        return original_is_file(path_instance)

    mocker.patch("pathlib.Path.is_file", side_effect=custom_is_file, autospec=True)

    expected_msg = f".*{re.escape(str(mock_configs['sevenzip_path']))}不存在或不是可执行文件.*"
    with pytest.raises(Exception, match=expected_msg):
        _init.is_env_ok()


def test_is_env_ok_raises_error_with_precise_mock(mock_configs, mocker):
    """
    测试当 .env 文件不存在时抛出异常，且不影响其他路径检查。
    """
    # 1. 保存原始的 exists 方法
    original_exists = Path.exists

    # 2. 定义我们的 side_effect 函数
    def custom_exists(path_instance: Path):
        # 3. 检查是不是我们想 mock 的那个特定路径
        #    用 str(path_instance) 或者 path_instance.resolve() 来获取完整路径字符串进行比较
        if path_instance.name == ".env":
            print(f"Mocking: Path('{path_instance}').exists() -> False")
            return False
        # 4. 如果是其他路径，则调用原始的、真正的 exists 方法
        print(f"Calling original exists for: '{path_instance}'")
        return original_exists(path_instance)

    # 5. 使用 side_effect 来应用我们的自定义逻辑
    mocker.patch("pathlib.Path.exists", side_effect=custom_exists, autospec=True)

    # --- 测试逻辑开始 ---
    # is_env_ok 内部检查 .env 时，会调用 custom_exists 并返回 False
    with pytest.raises(FileNotFoundError, match=".*不存在.*env.*"):
        _init.is_env_ok()

    # --- 验证我们的 mock 没有“误伤” ---
    # 我们可以验证一下，对其他真实存在的文件的检查不会受影响
    # 比如，检查一下你的测试文件本身，它肯定是存在的
    test_file = Path(__file__)
    assert test_file.exists() == True  # 这里会调用 original_exists，返回正确结果


def test_package_init_raises_exception_when_env_not_ok(mocker):
    """
    测试当环境检查失败时，导入 my_package 包抛出异常。
    """
    # 模拟环境检查失败
    mocker.patch("my_package._init.is_env_ok", side_effect=Exception("Env check failed"))

    # 因为 my_package 可能已经被导入，需要重新加载，才能触发is_env_ok的检查
    with pytest.raises(Exception, match="Env check failed"):
        importlib.reload(sys.modules["my_package"])

    # pytest 和 mocker 会在每个测试函数结束后自动清理环境和 mock
