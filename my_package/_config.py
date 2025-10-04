from dataclasses import dataclass
from pathlib import Path
import datetime
# python_interpreter
PYTHON_INTERPRETER = '"D:/Software/Anaconda/envs/appdev/python.exe"'
# other_py_path
TREE_MAKE = '"d:/Workspace/Repos/tree_make/main.py"'

# THISREPO_CONFIG
THISREPO_DIR = Path(__file__).parent.parent
THISREPO_TAG_NAME = datetime.datetime.now().strftime("%Y-%m-%d")
THISREPO_COMMIT_MESSAGE = f'"release: {THISREPO_TAG_NAME}"'
THISREPO_REMOTE_NAME = "origin"

# NOTESREPO_CONFIG
NOTESREPO_DIR = Path("D:/Notes")
NOTESREPO_COMMIT_MESSAGE = f'"chore: Daily backup for {THISREPO_TAG_NAME}"'
SEVENZIP_PATH = Path("D:/Software/7-Zip/7z.exe")
ZIP_PATH = THISREPO_DIR / f"{THISREPO_TAG_NAME}.7z"


# CONFIGS
@dataclass
class ThisREPOConfig:
    repo_dir: Path = THISREPO_DIR
    repo_tag_name: str = THISREPO_TAG_NAME
    repo_commit_message: str = THISREPO_COMMIT_MESSAGE
    repo_remote_name: str = THISREPO_REMOTE_NAME
    zip_path: Path = ZIP_PATH


@dataclass
class NotesREPOConfig:
    repo_dir: Path = NOTESREPO_DIR
    repo_commit_message: str = NOTESREPO_COMMIT_MESSAGE
    sevenzip_path: Path = SEVENZIP_PATH
    output_path: Path = ZIP_PATH


# MISCELLANEOUS
@dataclass
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
