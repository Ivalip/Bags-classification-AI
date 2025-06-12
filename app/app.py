#!/usr/bin/env python
# -*- coding: utf-8 -*-
from icecream import ic
ic("============ App restarted =============")
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
import logging as Log
# -------------------------------------------------------------
from generalUtils import generateCode, emptyFolder, save_file
from aiPredict import Scanner
scanner = Scanner()
# ---------------------------------
app = Flask(__name__)
app.config['BASE_UPLOAD_PATH'] = 'temp'
# Максимальный размер запроса: 500 МБ
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# Очистим папку при старте
os.makedirs(app.config['BASE_UPLOAD_PATH'], exist_ok=True)
emptyFolder(app.config['BASE_UPLOAD_PATH'])
Log.basicConfig(level=Log.INFO, filename="py_log.log", filemode="w",
                format="%(asctime)s %(levelname)s %(message)s")

# Константы
CODE_SIZE = 5

@app.route('/', methods=['GET'])
def get_code():
    """Генерация нового кода и создание папок"""
    while True:
        # Генерация кода доступа
        gen_code = generateCode(CODE_SIZE)
        # Создание пути директории нового пользователя
        base_dir = os.path.join(app.config['BASE_UPLOAD_PATH'], gen_code)
        # Если директория с этим кодом не существует, то выходим из цикла
        if (not os.path.exists(base_dir)): break
    ic("GET Message for Code", gen_code)
    # Создание директории для изображений пользователя
    os.makedirs(os.path.join(base_dir, 'image'), exist_ok=True)
    # Создание директории для видео пользователя
    os.makedirs(os.path.join(base_dir, 'video'), exist_ok=True)
    # Возврат кода клиенту в формате JSON
    return jsonify(code=gen_code)


@app.route('/<code>/<type>', methods=['POST'])
def post_media(code, type):
    """Загрузка файла"""
    ic(f"Upload {type} for code:", code)
    Log.info(f"Upload video for code: {code}")
    Log.info(f"request.files keys: {list(request.files.keys())}")

    # Проверка на правильность пути обращения
    if type not in ["image", "video"]:
        ic("POST", "Wrong PATH", type)
        return jsonify(error="Wrong PATH"), 400

    # Словарь доступных разрешений файлов
    acceptable_extension = {
        "image" : {'jpg', 'jpeg', 'png', 'bmp'},
        "video" : {'mp4', 'avi', 'mov', 'mkv'}
    }

    # -------------------------------------------
    # Получение директории пользователя с кодом
    base_dir= os.path.join(app.config['BASE_UPLOAD_PATH'], code)

    # Если директорией с данным кодом не существует
    if not os.path.isdir(base_dir):
        ic("POST", "Please generate new code")
        # Возврат ошибку отсутствия в формате JSON
        return jsonify(error="Invalid code"), 404

    # Если файла не существует в запросе GET
    if 'file' not in request.files:
        return jsonify(error="No file part"), 400

    # Получение файла
    # uploaded_file = request.files.get('file') or request.files.get(type)
    # uploaded_file = request.files['file']
    uploaded_file = request.files.get('file')


    # Проверка, что имя файла не пустой
    if uploaded_file.filename == '':
        return jsonify(error="Empty filename"), 400

    # Проверка, что объект файла не None
    if uploaded_file is None:
        # Возврат ошибки
        ic("POST", "No file part")
        return jsonify(error="No file part"), 400

    # Если у файла нет имени
    if uploaded_file.filename == '':
        # Возврат ошибки
        ic("POST", "No selected file")
        return jsonify(error="No selected file"), 400

    # Если файл не является изображением
    if not uploaded_file.mimetype.startswith(f'{type}/'):
        # Возврат ошибки
        ic("POST", "Unsupported type", type)
        return jsonify(error=f"Unsupported {type} type"), 415

    Log.info(f"Received filename: {uploaded_file.filename}, mimetype: {uploaded_file.mimetype}")
    saved_filename = save_file(code, type, uploaded_file, app.config['BASE_UPLOAD_PATH'], acceptable_extension[type])

    if saved_filename is None:
        ic("Image corrupted")
        return jsonify(error=f"Image corrupted"), 415

    # Запуск сканирования файла
    filepath = os.path.join(base_dir, type)
    ic("Scanning started for ", filepath)

    scanner.scan(code, filepath, type)

    ic("POST", "ok", saved_filename, uploaded_file.mimetype)
    return jsonify(status="ok", filename=saved_filename, mimetype=uploaded_file.mimetype), 201
    # -------------------------------------------

# @app.route('/<code>/<type>', methods=['GET'])
# def get_media_info(code, type):
#     # Получение директории пользователя по коду
#     media_dir = os.path.join(app.config['BASE_UPLOAD_PATH'], code, type)
#     # Если этой директории не существует
#     if not os.path.isdir(media_dir):
#         # Возврат ошибки
#         return jsonify(error=f"No {type} directory"), 404
#     # Получение списка файлов директории
#     files = os.listdir(media_dir)
#     # Возврат списка в JSON формате
#     return jsonify(type=files)


