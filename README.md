# 银猫有话说 · 公众号智能体

全自动公众号推文生成与发布系统，基于 LangGraph 构建。从抓热点、选题、搜资料、写文章到微信排版发布，一条流水线跑完。

## 流程

```
热点抓取 → 选题 → 搜索规划 → 资料收集 → 写作 → 微信排版 → 格式校验 → 发布
```

也支持跳过选题，直接指定话题写文章。

## 技术栈

| 环节 | 技术 |
|------|------|
| 智能体框架 | LangGraph |
| 选题 / 排版 / 研究规划 | DeepSeek Chat |
| 写作（核心） | DeepSeek R1（推理模型） |
| 热点搜索 / 资料收集 | Tavily Search API |
| 热点来源 | 微博热搜、抖音热搜等 |
| 封面图 | 百度实图（免费，无需 API Key） |
| 发布 | 微信公众号官方 API |

## 快速开始

**1. 安装依赖**

```bash
pip install -r requirements.txt
```

**2. 配置环境变量**

复制 `.env.example` 为 `.env`，填写以下内容：

```env
# 必填
DEEPSEEK_API_KEY=sk-...
TAVILY_API_KEY=tvly-...

# 发布到公众号才需要
WECHAT_APP_ID=wx...
WECHAT_APP_SECRET=...

# 运行模式（true=只生成不发布）
DRY_RUN=true

# 仅保存草稿，不自动发布（适合订阅号）
DRAFT_ONLY=false
```

**3. 测试运行（不发布）**

```bash
python main.py --dry-run
```

生成结果保存在 `output/` 目录：
- `output/article.html` — 微信排版预览，浏览器直接打开查看效果
- `output/article.md` — 原始 Markdown
- `output/meta.json` — 标题、摘要、选题等元信息

**4. 正式发布**

```bash
# .env 中 DRY_RUN=false，填好微信配置
python main.py
```

## 使用方式

**自动选题**（默认）

```bash
python main.py
```

智能体自动抓取今日热点，选出最值得写的一个话题，全程无需干预。

**指定话题**

```bash
# 指定话题，角度由 AI 自动生成
python main.py --topic "夏天空调开多少度最省电"

# 话题和切入角度都指定
python main.py --topic "夏天空调开多少度最省电" --angle "从电费账单反推最优解"
```

**避免重复选题**

```bash
python main.py --used-topics "内卷" "躺平" "AI焦虑"
```

**组合使用**

```bash
python main.py --dry-run --topic "高考志愿怎么填" --angle "从录取数据看冷门专业的真实出路"
```

## 发布模式说明

| 模式 | 配置 | 说明 |
|------|------|------|
| dry-run | `DRY_RUN=true` 或 `--dry-run` | 只生成文件，不调用微信 API |
| 草稿模式 | `DRAFT_ONLY=true` | 上传草稿到公众号后台，手动点发布 |
| 自动发布 | `DRY_RUN=false` | 全自动发布，需认证服务号 |

> 订阅号无法调用自动发布接口，建议用草稿模式或 dry-run 后手动操作。

## 项目结构

```
├── main.py                  # 入口，命令行参数处理
├── graph.py                 # LangGraph 图定义与节点连接
├── nodes/
│   ├── topic_selector.py    # 抓热点、AI 选题（或使用指定话题）
│   ├── research_planner.py  # 规划 6-8 个搜索查询
│   ├── researcher.py        # 执行搜索，整理资料摘要
│   ├── writer.py            # DeepSeek R1 写作（1200-1800 字）
│   ├── formatter.py         # 生成微信内联 CSS HTML
│   ├── validator.py         # 格式校验，失败自动重排
│   └── publisher.py         # 上传封面图 → 创建草稿 → 发布
├── prompts/
│   ├── topic_prompt.py      # 选题 / 角度生成提示词
│   ├── writer_prompt.py     # 写作 / 研究规划提示词
│   └── format_prompt.py     # 排版提示词
├── tools/
│   ├── search_tool.py       # Tavily 搜索 + 热点抓取封装
│   └── wechat_api.py        # 微信公众号 API 封装
├── templates/
│   └── wechat_style.py      # 微信内联 CSS 样式
├── output/                  # 生成结果（运行后自动创建）
├── .env.example
└── requirements.txt
```

## 注意事项

- **写作风格**：以"银猫"人设写作，接地气、有观点，文章里会自然带出生活百科式的小知识点，不是课堂科普，就是那种"哦原来是这样"的日常涨知识感。
- **自动发布权限**：微信直接发布需要认证服务号。订阅号只能保存草稿，用 `DRAFT_ONLY=true` 或 dry-run 后手动发布。
- **内联 CSS**：微信不支持外部样式表，HTML 输出已全部内联处理。
- **图片**：文章中图片占位符在 dry-run 模式下不会替换，发布模式下自动从百度实图获取并插入。
