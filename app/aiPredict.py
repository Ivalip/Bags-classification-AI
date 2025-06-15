import os
import cv2
import supervision as sv
from icecream import ic
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
# --------- Import YOLO -----------
from ultralytics import YOLO, solutions
ic("ultralytics has been imported")

class Scanner():
    def __init__(self):
        self.model_path = 'app/models/20250613_161906_yolo11m_MEGA_5hr.pt'
        self.model = YOLO(self.model_path, task='detect')
        self.classes = [self.model.names[k] for k in sorted(self.model.names)]
        self.tracker = sv.ByteTrack()
        ic("YOLO model have been imported")
        ic(self.classes)
        # Создаём пул потоков
        self.executor = ThreadPoolExecutor(max_workers=20)
        self.pool = {}
    def rename_keys(original_dict):
        """
        Заменяет ключи в original_dict согласно rename_map.

        :param original_dict: исходный словарь
        :param rename_map: словарь вида {старое_имя: новое_имя}
        :return: новый словарь с переименованными ключами
        """
        rename_interface = {"Пакет": "bags", "Сумка":"handbags", "Чемодан":"suitcases", "Рюкзак":"backpacks"}
        return {
            rename_interface.get(key, key): value
            for key, value in original_dict.items()
        }

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
            return {"status": "Prediction has been done before"}
        if not self.pool[code].done():
            return {"status": "Scanning still going"}
        result = self.pool[code].result()
        ic(result)
        result["status"] = "Scanning is Done!"
        del self.pool[code]
        return result
    def scan_image(self, file_path):
        # TODO: complete this method
        filename = os.listdir(file_path)[-1]
        ic("in scan_image", filename)
        results = self.model(os.path.join(file_path, filename))
        ic("Image scanned")
        for r in results:
            res = [(self.model.names[i.cls.item()], i.conf.item()) for i in r.boxes]
            r.save(filename=f'{file_path}/{filename}_labeled.jpg')
        ic(res)
        bag_count = {class_name: sum(1 for item in res if item[0] == class_name) for class_name in self.classes}
        ic(bag_count)
        return Scanner.rename_keys(bag_count)

    def scan_video(self, file_path):
        filename = os.listdir(file_path)[-1]
        cap = cv2.VideoCapture(os.path.join(file_path, filename))
        assert cap.isOpened(), "Error reading video file"

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(f'{file_path}/{filename}_labeled.mp4', fourcc, cap.get(cv2.CAP_PROP_FPS),
                            (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

        # Initialize object counter object
        # counter = solutions.ObjectCounter(
        #     show=True,  # display the output
        #     # region=region_points,  # pass region points
        #     model=self.model_path,  # model="yolo11n-obb.pt" for object counting with OBB model.
        #     # classes=[0, 2],  # count specific classes i.e. person and car with COCO pretrained model.
        #     tracker="botsort.yaml",  # choose trackers i.e "bytetrack.yaml"
        # )


        unique_ids_per_class = defaultdict(set)
        class_names = self.model.names


        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Предсказываем 
            results = self.model(frame, verbose=False)[0]

            # Нарисовать разметку на кадре
            out.write(results.plot())

            #--------------------- Подсчет --------------------
            detections = sv.Detections.from_ultralytics(results)

            # Применяем трекинг: к входу ByteTrack нужен именно объект sv.Detections
            tracked = self.tracker.update_with_detections(detections)

            # tracked — это объект sv.Detections с дополненными атрибутами tracker_id и class_id
            for cls_id, track_id in zip(tracked.class_id, tracked.tracker_id):
                unique_ids_per_class[class_names[int(cls_id)]].add(int(track_id))
            #--------------------------------------------------

            # results = counter(frame)
            # print(results)

        cap.release()
        out.release()

        cv2.destroyAllWindows()

        ic("Video is done scanning")

        final_counts = {cls: len(ids) for cls, ids in unique_ids_per_class.items()}

        # bag_count = {self.rename_interface[class_name]: sum(1 for item in res if item[0] == class_name) for class_name in self.classes}
        ic(final_counts)
        return Scanner.rename_keys(final_counts)
        # return {"bags": 5, "handbags": 5, "suitcases": 5, "backpacks": 5}


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
