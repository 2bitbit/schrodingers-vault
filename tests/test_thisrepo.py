import pytest
from unittest.mock import MagicMock
import subprocess
from my_package import ThisREPO


@pytest.fixture
def thisrepo_instance(mock_configs, mocker):
    """
    创建一个 ThisREPO 的实例，并模拟所有 subprocess 调用。
    """
    # 模拟 subprocess.run
    mocker.patch("subprocess.run", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""))

    # 确保 ThisREPOConfig 使用的是最新的模拟配置
    return ThisREPO()


def test_save(thisrepo_instance):
    """测试 save 方法是否调用正确的 add,commit 命令。"""
    thisrepo_instance.save()
    subprocess.run.assert_any_call(
        ["git", "add", str(thisrepo_instance.config.repo_dir)],
        cwd=thisrepo_instance.config.repo_dir,
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run.assert_any_call(
        ["git", "commit", "-m", thisrepo_instance.config.repo_commit_message],
        cwd=thisrepo_instance.config.repo_dir,
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )


def test_clean_old_zip_exists(thisrepo_instance, mocker):
    """测试当旧的 zip 文件存在时，是否会调用删除方法。"""
    mock_path: MagicMock = mocker.patch("pathlib.Path.exists", return_value=True, autospec=True)
    mock_unlink: MagicMock = mocker.patch("pathlib.Path.unlink", autospec=True)
    zip_path_instance = thisrepo_instance.config.zip_path

    thisrepo_instance.clean_old_zip()

    # Path.exists 会被多次调用，我们只关心我们的 zip 路径
    assert any(call == mocker.call(zip_path_instance) for call in mock_path.call_args_list)
    mock_unlink.assert_called_once()


def test_clean_old_zip_not_exists(thisrepo_instance, mocker):
    """测试当旧的 zip 文件不存在时，是否会跳过删除。"""
    mocker.patch("pathlib.Path.exists", return_value=False)
    mock_unlink = mocker.patch("pathlib.Path.unlink", autospec=True)

    thisrepo_instance.clean_old_zip()

    mock_unlink.assert_not_called()


def test_tag(thisrepo_instance):
    """测试 tag 方法是否能正确处理标签已存在和不存在的情况。"""
    # 模拟第一次删除标签时失败（标签不存在）
    subprocess.run.return_value = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr='error: tag "tag-name" not found')

    thisrepo_instance.tag()

    # 检查调用
    assert subprocess.run.call_count == 2
    # 第一次是尝试删除
    subprocess.run.assert_any_call(
        ["git", "tag", "-d", thisrepo_instance.config.repo_tag_name],
        check=False,
        cwd=thisrepo_instance.config.repo_dir,
        shell=True,
        capture_output=True,
        text=True,
    )
    # 第二次是创建
    subprocess.run.assert_called_with(
        ["git", "tag", thisrepo_instance.config.repo_tag_name, "-a", "-m", thisrepo_instance.config.repo_commit_message],
        cwd=thisrepo_instance.config.repo_dir,
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )


def test_push_main(thisrepo_instance):
    """测试 push_main 方法。"""
    thisrepo_instance.push_main()
    subprocess.run.assert_called_once_with(
        ["git", "push", "--force-with-lease", thisrepo_instance.config.repo_remote_name, "main"],
        cwd=thisrepo_instance.config.repo_dir,
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )


def test_release(thisrepo_instance, capsys):
    """测试 release 方法是否打印出正确的 gh 命令。"""
    thisrepo_instance.release()
    captured = capsys.readouterr()

    expected_command = (
        'cd "'
        + str(thisrepo_instance.config.repo_dir)
        + '"'
        + f'&& gh release create "{thisrepo_instance.config.repo_tag_name}" "{thisrepo_instance.config.zip_path}" '
        + f'--title "Release {thisrepo_instance.config.repo_tag_name}" --notes ""'
    )

    assert expected_command in captured.out
