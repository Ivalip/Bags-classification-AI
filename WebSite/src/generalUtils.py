from random import choice as rdch
import string
import os

def generateCode(length: int) -> str:
    # 62 symbols
    symbList = string.ascii_uppercase + string.ascii_lowercase + string.digits
    code = "".join(rdch(symbList) for _ in range(length))

    return code

def emptyFolder(folderpath: str):
    for i in os.listdir(folderpath):
        if os.path.isdir(f"{folderpath}/{i}"):
            emptyFolder(f"{folderpath}/{i}")
            os.rmdir(f"{folderpath}/{i}")
        else:
            os.remove(f"{folderpath}/{i}")