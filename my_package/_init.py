from ._config import SEVENZIP_PATH, THISREPO_DIR, NOTESREPO_DIR, ZIP_PATH
from dotenv import load_dotenv  # 用于__init__.py中调用


def is_env_ok():
    sevenzip_path = SEVENZIP_PATH
    zip_path = ZIP_PATH
    dirs = [THISREPO_DIR, NOTESREPO_DIR]

    for p in dirs:
        if not p.is_dir():
            raise Exception(f"错误: {p}不存在或不是目录，请检查 _config.py 文件。")
    if not (sevenzip_path.is_file() and sevenzip_path.suffix == ".exe"):
        raise Exception(f"错误: {sevenzip_path}不存在或不是可执行文件，请检查 _config.py 文件")
    if not (zip_path.suffix == ".7z"):
        raise Exception(f"错误：{zip_path}不是一个7z文件，请检查 _config.py 文件")
    if not (THISREPO_DIR / ".env").exists():
        raise FileNotFoundError("错误: 项目根目录中不存在 '.env' 文件。")

    return True
