"""节点4: 写作爆款推文"""
import re
import os
from openai import OpenAI
from prompts.writer_prompt import WRITER_PROMPT, DIGEST_EXTRACTOR_PROMPT


def get_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )


def writer_node(state: dict) -> dict:
    print(f"✍️  [写作] 开始撰写「{state['topic']}」...")
    client = get_client()

    prompt = WRITER_PROMPT.format(
        topic=state["topic"],
        angle=state.get("topic_angle", ""),
        research_summary=state.get("research_summary", ""),
    )

    # 写作用 deepseek-reasoner（R1），有推理能力，内容更有深度
    print("   使用 DeepSeek-R1 写作中（约需1-2分钟）...")
    resp = client.chat.completions.create(
        model="deepseek-reasoner",
        max_tokens=12000,
        messages=[{"role": "user", "content": prompt}],
    )
    article_md = resp.choices[0].message.content.strip()

    # 提取标题
    title = state["topic"]
    title_match = re.search(r'^#\s+(.+)$', article_md, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        article_md = article_md.replace(title_match.group(0), "", 1).strip()

    # 提取摘要
    digest = ""
    digest_match = re.search(r'^>\s*(.+?)(?:\n(?!>)|$)', article_md, re.MULTILINE | re.DOTALL)
    if digest_match:
        digest_block = digest_match.group(0)
        digest_resp = client.chat.completions.create(
            model="deepseek-chat",
            max_tokens=200,
            messages=[{"role": "user", "content": DIGEST_EXTRACTOR_PROMPT.format(digest_block=digest_block)}],
        )
        digest = digest_resp.choices[0].message.content.strip()[:120]

    word_count = len(article_md.replace(" ", "").replace("\n", ""))
    print(f"✅ [写作] 完成！标题：{title}，字数约 {word_count} 字")

    return {
        **state,
        "article_title": title,
        "article_content": article_md,
        "article_digest": digest,
        "status": "written",
    }
