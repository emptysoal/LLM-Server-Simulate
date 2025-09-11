from flask import Flask, render_template, request, Response, jsonify
import time
import random
import json

app = Flask(__name__)


def stream_json(text, delay=0.05):
    """生成器函数，用于逐字输出文本，返回JSON格式"""
    for idx, char in enumerate(text):
        # 构建JSON数据
        data = {
            "char": char,
            "index": idx,
            "total": len(text),
            "timestamp": time.time(),
            "progress": f"{(idx + 1) / len(text) * 100:.1f}%"
        }
        yield json.dumps(data) + "\n"
        time.sleep(delay)  # 控制输出速度


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


# if __name__ == '__main__':
#     app.run(port=5000, host="0.0.0.0")
