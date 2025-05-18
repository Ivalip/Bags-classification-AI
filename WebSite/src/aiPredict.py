import torch
print("torch has been imported")
from torchvision import transforms
print("torchvision has been imported")
from PIL import Image
import io

image_path = 'test/test.jpg'  # Укажите путь к вашему изображению
model = torch.jit.load('model_scripted.pt', map_location=torch.device('cpu')).eval()
image = Image.open(image_path)
image = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28,28)),
    # transforms.ToPILImage(), 
    transforms.ToTensor()
])(image).reshape(1,1,28,28)
res = model(image)
print(res.argmax())