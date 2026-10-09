#!/usr/bin/env python3
"""生成一个极简版个人智能书架站点（单文件 index.html）。

无后端、无登录、无权限：书架存浏览器 localStorage，问答走自备的 OpenAI 兼容大模型。

用法（推荐：不写 Key，由使用者在页面里填，站点可安全分享）：
  python3 init_bookshelf.py --out ~/my-bookshelf \
      --base-url https://api.deepseek.com/v1 \
      --model deepseek-chat

  # 本机自用、想省事才注入 Key（注意：此时站点不可公开）
  python3 init_bookshelf.py --out ~/my-bookshelf \
      --base-url https://api.deepseek.com/v1 \
      --api-key <你的Key> \
      --model deepseek-chat

  # 本机 Ollama（无需真实 Key，填任意字符串即可）
  python3 init_bookshelf.py --out ~/my-bookshelf \
      --base-url http://localhost:11434/v1 --api-key ollama --model qwen2.5:7b

  # 还没有 Key：先用 mock 服务把界面跑通
  python3 mock_llm_server.py --port 8899 &
  python3 init_bookshelf.py --out ~/my-bookshelf \
      --base-url http://127.0.0.1:8899/v1 --api-key mock --model mock-model
"""
import argparse
import os
import sys

TEMPLATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "index.html")

PLACEHOLDERS = {
    "base_url": "__BASE_URL__",
    "api_key": "__API_KEY__",
    "model": "__MODEL__",
    "vision_model": "__VISION_MODEL__",
}


def js_str(value: str) -> str:
    """转成可安全嵌入 JS 单引号字符串的内容。"""
    return value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n")


def main():
    p = argparse.ArgumentParser(description="生成极简版智能书架站点")
    p.add_argument("--out", required=True, help="输出目录（不存在则创建）")
    p.add_argument("--base-url", dest="base_url", required=True,
                   help="OpenAI 兼容接口 baseURL，如 https://api.deepseek.com/v1")
    p.add_argument("--api-key", dest="api_key", default="",
                   help="API Key。留空则不写入文件，由使用者在页面「⚙ 连接模型」里填写（存浏览器本地，可安全分享站点）")
    p.add_argument("--model", required=True, help="模型名，如 deepseek-chat")
    p.add_argument("--vision-model", dest="vision_model", default="",
                   help="视觉模型名（图片识书用，可留空）")
    p.add_argument("--title", help="站点标题（浏览器标签）")
    p.add_argument("--subtitle", help="首屏大标题，可用 \\n 换行")
    args = p.parse_args()

    if not os.path.exists(TEMPLATE):
        sys.exit("找不到模板文件：%s" % os.path.abspath(TEMPLATE))

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        html = f.read()

    values = {
        "base_url": args.base_url or "",
        "api_key": args.api_key or "",
        "model": args.model or "",
        "vision_model": args.vision_model or "",
    }
    for key, token in PLACEHOLDERS.items():
        html = html.replace(token, js_str(values[key]))

    if args.title:
        html = html.replace("'我的书架'", "'%s'" % js_str(args.title), 1)
        html = html.replace("<title>答案就在书架上 · 你的私人智能书架</title>",
                            "<title>%s</title>" % args.title, 1)
    if args.subtitle:
        html = html.replace("'问题的答案，也许早就在书里。'", "'%s'" % js_str(args.subtitle), 1)

    out_dir = os.path.abspath(os.path.expanduser(args.out))
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "index.html")
    with open(target, "w", encoding="utf-8") as f:
        f.write(html)

    print("✅ 已生成：%s" % target)
    print("   接口：%s" % args.base_url)
    print("   模型：%s%s" % (args.model, ("（视觉：%s）" % args.vision_model) if args.vision_model else ""))
    if args.api_key:
        print("   ⚠️  API Key 已写入文件：请勿把此站点上传到公开仓库或分享给他人")
    else:
        print("   🔒 未写入 API Key：打开页面后点右上角「⚙ 连接模型」填写，密钥只存浏览器本地")
    print("\n直接用浏览器打开 index.html 即可（无需后端、无需登录）。")
    print("   如需 http 方式：python3 -m http.server 8000 --directory %s" % out_dir)


if __name__ == "__main__":
    main()
