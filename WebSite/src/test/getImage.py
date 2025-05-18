import requests
import os 
url = 'http://127.0.0.1:5000/uploads'
# print(os.getcwd())
x = requests.get(url)
print(x.status_code)
with open("response.jpg", "wb") as f:
    f.write(x.content)