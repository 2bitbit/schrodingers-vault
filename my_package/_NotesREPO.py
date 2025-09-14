import subprocess
import os
import sys
import re
from ._config import NotesREPOConfig


class NotesREPO:
    def __init__(self, notesrepo_config: NotesREPOConfig | None = None):
        if not isinstance(notesrepo_config, (NotesREPOConfig, type(None))):
            raise TypeError("notesrepo_config must be an instance of NotesREPOConfig or None.")
        if notesrepo_config is None:
            notesrepo_config = NotesREPOConfig()
        self.config = notesrepo_config

    def save(self):
        print("对 NotesREPO 目录执行 git add")
        self._run_command(["git", "add", str(self.config.repo_dir)])

        print("对 NotesREPO 目录执行 git commit")
        self._run_command(["git", "commit", "-m", self.config.repo_commit_message])

    def compress(self):
        print("--- 开始压缩文件 ---")
        compress_command = [
            str(self.config.sevenzip_path),
            "a",  # 添加文件到压缩包 (Add)
            "-mx=9",  # 最高压缩等级 (Maximum)
            f"-p{os.getenv('password')}",  # 设置加密密码
            # "-mhe=on",  不对目录加密
            "-aoa",  # 覆盖所有已存在的文件 (All Overwrite All)
            str(self.config.output_path),  # 输出文件路径
            str(self.config.repo_dir),  # 要压缩的目标目录
            "-bsp1",  # 7z检测到听众是人采取行缓冲，是脚本采取块缓冲。我们强制使用行缓冲来实时监控输出。
        ]

        # 使用 Popen 实时获取输出
        process = subprocess.Popen(
            compress_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert process.stdout

        # 应对7z的进度条输出
        for line in process.stdout:
            if re.match(r" +\n", line):  # 遇到纯换行时，不打印任何内容，保持界面干净
                continue
            if re.match(r" *\d+%( \d+ U)?", line):
                sys.stdout.write("\r" + " " * 100 + "\r" + line.strip())
                sys.stdout.flush()
                continue
            else:
                sys.stdout.write(line)

        # 等待子进程执行完成，这样 returncode 才会被设置
        process.wait()
        # 获取最终的返回码
        if process.returncode != 0:
            raise Exception(f"\n错误: 命令执行失败，返回码: {process.returncode}，错误信息: {process.stderr}")
        else:
            print(f"文件已成功压缩到: {self.config.output_path}")

    def _run_command(self, command: list[str], check: bool = True):
        try:
            return subprocess.run(
                command,
                cwd=self.config.repo_dir,
                shell=True,
                capture_output=True,
                text=True,
                check=check,
            )
        except Exception as e:
            raise Exception(f"错误: 命令执行失败。错误信息: {e}")
