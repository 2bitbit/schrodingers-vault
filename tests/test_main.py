# tests/test_main.py
from my_package import ThisREPO, NotesREPO
from main import main_workflow
import pytest  # 导入 pytest 以便使用 mocker
from unittest.mock import call  # 或者 from mocker import call


def test_main_workflow(mocker):
    """
    测试 main_workflow 是否以正确的顺序调用了各个方法。
    """
    # --- 步骤 1: 准备好所有 mock 对象，包括 manager ---
    # 创建 ThisREPO 和 NotesREPO 的 mock 对象
    mock_thisrepo = mocker.MagicMock(spec=ThisREPO)
    mock_notesrepo = mocker.MagicMock(spec=NotesREPO)

    # 创建一个 manager mock 来记录所有对 mock 对象的调用
    manager = mocker.Mock()

    # --- 步骤 2: 在调用工作流之前，将 mock 附加到 manager ---
    # 告诉 manager 开始监控这两个 mock
    manager.attach_mock(mock_thisrepo, "thisrepo")
    manager.attach_mock(mock_notesrepo, "notesrepo")

    # --- 步骤 3: 现在 manager 已经就位，开始调用主工作流 ---
    # manager 会在此时记录下所有对 mock_thisrepo 和 mock_notesrepo 的调用
    main_workflow(thisrepo=mock_thisrepo, notesrepo=mock_notesrepo)

    # --- 步骤 4: 定义预期的调用顺序并进行断言 ---
    # 定义预期的调用顺序
    expected_calls = [
        # 注意: mocker.call 是一个独立的工具，可以直接使用
        # 也可以写作 from unittest.mock import call
        call.notesrepo.save(),
        call.thisrepo.clean_old_zip(),
        call.notesrepo.compress(),
        call.thisrepo.save(),
        call.thisrepo.tag(),
        call.thisrepo.push_main(),
        call.thisrepo.push_tag(),
        call.thisrepo.release(),
    ]

    # 断言调用顺序
    assert manager.method_calls == expected_calls
