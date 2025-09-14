from . import _init

if _init.is_env_ok():
    _init.load_dotenv()
    from ._ThisREPO import ThisREPO
    from ._NotesREPO import NotesREPO
else:
    raise Exception("Environment not OK.")
