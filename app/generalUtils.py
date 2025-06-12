from random import choice as rdch
import string
import os
import mimetypes
from werkzeug.utils import secure_filename
from icecream import ic
import subprocess
import sys

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

def allowed_file(filename, exts):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in exts


def save_file(code, type, uploaded_file, base_upload_path, allowed_exts):
    """Сохраняет файл в temp/<code>/<type>/ с оригинальным расширением или по mimetype"""
    # Получение пути директории сохранения
    upload_dir = os.path.join(base_upload_path, code, type)
    # Создание директории сохранения
    os.makedirs(upload_dir, exist_ok=True)
    # Преобразование название файла в допустимый для файловой системы
    original_name = secure_filename(uploaded_file.filename)
    # Разделение имени файла и его разрешения
    name, ext = os.path.splitext(original_name)
    # Если разрешение файла отсутствует
    if not ext:
        # Попытка получить расширение из mimetype
        guessed = mimetypes.guess_extension(uploaded_file.mimetype) or ''
        ext = guessed
    # Соединение названия файла и разрешения
    filename = f"{name}{ext}"

    if not allowed_file(filename, allowed_exts):
        return None
    # Получение пути файла сохранения
    path = os.path.join(upload_dir, filename)
    # Сохранение файла по пути
    uploaded_file.save(path)
    if type == "image":
        code = f'''
import cv2
img = cv2.imread("{path}")
print("IMG IS", img is not None)
'''
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True
        )
        
        stderr = result.stderr.strip()
        stdout = result.stdout.strip()

        # Corrupt JPEG data: premature end of data segment
        # Invalid SOS parameters for sequential JPEG
        # WARNING ⚠️ Image Read Error E:\Documents\# Projects\Bags-classification-AI\app\temp\53Jqi\image\20250526_075840.jpg

        # is_valid = "IMG IS True" in stdout and "Invalid SOS" not in stderr
        # is_valid = "IMG IS True" in stdout and len(stderr)==0
        if len(stderr)!=0:
            ic(stdout)
            ic(stderr)
            return None


    # Возврат название файла 
    return filename
