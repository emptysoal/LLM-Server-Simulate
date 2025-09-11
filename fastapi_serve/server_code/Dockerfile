FROM python:3.8.9
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple
CMD uvicorn server_02:app --host 0.0.0.0 --port 8000
