#!/usr/bin/env python3
"""一个最小的 OpenAI 兼容 mock 服务，用于在**没有 API Key** 的情况下先把书架跑通。

启动：
    python3 mock_llm_server.py --port 8899
然后在生成的 index.html 里把 CONFIG.llm 填成（或直接在页面「⚙ 连接模型」里填）：
    baseURL: 'http://127.0.0.1:8899/v1'
    apiKey:  'mock'
    model:   'mock-model'

它会识别「为图书《X》提供资料」这类请求并返回结构化 JSON，其余请求返回一段固定文本。
所有响应均以 SSE 流式返回，因此可以用来验证前端的流式解析是否正常。
"""
import argparse
import json
import re
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BOOK_TEMPLATE = {
    "title": "",
    "author": "（mock）未知",
    "category": "综合",
    "tags": ["mock", "示例"],
    "summary": "这是一条由 mock 服务生成的示例简介，用于在没有真实大模型时验证链路是否通畅。",
    "content": "要点一：示例内容。要点二：示例内容。要点三：示例内容。",
}


def sse_chunk(text: str) -> bytes:
    payload = {"choices": [{"delta": {"content": text}}]}
    return b"data: " + json.dumps(payload, ensure_ascii=False).encode("utf-8") + b"\n\n"


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self._cors()
        self.end_headers()
        self.wfile.write(json.dumps({"ok": True, "service": "mock-llm"}).encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw or b"{}")
        except Exception:
            body = {}

        # 取出最后一条用户消息文本
        text = ""
        for m in reversed(body.get("messages") or []):
            if m.get("role") == "user":
                c = m.get("content")
                text = c if isinstance(c, str) else " ".join(
                    p.get("text", "") for p in c if isinstance(p, dict)
                )
                break

        m = re.search(r"《([^》]+)》", text)
        if m and ("提供资料" in text or "JSON" in text):
            info = dict(BOOK_TEMPLATE)
            info["title"] = m.group(1)
            answer = json.dumps(info, ensure_ascii=False)
        elif "ping" in text.lower():
            answer = "正常"
        else:
            answer = "（mock 回答）你问的是：%s" % (text[:60] or "空问题")

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self._cors()
        self.end_headers()
        # 分块吐出，模拟真实流式
        step = 12
        for i in range(0, len(answer), step):
            self.wfile.write(sse_chunk(answer[i:i + step]))
            self.wfile.flush()
            time.sleep(0.01)
        self.wfile.write(b"data: [DONE]\n\n")
        self.wfile.flush()

    def log_message(self, fmt, *args):  # 静音
        pass


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=8899)
    args = p.parse_args()
    print("mock LLM 已启动： http://127.0.0.1:%d/v1/chat/completions" % args.port)
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
