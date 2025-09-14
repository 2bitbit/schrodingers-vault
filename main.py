from my_package import ThisREPO, NotesREPO
from main_workflow import main_workflow

if __name__ == "__main__":
    thisrepo_implementation = ThisREPO()
    notesrepo_implementation = NotesREPO()

    print("--- 开始执行工作流 ---")
    main_workflow(
        thisrepo=thisrepo_implementation,
        notesrepo=notesrepo_implementation,
    )
    print("--- 工作流执行完毕 ---")
