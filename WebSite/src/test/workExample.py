import requests
import os 
from time import sleep

url = 'http://127.0.0.1:5000/'

x = requests.get(url)
print("GET Code", x.status_code, x.text)
code = x.text
print('"' in code)
if ('"' in code):
    code = code.replace('"','')
# print(os.getcwd())
files = {'image': open('test.jpg', 'rb')}
# sleep(2)
print("POST image")
x = requests.post(f"{url}/{code}", files=files)

print(x.status_code, x.content)
print(files)

x = requests.post(f"{url}/{code}", files=files)

x = requests.get(url+code)
print(x.status_code, x.content)