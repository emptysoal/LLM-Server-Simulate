from flask import Flask, render_template, request, Response, jsonify
import time
import random
import json
from threading import Thread, Lock

app = Flask(__name__)


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


def stream_json(text, delay=0.05):
    """生成器函数，用于逐字输出文本，返回JSON格式"""

    text_streamer = TextIterator()

    # 模拟把大模型的推理放到一个线程中并行执行
    t = Thread(target=generate_text, args=(text, delay, text_streamer))
    t.start()

    for idx, char in enumerate(text_streamer):
        if char == "&":
            continue
        # 构建JSON数据
        data = {
            "char": char,
            "index": idx,
            "total": len(text),
            "timestamp": time.time(),
            "progress": f"{(idx + 1) / len(text) * 100:.1f}%"
        }
        yield json.dumps(data) + "\n"

    t.join()


@app.route('/test')
def connect_test():
    return {"message": "success", "status": 200}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/stream-json', methods=['POST'])
def stream():
    text = request.form.get('text', '')
    if not text:
        return jsonify({"error": "没有提供文本"}), 400

    # 随机添加一点延迟变化，使输出更自然
    base_delay = 0.05
    variation = random.uniform(0.8, 1.2)

    return Response(
        stream_json(text, delay=base_delay * variation),
        mimetype='application/json'
    )


if __name__ == '__main__':
    app.run(port=5000, host="0.0.0.0")
