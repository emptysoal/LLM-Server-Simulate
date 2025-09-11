from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
import random
import json
import asyncio
from threading import Thread, Lock
from queue import Queue

app = FastAPI(title="流式文本输出演示", version="1.0.0")


class TextIterator:
    def __init__(self):
        self.text = ""
        self._pos = 0
        self._stop = False
        self.lock = Lock()

    def add_char(self, char):
        with self.lock:
            self.text += char

    def __iter__(self):
        return self

    def __next__(self):
        if self._stop:
            raise StopIteration

        while True:
            if self._pos >= len(self.text):
                continue
            char = self.text[self._pos]
            break

        if char == "&":
            self._stop = True

        self._pos += 1

        return char


def generate_text(string: str, delay: float, iterator: TextIterator):
    """模拟大模型的 model.generate 方法进行流式输出"""
    for char in string:
        time.sleep(delay)  # 模拟推理，推理一个 token 耗时 delay
        iterator.add_char(char)
    # 追加结束标识
    time.sleep(delay)
    iterator.add_char("&")  # & 标识生成结束，相当于<|endoftext|>


# 挂载静态文件（如果需要）
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="templates")


def stream_json(text: str, delay: float = 0.05):
    """异步生成器函数，用于逐字输出文本，返回JSON格式"""

    text_streamer = TextIterator()

    # 模拟把大模型的推理放到一个线程中并行执行
    t = Thread(target=generate_text, args=(text, delay, text_streamer))
    t.daemon = True  # 设置为守护线程，确保主程序退出时线程也会退出
    t.start()

    for index, char in enumerate(text_streamer):
        if char == "&":
            continue
        # 构建JSON数据
        data = {
            "char": char,
            "index": index,
            "total": len(text),
            "timestamp": time.time(),
            "progress": f"{(index + 1) / len(text) * 100:.1f}%"
        }
        yield json.dumps(data) + "\n"

    t.join()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """返回主页面"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/stream-json")
async def stream_json_endpoint(request: Request):
    """流式JSON数据端点"""
    form_data = await request.form()
    text = form_data.get("text", "")

    if not text:
        return {"error": "没有提供文本"}

    # 随机添加一点延迟变化，使输出更自然
    base_delay = 0.05
    variation = random.uniform(0.8, 1.2)

    return StreamingResponse(
        stream_json(text, delay=base_delay * variation),
        media_type="application/json"
    )


# 可选：添加一个健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}
