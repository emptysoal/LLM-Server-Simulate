from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import time
import random
import json
import asyncio

app = FastAPI(title="流式文本输出演示", version="1.0.0")

# 挂载静态文件（如果需要）
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 设置模板目录
templates = Jinja2Templates(directory="templates")


def stream_json(text: str, delay: float = 0.05):
    """异步生成器函数，用于逐字输出文本，返回JSON格式"""
    for index, char in enumerate(text):
        # 构建JSON数据
        data = {
            "char": char,
            "index": index,
            "total": len(text),
            "timestamp": time.time(),
            "progress": f"{(index + 1) / len(text) * 100:.1f}%"
        }
        yield json.dumps(data) + "\n"
        time.sleep(delay)  # 使用异步sleep


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
