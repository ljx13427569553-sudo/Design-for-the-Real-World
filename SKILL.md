---
name: bookshelf-lite
description: 搭建极简版个人智能书架网站——一个空书架，用户上传自己的书，然后基于藏书问答找书。无后端、无登录、无权限管理，书架存浏览器 localStorage，问答接自备的 OpenAI 兼容大模型（DeepSeek/通义/Kimi/OpenAI/本地 Ollama）。当用户想要一个"简单点""不用登录""自己用"的书架或私人书单问答站点时使用。
agent_created: true
---

# 极简智能书架（bookshelf-lite）

给用户一个**空书架**：上传自己的书 → AI 自动理解每本书 → 基于藏书问答找书。

产出物是一个**自包含的 `index.html`**（约 990 行，无后端、无构建步骤，双击即用）。

## 与完整版 `bookshelf-answers` 的区别

| | 本 Skill（lite） | bookshelf-answers |
|---|---|---|
| 后端 | 无（localStorage） | 可选本地 / WorkBuddy 云服务 |
| 登录与权限 | **完全没有** | 邮箱登录 + 数据隔离 |
| 大模型 | 自备 OpenAI 兼容接口 | 自备接口 或 平台免密钥模型 |
| 多设备同步 / 分享 | ❌ | ✅（cloud 模式） |
| 代码复杂度 | 单后端，3 个模块 | 双后端 + Backend 适配层 |

**何时改用完整版**：用户说"分享给别人""换设备也要能看到""不想配 API Key"时，
改用 `bookshelf-answers` 的 cloud 模式。

## 工作流

1. 向用户收集必填项：`baseURL`、`model`；`apiKey` **可选**。
   可选 `visionModel`（支持图片的模型，用于拍照识书）。

   **Key 优先让用户在页面里填**（不加 `--api-key` 参数）：密钥只存浏览器 localStorage，
   不写入文件，站点可安全分享 / 传 GitHub。用户明确表示"本机自用、想省事"时才用 `--api-key` 注入。

   常用接口（详见 `references/llm-providers.md`）：

   | 服务商 | baseURL | model |
   |---|---|---|
   | DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
   | 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
   | Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
   | OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
   | 本地 Ollama | `http://localhost:11434/v1` | `qwen2.5:7b`（apiKey 填 `ollama`） |

2. 生成站点（**默认不写 Key**）：

   ```bash
   python3 scripts/init_bookshelf.py --out ~/my-bookshelf \
     --base-url https://api.deepseek.com/v1 \
     --model deepseek-chat
   ```

3. 打开 `~/my-bookshelf/index.html`：
   - 未填 Key 时会**自动弹出「连接模型」弹层**，引导填写（填完存浏览器本地）
   - 填好后右上角状态点显示「已就绪 · <模型名>」，页面**没有登录入口**
   - 随时可点工具栏「⚙ 连接模型」修改配置

4. 冒烟：加一本书 → 出现在书架 → 问答能返回基于该书的回答。

**用户暂时没有 Key 时**：先起 `python3 scripts/mock_llm_server.py --port 8899`，
用 `--base-url http://127.0.0.1:8899/v1 --api-key mock --model mock-model` 生成，
界面和链路可以先跑通，之后替换真实配置。

## 文件清单

| 文件 | 用途 |
|---|---|
| `assets/index.html` | 站点模板（4 个占位符：`__BASE_URL__` `__API_KEY__` `__MODEL__` `__VISION_MODEL__`） |
| `scripts/init_bookshelf.py` | 注入配置，生成实例站点 |
| `scripts/mock_llm_server.py` | 无 Key 时跑通链路的 mock 大模型（含 CORS，可直接配合浏览器使用） |
| `references/llm-providers.md` | 各家接入参数、Key 安全说明、常见问题 |

## 代码结构（二次开发时）

模板只有三个模块，改动前先认清边界：

- `CONFIG`（文件顶部）—— 站点文案 + 大模型接口，用户唯一需要动的地方。
- `Store` —— localStorage 读写：`read/write/list/add/update/remove`。
- `LLM.stream(messages, opts)` —— OpenAI 兼容 SSE 流式调用，取 `choices[0].delta.content`。

业务层（清洗书单、批量上传、问答、编辑删除）直接调这两个模块，**不要再引入
后端适配层或登录逻辑**，否则就退化成完整版了。

改完务必跑语法校验：

```bash
node -e "const js=require('fs').readFileSync('assets/index.html','utf8').match(/<script>([\s\S]*?)<\/script>/)[1]; new (require('vm').Script)(js); console.log('OK')"
```

## 已内置的健壮性设计（不要退化）

- **硬超时**：`withHardTimeout()` 用 `Promise.race` 兜底，单本书 120 秒必出结果。
  不要改回仅依赖 `AbortController`——流式请求对 abort 响应不彻底时会永久挂起。
- **并行上传 + 失败清单**：并发 2 路，失败的书单独列出，不影响其余书籍。
- **书单清洗**：`cleanBookLine()` 去除序号（`1.` `2、` `（3）` `【4】`）、emoji、
  书名号，并拆分「书名 / 作者」「书名｜作者」「书名——作者」。
- **书架分排**：每排 7 本。改步长时务必同步改 `slice(start, start + 7)`，
  否则会重复渲染一整本书。

## 验证清单（交付前）

- [ ] `node` 语法校验通过
- [ ] 打开是空书架，且页面无登录入口
- [ ] 状态点显示模型已就绪
- [ ] 批量上传书单的清洗预览正确（序号、emoji 已去除）
- [ ] 添加的书渲染到书架，刷新后仍在
- [ ] 问答返回基于书架内容的回答
