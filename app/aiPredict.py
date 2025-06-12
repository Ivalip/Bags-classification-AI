import os
import cv2
from icecream import ic
from concurrent.futures import ThreadPoolExecutor, as_completed
# --------- Import YOLO -----------
from ultralytics import YOLO, solutions
ic("ultralytics has been imported")

class Scanner():
    def __init__(self):
        self.model_path = 'models/20250610_205550_yolo11m_reducedBoxSize08.pt'
        self.model = YOLO(self.model_path)
        ic("YOLO model have been imported")
        # Создаём пул потоков
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.pool = {}
    # POST-signal scan
    def scan(self, code, file_path, type):
        if type == "image":
            ic("image scanning", file_path)
            self.pool[code] = self.executor.submit(self.scan_image, file_path)
            return f"Image have been scanned"
        elif type == "video":
            ic("video scanning")
            self.pool[code] = self.executor.submit(self.scan_video, file_path)
            return f"Video have been scanned"
        else:
            ic("file is not image nor video")
            return "file is not image nor video"
    # GET-signal get_prediction
    def get_prediction(self, code):
        if code not in self.pool:
            return "This code doesn't exist: Prediction have been made or haven't been made before"
        if not self.pool[code].done():
            return "Scanning still going"
        result = self.pool[code].result()
        del self.pool[code]
        return result
    def scan_image(self, file_path):
        # TODO: complete this method
        filename = os.listdir(file_path)[-1]
        results = self.model(os.path.join(file_path, filename))
        res = ""
        for r in results:
            # for c in r.boxes.cls:
            #     res = model.names[int(c)]
            # print(res)
            words_array = [(self.model.names[i.cls.item()], i.conf.item()) for i in r.boxes]
            # print(*words_array)
            res = words_array
            r.save(filename=f'{file_path}/{filename}_labeled.jpg')
        ic(res)
        return res
    def scan_video(self, file_path):
        filename = os.listdir(file_path)[-1]
        cap = cv2.VideoCapture(os.path.join(file_path, filename))
        assert cap.isOpened(), "Error reading video file"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(f'{file_path}/{filename}_labeled.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS),
                            (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Выполнить инференс и получить результат
            results = self.model(frame, verbose=False)

            # Визуализировать результаты прямо на кадре
            annotated_frame = results[0].plot()

            # Записать кадр
            out.write(annotated_frame)

            # Отображение (опционально)
            # cv2.imshow('YOLOv8 Detection', annotated_frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

        cap.release()
        out.release()
        cv2.destroyAllWindows()
        ic("done")
        # cv2.destroyAllWindows()  # destroy all opened windows

        # # Открываем видео
        # cap = cv2.VideoCapture(os.path.join(file_path, os.listdir(file_path)[-1]))

        # # Уникальные ID обнаруженных объектов
        # counted_ids = set()

        # # Класс объекта, который нужно считать (например, человек = class_id 0 в COCO)
        # target_class_id = 0

        # while True:
        #     ret, frame = cap.read()
        #     if not ret:
        #         break

        #     # Обнаружение и трекинг
        #     results = self.model.track(frame, persist=True, conf=0.4, classes=[target_class_id])

        #     if results[0].boxes.id is not None:
        #         ids = results[0].boxes.id.cpu().numpy()
        #         classes = results[0].boxes.cls.cpu().numpy()

        #         for obj_id, cls in zip(ids, classes):
        #             if cls == target_class_id and obj_id not in counted_ids:
        #                 counted_ids.add(obj_id)

        #     # (Необязательно) Показываем кадр
        #     annotated_frame = results[0].plot()
        #     cv2.imshow("Tracking", annotated_frame)

        #     if cv2.waitKey(1) & 0xFF == ord('q'):
        #         break

        # cap.release()
        # # cv2.destroyAllWindows()

        # print(f"Объектов найдено: {len(counted_ids)}")
        return "test"


# import time
# scanner = Scanner()

# for i in range(100):
#     res = scanner.get_prediction("test")
#     ic(res)

# scanner.scan("test", "test/image", "image")
# while True:
#     res = scanner.get_prediction("test")
#     ic(res)
#     time.sleep(0.5)
#     if res != "Scanning still going":
#         break
