FROM python:3.8.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
CMD gunicorn -w 2 -b 0.0.0.0:5000 server:app
