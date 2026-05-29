"""节点5: 生成微信HTML排版 - 大模型自由设计样式，真实网络配图"""
import re
import os
import time
from openai import OpenAI
from prompts.format_prompt import FORMAT_PROMPT
from tools.image_search import search_image


def get_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )


def replace_image_placeholders(html: str) -> str:
    """将 IMAGE_PLACEHOLDER_xxx 替换为真实网络图片URL"""
    pattern = r'src="IMAGE_PLACEHOLDER_([^"]+)"'

    def replacer(m):
        raw_desc = m.group(1)
        try:
            from urllib.parse import unquote
            desc = unquote(raw_desc)
        except Exception:
            desc = raw_desc
        # 从网络搜索真实图片
        img_url = search_image(desc)
        # 搜索之间有短暂间隔，避免触发 API 频率限制
        time.sleep(0.3)
        return f'src="{img_url}"'

    return re.sub(pattern, replacer, html)


def formatter_node(state: dict) -> dict:
    retry = state.get("format_retry_count", 0)
    print(f"🎨 [排版] 大模型自由设计HTML样式{'（重试）' if retry > 0 else ''}...")

    client = get_client()
    prompt = FORMAT_PROMPT.format(
        topic=state.get("topic", ""),
        angle=state.get("topic_angle", ""),
        article_title=state.get("article_title", ""),
        markdown_content=state["article_content"],
    )

    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=16000,
        messages=[{"role": "user", "content": prompt}],
    )
    full_html = resp.choices[0].message.content.strip()

    # 清理代码块标记
    if full_html.startswith("```html"):
        full_html = full_html[7:]
    if full_html.startswith("```"):
        full_html = full_html[3:]
    if full_html.endswith("```"):
        full_html = full_html[:-3]
    full_html = full_html.strip()

    # 替换图片占位符为真实网络图片
    full_html = replace_image_placeholders(full_html)

    print(f"✅ [排版] HTML生成完成，长度 {len(full_html)} 字符")
    return {
        **state,
        "html_content": full_html,
        "format_retry_count": retry,
        "status": "formatted",
    }
