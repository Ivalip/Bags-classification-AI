# Bags-classification-AI

Серверное приложения для определения количества сумок, рюкзаков и видео на фото и видео с помощью обученной нейронной сети с возможностью получения файла медиа с разметкой.

Исходный код обучения модели: https://www.kaggle.com/code/nikosolov/bagsai/

# Виды обращения к серверу

Серверное приложение разворачивается на порт 5000. В таблице ниже представлены виды запроса к серверу с учетом адреса и типа запроса

|Тип запроса|Адрес запроса|Описание запроса|
|-|-|-|
|GET|`/`|Получение кода доступа: `<code>`|
|POST|`/<code>`|Загрузка фото или видео на сервер для сканирования|
|GET|`/<code>`|Получение информации о сканировании со статусом 
|GET|`/<code>/download`|Получение фото или видео с разметкой|

# Способы развертывания серверного приложения
1. Локальный запуск
```
$ git clone --depth=1 "https://github.com/Ivalip/Bags-classification-AI"
$ cd Bags-classification-AI
$ pip install -r requirements.txt
$ cd app
$ python3 app.py
```
2. Через Docker Engine
```
$ sudo docker build -t ai-app "https://github.com/Ivalip/Bags-classification-AI.git#main:/"
$ sudo docker run -p 5000:5000 ai-app
```