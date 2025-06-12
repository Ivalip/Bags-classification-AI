import requests
import os 
url = 'http://127.0.0.1:5000/'
# print(os.getcwd())
x = requests.get(url)
print(x.status_code, x.text)