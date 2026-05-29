# 银渐层沉思录 · 公众号智能体

全自动公众号推文生成与发布系统，基于 LangGraph 构建，从选题到发布一键完成。

## 流程

```
热点搜索 → 选题 → 规划搜索 → 资料收集 → Opus写作 → 微信排版 → 格式校验 → 发布
```

## 技术栈

| 环节 | 技术 |
|------|------|
| 智能体框架 | LangGraph |
| 选题 / 规划 / 排版 | Claude Sonnet 4.6 |
| 写作（核心） | Claude Opus 4.6 |
| 热点搜索 / 资料收集 | Tavily Search API |
| 封面图 | Unsplash API（无Key时fallback到picsum） |
| 发布 | 微信公众号官方API |

## 快速开始

**1. 安装依赖**

```bash
pip install -r requirements.txt
```

**2. 配置环境变量**

```bash
cp .env .env
```

编辑 `.env`，至少填写前两项即可运行 dry-run：

```env
ANTHROPIC_API_KEY=sk-ant-...
TAVILY_API_KEY=tvly-...

# 发布到公众号才需要以下配置
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...
UNSPLASH_ACCESS_KEY=...

DRY_RUN=true
```

**3. 测试运行（不发布）**

```bash
python main.py --dry-run
```

生成结果保存在 `output/` 目录：
- `output/article.html` — 微信排版预览，浏览器直接打开
- `output/article.md` — 原始 Markdown
- `output/meta.json` — 标题、摘要等元信息

**4. 正式发布**

```bash
# 将 .env 中 DRY_RUN 改为 false，填好微信配置
python main.py
```

**避免重复选题**

```bash
python main.py --used-topics "AI焦虑" "内卷" "躺平"
```

## 项目结构

```
├── main.py                  # 入口
├── graph.py                 # LangGraph 图定义
├── nodes/
│   ├── topic_selector.py    # 搜索热点，Claude 选题
│   ├── research_planner.py  # 规划 6-8 个搜索查询
│   ├── researcher.py        # 执行搜索，整理资料摘要
│   ├── writer.py            # Opus 写作 3000-4000 字
│   ├── formatter.py         # 生成微信内联 CSS HTML
│   ├── validator.py         # 格式校验，失败自动重试
│   └── publisher.py        # 上传封面图 → 草稿 → 发布
├── tools/
│   ├── search_tool.py       # Tavily 搜索封装
│   └── wechat_api.py        # 微信公众号 API 封装
├── prompts/                 # 选题 / 写作 / 排版提示词
├── templates/
│   └── wechat_style.py      # 微信内联 CSS 样式常量
├── .env.example
└── requirements.txt
```

## 注意事项

- **发布权限**：微信 API 直接发布需要**认证服务号**。订阅号只能保存草稿，无法调用 `freepublish/submit`，建议先用 dry-run 生成 HTML，再手动粘贴到公众号编辑器。
- **内联 CSS**：微信不支持外部样式表，所有样式已内联处理，不要在 HTML 中添加 `class` 或 `<link>` 标签。
- **图片**：文章中的图片占位符（`IMAGE_PLACEHOLDER_*`）在 dry-run 模式下不会替换为真实图片，发布前需手动处理或配置 Unsplash Key。
