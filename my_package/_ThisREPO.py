import subprocess
from ._config import ThisREPOConfig, Colors
import re
import os


class ThisREPO:
    def __init__(self, thisrepo_config: ThisREPOConfig | None = None):
        if not isinstance(thisrepo_config, (ThisREPOConfig, type(None))):
            raise TypeError("thisrepo_config must be an instance of ThisREPOConfig or None.")
        if thisrepo_config is None:
            thisrepo_config = ThisREPOConfig()
        self.config = thisrepo_config

    def save(self):
        print("对 ThisREPO 目录执行 git add")
        self._run_command(f"git add {str(self.config.repo_dir)}")

        print("对 ThisREPO 目录执行 git commit")
        self._run_command(f"git commit -m {self.config.repo_commit_message}")

    def clean_repeated_zip(self):
        repeated_zip_path = self.config.zip_path
        if not repeated_zip_path.exists():
            print("未检测到当日旧的重复压缩文件，跳过清理。")
            return

        print("检查到旧的压缩文件，执行清理")
        try:
            repeated_zip_path.unlink()
        except Exception as e:
            raise Exception(f"错误: 无法删除旧文件 {repeated_zip_path}。错误信息: {e}")
        print(f"已删除已存在的旧文件: {repeated_zip_path}\n")

    def tag(self):
        print("对 ThisREPO 目录执行 git tag")
        # 如果标签已存在，先在本地删除它再重新创建
        p = self._run_command(
            f"git tag -d {self.config.repo_tag_name}",
            check=False,
        )
        if not re.search(r"error.*tag.*not found", p.stderr, re.IGNORECASE):
            print(f"检测到标签 {self.config.repo_tag_name} 已存在，删除完毕。")

        # 开始创建新标签
        self._run_command(f"git tag {self.config.repo_tag_name} -a -m {self.config.repo_commit_message}")
        print(f"标签 {self.config.repo_tag_name} 创建成功。")

    def push_main(self):
        print("对 ThisREPO main 分支执行 git push")
        self._run_command(f"git push --force-with-lease  {self.config.repo_remote_name} main")

    def push_tag(self):
        print("对 ThisREPO tag 执行 git push")
        p = self._run_command(
            f"git push -d {self.config.repo_remote_name} {self.config.repo_tag_name}",
            check=False,
        )
        if "error: failed to push some refs" not in p.stderr:
            print(f"远程仓库中标签 {self.config.repo_tag_name} 已经存在，执行删除。")

        self._run_command(f"git push {self.config.repo_remote_name} {self.config.repo_tag_name}")
        print(f"标签{self.config.repo_tag_name}已成功推送到远程仓库{self.config.repo_remote_name}。")

    def release(self):
        print(f"\n--- 准备在 GitHub 上创建 Release {self.config.repo_tag_name} 并上传压缩包 ---")
        is_external_terminal = True
        for k, v in os.environ.items():
            if "term" in k.lower():
                print(f"发现环境变量:{k}={v} ")
                is_external_terminal = False
        if not is_external_terminal:
            print(f"{Colors.RED}{Colors.BOLD}此步骤极度不建议在集成终端中进行！请新建单独的终端执行！! !{Colors.RESET}")
        print(
            "请在非集成终端，执行: "
            + f'cd "{str(self.config.repo_dir)}"'
            + f'&& gh release create "{self.config.repo_tag_name}" "{self.config.zip_path}" '
            + f'--title "Release {self.config.repo_tag_name}" --notes ""'
        )
        print("并打开网络监视器确定网速不慢，耐心等待")

    def _run_command(self, command: str, check: bool = True):
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
