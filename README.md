# bookshelf-lite · 个人智能书架

一个**空书架，上传自己的书，然后问答找书**的极简网站。

无后端、无登录、无权限管理——书架存在浏览器 localStorage，问答接你自己的大模型。

![书架预览](https://img.shields.io/badge/纯前端-单文件%20HTML-orange) ![后端](https://img.shields.io/badge/存储-localStorage-blue) ![模型](https://img.shields.io/badge/LLM-OpenAI%20兼容-green)

---

## 它能做什么

| 功能 | 说明 |
|---|---|
| 📖 上传图书 | 输入书名添加，或粘贴书单批量导入（自动清洗序号、表情、作者分隔符） |
| 🖼️ 图片识书 | 拍照 / 拖入书架照片，视觉模型识别书名并逐本添加 |
| 🪵 可视化书架 | 木质书架 + 多彩书脊，每 7 本一排，点击看详情 |
| ✏️ 编辑删除 | 改书名、作者、分类、标签、简介、内容要点 |
| 💬 问答找书 | 提问后从书架里推荐最相关的书，附书名与简介 |

## 快速开始

### 方式 A：作为 Agent Skill 使用（推荐）

装到你的 agent 技能目录，之后让 AI 一句话帮你生成：

```bash
# 复制到用户级 skill 目录
cp -R bookshelf-lite ~/.workbuddy/skills/

# 或者直接告诉 agent：
# "用 bookshelf-lite 帮我搭一个书架，接 DeepSeek"
```

### 方式 B：直接用脚本生成

```bash
# 不写 Key 进文件（推荐，Key 在页面里填，可安全分享站点）
python3 scripts/init_bookshelf.py --out ~/my-bookshelf \
  --base-url https://api.deepseek.com/v1 \
  --model deepseek-chat

# 本机自用、想省事也可以直接注入 Key
python3 scripts/init_bookshelf.py --out ~/my-bookshelf \
  --base-url https://api.deepseek.com/v1 \
  --api-key sk-xxxxxx --model deepseek-chat

# 想先跑通链路但没有 Key？用自带的假模型服务
python3 scripts/mock_llm_server.py --port 8899
python3 scripts/init_bookshelf.py --out ~/my-bookshelf \
  --base-url http://127.0.0.1:8899/v1 --api-key mock --model mock-model
```

生成完直接用浏览器打开 `my-bookshelf/index.html`。

## 连接大模型

任意 **OpenAI 兼容接口**都能接：

| 厂商 | Base URL | 模型名示例 |
|---|---|---|
| DeepSeek | `https://api.deepseek.com/v1` | `deepseek-chat` |
| 通义千问 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus` |
| Kimi | `https://api.moonshot.cn/v1` | `moonshot-v1-8k` |
| 智谱 GLM | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` |
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| 本地 Ollama | `http://localhost:11434/v1` | `qwen2.5:7b` |

更多见 [`references/llm-providers.md`](references/llm-providers.md)。

两种填法：
1. **页面里填**（推荐）：打开站点 → 右上角「⚙ 连接模型」→ 填入并保存，存在浏览器 localStorage
2. **生成时注入**：`--api-key sk-xxx`，会写进 HTML（**别把这种情况下生成的站点传公开仓库**）

## 🔒 关于 API Key 安全

这是本项目最需要留意的一点：

- 模板与仓库**不包含任何密钥**，配置位是空占位符
- 推荐走「页面里填」，密钥只存浏览器，**不落在文件里**——这样把站点传 GitHub、发给别人都安全
- 如果用了 `--api-key` 注入，Key 会以明文出现在 `index.html` 里，此时**请勿公开该站点**
- 纯前端直连意味着 Key 会出现在浏览器请求头中，因此**只适用于自己用或信任的局域网环境**；若要开放给公众使用，应加一层后端代理来隐藏密钥

## 目录结构

```
bookshelf-lite/
├── SKILL.md                      # Agent Skill 说明（触发条件、工作流）
├── assets/index.html             # 站点模板（单文件，含全部功能）
├── scripts/
│   ├── init_bookshelf.py         # 生成器：把模板变成你的专属站点
│   └── mock_llm_server.py        # 假模型服务，无 Key 时验证链路
└── references/
    └── llm-providers.md          # 各家大模型接入参数
```

## License

MIT — 见 [LICENSE](LICENSE)。