@app.route('/<code>', methods=['GET'])
def get_status(code):
    """Возвращает список загруженных изображений и видео"""
    # Получение пути директории пользователя с кодом
    base_dir = os.path.join(app.config['BASE_UPLOAD_PATH'], code)
    # Если этой директории не существует
    if not os.path.isdir(base_dir):
        # Возврат ошибку отсутствия в формате JSON
        return jsonify(error="Code not found"), 404
    # Иначе: получение списков изображений и видео
    images = os.listdir(os.path.join(base_dir, 'image'))
    videos = os.listdir(os.path.join(base_dir, 'video'))
    # Возврат списков изображений и видео
    ic("GET Message for status", images, videos)
    
    res = scanner.get_prediction(code)
    ic("Prediction:",res)
    # stats = {"handbags": res["Пакет"], "handbags": res["Сумка"], "suitcases": res["Чемодан"], "backpacks": res["Рюкзак"]}
    # if isinstance(res, dict):
    #     ic("is dict")
    #     return jsonify(stats)
    return jsonify(res)
    # Возврат подсчета сумок
    # return jsonify(images=images, videos=videos)


@app.route('/<code>/download', methods=['GET'])
def download_latest(code):
    base = os.path.join(app.config['BASE_UPLOAD_PATH'], code)
    if not os.path.isdir(base):
        return jsonify(error="Invalid code"), 404

    all_files = []
    for sub in ('images', 'videos'):
        d = os.path.join(base, sub)
        if os.path.isdir(d):
            for fn in os.listdir(d):
                path = os.path.join(d, fn)
                all_files.append((path, os.path.getmtime(path)))

    if not all_files:
        return jsonify(error="No uploads"), 404
    latest, _ = max(all_files, key=lambda x: x[1])
    folder, fn = os.path.split(latest)

    return send_from_directory(folder, fn, as_attachment=False)


@app.route('/test')
def upload_page():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')





# @app.route('/<code>/image', methods=['POST'])
# def post_image(code):
#     """Загрузка изображения"""
#     Log.info(f"Upload image for code: {code}")
#     ic("Upload image for code", code)

#     Log.info(f"request.files keys: {list(request.files.keys())}")

#     # Получение директории пользователя с кодом
#     base_dir = os.path.join(app.config['BASE_UPLOAD_PATH'], code)
#     if not os.path.isdir(base_dir):
#         # Возврат ошибку отсутствия в формате JSON
#         return jsonify(error="Please generate new code"), 400

#     # Получение файла по запросу GET
#     f = request.files.get('file') or request.files.get('image')
#     # Если файла не существует в запросе GET
#     if f is None:
#         # Возврат ошибки
#         return jsonify(error="No file part"), 400

#     Log.info(f"Received filename: {f.filename}, mimetype: {f.mimetype}")

#     # Если у файла нет имени
#     if f.filename == '':
#         # Возврат ошибки
#         return jsonify(error="No selected file"), 400

#     # Если файл не является изображением
#     if not f.mimetype.startswith('image/'):
#         # Возврат ошибки
#         return jsonify(error="Unsupported image type"), 415

#     # Сохранение файла в директорию пользователя с кодом
#     filename = save_file(code, 'images', f)
#     # Возврат ответа в JSON-формате
#     return jsonify(status="ok", filename=filename, mimetype=f.mimetype), 201


# @app.route('/<code>/video', methods=['POST'])
# def post_video(code):
#     """Загрузка видео"""
#     Log.info(f"Upload video for code: {code}")
#     Log.info(f"request.files keys: {list(request.files.keys())}")

#     base_dir = os.path.join(app.config['BASE_UPLOAD_PATH'], code)
#     if not os.path.isdir(base_dir):
#         return jsonify(error="Please generate new code"), 400

#     f = request.files.get('file') or request.files.get('video')
#     if f is None:
#         return jsonify(error="No file part"), 400

#     Log.info(f"Received filename: {f.filename}, mimetype: {f.mimetype}")
#     if f.filename == '':
#         return jsonify(error="No selected file"), 400
#     if not f.mimetype.startswith('video/'):
#         return jsonify(error="Unsupported video type"), 415

#     filename = save_file(code, 'video', f)
#     return jsonify(status="ok", filename=filename, mimetype=f.mimetype), 201



# @app.route('/<code>/image', methods=['GET'])
# def get_image_info(code):
#     images_dir = os.path.join(app.config['BASE_UPLOAD_PATH'], code, 'images')
#     if not os.path.isdir(images_dir):
#         return jsonify(error="No images directory"), 404
#     files = os.listdir(images_dir)
#     ic(files)
#     results = model(os.path.join(images_dir, files[-1]))
#     # res = ""
#     for r in results:
#         # for c in r.boxes.cls:
#         #     res = model.names[int(c)]
#         # print(res)
#         words_array = [(model.names[i.cls.item()], i.conf.item()) for i in r.boxes]
#         print(*words_array)
#         res = words_array
#         r.save(filename=f'temp/{code}/images/labeled.jpg')

#     return jsonify(images=files)


# @app.route('/<code>/video', methods=['GET'])
# def get_video_info(code):
#     videos_dir = os.path.join(app.config['BASE_UPLOAD_PATH'], code, 'videos')
#     if not os.path.isdir(videos_dir):
#         return jsonify(error="No videos directory"), 404
#     files = os.listdir(videos_dir)
#     return jsonify(videos=files)
