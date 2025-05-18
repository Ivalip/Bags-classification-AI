import torch
import torchvision
from torchvision.models.detection.faster_rcnn import FastRCNNPredictor
from torchvision.transforms import functional as F

import fiftyone as fo
import fiftyone.zoo as foz
import fiftyone.utils.coco as fouc

from PIL import Image
import os
from tqdm import tqdm

# 1. Загружаем COCO 2014 с помощью FiftyOne
print("Loading COCO 2014...")
dataset = foz.load_zoo_dataset(
    "coco-2014",
    split="train",
    dataset_name="coco-2014-baggage",
    label_types=["detections"],
    classes=["backpack", "handbag", "suitcase"],
    max_samples=500,  # Ограничим для ускорения обучения
)

# 2. Подготовка данных в PyTorch Dataset
class BaggageDataset(torch.utils.data.Dataset):
    def __init__(self, fiftyone_dataset, transforms=None):
        self.samples = fiftyone_dataset
        self.transforms = transforms

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = Image.open(sample.filepath).convert("RGB")

        boxes = []
        labels = []

        for obj in sample.detections.detections:
            x, y, w, h = obj.bounding_box
            W, H = image.size
            x1 = x * W
            y1 = y * H
            x2 = x1 + w * W
            y2 = y1 + h * H
            boxes.append([x1, y1, x2, y2])
            # map to label indices:
            label = {"backpack": 1, "handbag": 2, "suitcase": 3}[obj.label]
            labels.append(label)

        boxes = torch.as_tensor(boxes, dtype=torch.float32)
        labels = torch.as_tensor(labels, dtype=torch.int64)

        target = {
            "boxes": boxes,
            "labels": labels,
        }

        if self.transforms:
            image = self.transforms(image)

        return image, target

    def __len__(self):
        return len(self.samples)

#  3. Создаем DataLoader
def get_transform():
    return torchvision.transforms.Compose([
        torchvision.transforms.ToTensor(),
    ])

dataset_train = BaggageDataset(dataset, transforms=get_transform())
data_loader = torch.utils.data.DataLoader(dataset_train, batch_size=2, shuffle=True, collate_fn=lambda x: tuple(zip(*x)))

#  4. Создание модели Faster R-CNN
def get_model(num_classes):
    model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
    in_features = model.roi_heads.box_predictor.cls_score.in_features
    model.roi_heads.box_predictor = FastRCNNPredictor(in_features, num_classes)
    return model

model = get_model(num_classes=4)  # 0 - background, 1-3 - наши классы
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

#  5. Тренировка
optimizer = torch.optim.SGD(model.parameters(), lr=0.005, momentum=0.9)

print("Training...")
model.train()
for epoch in range(5):
    for i, (images, targets) in enumerate(tqdm(data_loader)):
        
        images = list(img.to(device) for img in images)
        targets = [{k: v.to(device) for k, v in t.items()} for t in targets]

        loss_dict = model(images, targets)
        losses = sum(loss for loss in loss_dict.values())

        optimizer.zero_grad()
        losses.backward()
        optimizer.step()

    print(f"Epoch {epoch+1}, Loss: {losses.item()}")

#  6. Сохранение в TorchScript
print("Exporting TorchScript...")
model.eval()
example_input = [torch.rand(3, 512, 512).to(device)]
traced_model = torch.jit.trace(model, example_input)
torch.jit.save(traced_model, "baggage_detector.pt")
print("Model saved to baggage_detector.pt5")
