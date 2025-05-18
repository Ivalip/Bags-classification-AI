import cv2
import os

def getSize(path) -> str:
 res = cv2.imread(path).shape
 size = os.path.getsize(path)
#  os.remove(path)
 return f"{res}, {size}"