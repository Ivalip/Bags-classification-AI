import requests
import os 
url = 'http://127.0.0.1:5000/DeC89Csj0pYPL9ZNQAf'
# print(os.getcwd())
files = {'file': open('test.jpg', 'rb')}
x = requests.post(url, files=files)
print(x.status_code, x.content)