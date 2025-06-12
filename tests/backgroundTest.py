import time
import sys
import os
from icecream import ic

# import pytest
# Добавляем src в путь, чтобы можно было импортировать my_module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from aiPredict import Scanner

scanner = Scanner()

for i in range(100):
    res = scanner.get_prediction("test")
    ic(res)

scanner.scan("test", "test/image", "image")
while True:
    res = scanner.get_prediction("test")
    ic(res)
    time.sleep(0.5)
    if res != "Scanning still going":
        break
