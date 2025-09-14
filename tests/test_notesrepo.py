# tests/test_notesrepo.py
import pytest
import subprocess
import io
from my_package import NotesREPO


@pytest.fixture
def notesrepo_instance(mock_configs, monkeypatch, mocker):
    """创建一个 NotesREPO 的实例，并模拟相关依赖。"""
    # 模拟环境变量
    monkeypatch.setenv("password", "test_password")

    # 模拟 subprocess.run 用于 add 和 commit
    mocker.patch("subprocess.run", return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="", stderr=""))

    # 模拟 subprocess.Popen 用于 compress
    mock_popen = mocker.MagicMock()
    mock_popen.stdout = io.StringIO(" 50%\n 100% U\nAll OK\n")  # 模拟7z输出
    mock_popen.returncode = 0
    mocker.patch("subprocess.Popen", return_value=mock_popen)

    return NotesREPO()


def test_save(notesrepo_instance):
    """测试 save 方法。"""
    notesrepo_instance.save()
    subprocess.run.assert_any_call(
        ["git", "add", str(notesrepo_instance.config.repo_dir)],
        cwd=notesrepo_instance.config.repo_dir,
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )

    subprocess.run.assert_any_call(
        ["git", "commit", "-m", notesrepo_instance.config.repo_commit_message],
        cwd=notesrepo_instance.config.repo_dir,
        shell=True,
        capture_output=True,
        text=True,
        check=True,
    )


def test_compress_success(notesrepo_instance, capsys):
    """测试 compress 方法在成功时的情况。"""
    notesrepo_instance.compress()

    # 检查 Popen 是否以正确的参数被调用
    expected_command = [
        str(notesrepo_instance.config.sevenzip_path),
        "a",
        "-mx=9",
        "-ptest_password",
        "-aoa",
        str(notesrepo_instance.config.output_path),
        str(notesrepo_instance.config.repo_dir),
        "-bsp1",
    ]
    subprocess.Popen.assert_called_once_with(
        expected_command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    # 检查输出
    captured = capsys.readouterr()
    assert "All OK" in captured.out
    assert f"文件已成功压缩到: {notesrepo_instance.config.output_path}" in captured.out


def test_compress_failure(notesrepo_instance, mocker):
    """测试 compress 方法在 7z 返回错误码时抛出异常。"""
    # 覆盖 fixture 中的 Popen 模拟，使其返回错误码
    mock_popen = mocker.MagicMock()
    mock_popen.stdout = io.StringIO("ERROR: Cannot open file\n")
    mock_popen.returncode = 2  # 7-zip 的致命错误码
    mocker.patch("subprocess.Popen", return_value=mock_popen)

    with pytest.raises(Exception, match="错误: 命令执行失败，返回码: 2"):
        notesrepo_instance.compress()
