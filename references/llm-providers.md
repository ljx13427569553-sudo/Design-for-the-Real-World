# 接入自己的大模型

本 Skill 生成的站点不含任何后端，前端直接请求一个 **OpenAI 兼容的
`/chat/completions` 接口**。填对 `CONFIG.llm` 三项即可开用。

## 各家参数

| 服务商 | baseURL | 常用 model | 备注 |
|---|---|---|---|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat`、`deepseek-reasoner` | 性价比高，中文好 |
| 阿里云通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus`、`qwen-turbo` | 需开启「兼容 OpenAI」模式 |
| 月之暗面 Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k`、`moonshot-v1-32k` | 长文本 |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash`、`glm-4-plus` | flash 有免费额度 |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini`、`gpt-4o` | 需可访问的出口网络 |
| 本地 Ollama | `http://localhost:11434/v1` | `qwen2.5:7b`、`llama3.1:8b` | apiKey 填任意值（如 `ollama`） |
| 本地 vLLM / LM Studio | `http://localhost:8000/v1` | 视部署而定 | 同上 |

## 请求体约定

`LLM.stream()` 发出的固定请求体：

```json
{ "model": "...", "messages": [...], "stream": true, "temperature": 0.7 }
```

响应按标准 SSE 解析：逐行读 `data: {...}`，取 `choices[0].delta.content`，
遇到 `data: [DONE]` 结束。只要兼容 OpenAI 流式协议即可，不需要任何 SDK。

## 视觉模型（拍照识书）

`CONFIG.llm.visionModel` 用于「图片识书」（上传书架/封面照片识别书名）。
该模型必须支持图片输入，例如 `gpt-4o-mini`、`glm-4v`、`qwen-vl-max`。
留空则回退到 `model`——若主模型不支持图片，识别会失败并提示改用书名添加。

## API Key 安全

### 两种填法，安全性差别很大

| 填法 | Key 落在哪 | 能否公开站点 |
|---|---|---|
| **页面里填**（推荐，不加 `--api-key`） | 浏览器 localStorage，**不进文件** | ✅ 可以传 GitHub / 分享 |
| 生成时注入 `--api-key` | 明文写在 `index.html` 里 | ❌ 绝对不能公开 |

页面里填的流程：打开站点 → 右上角「⚙ 连接模型」→ 填 Base URL / Key / 模型名 → 保存。
首次打开若未配置会自动弹出该弹层。读取优先级：**localStorage > 模板内置值**。

### 仍然存在的固有限制

纯前端直连时，Key 会出现在浏览器发出的请求头里（用户自己可见）。因此：

- 仅适用于自己用或可信内网；不要填生产高额度主 Key，建议单开一个限额 Key；
- 若要开放给公众使用，应改为「前端 → 自建代理（服务端保存 Key）→ 大模型」，
  把 `LLM.stream()` 的 fetch 地址指向自己的代理即可。

## 常见问题

**Q：添加书籍一直转圈或超时？**
模板内置 120 秒硬超时与一次自动重试。若仍失败，多为服务端限流或模型响应慢。
纯推理模型（如 `deepseek-reasoner`）思考阶段不吐字，等待明显更久，属正常。

**Q：换浏览器 / 清缓存后书架空了？**
数据存在浏览器 localStorage（键 `bookshelf.books.v1`），换环境即丢失。
需要跨设备同步请改用 `bookshelf-answers` 的 cloud 模式。

**Q：想导出或迁移书架？**
浏览器控制台执行：

```js
copy(JSON.stringify(JSON.parse(localStorage.getItem('bookshelf.books.v1'))))
```

导入则反向写入：

```js
localStorage.setItem('bookshelf.books.v1', JSON.stringify(阵列)); location.reload();
```

**Q：批量上传的书顺序和书单不一致？**
上传是 2 路并发，完成顺序不保证。书架按 `created_at` 排序展示，属预期行为。
