FROM ubuntu:latest

RUN apt-get update -y
RUN apt install -y python3-pip python3-dev build-essential
COPY . /app
WORKDIR /app 
RUN pip3 install --break-system-packages -r requirements.txt
ENTRYPOINT ["python3"]
CMD ["app.py"]

