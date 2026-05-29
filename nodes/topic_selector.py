"""节点1: 选题"""
import json
import os
from openai import OpenAI
from tools.search_tool import search_trending_topics
from prompts.topic_prompt import TOPIC_SELECTOR_PROMPT


def get_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )


def chat(client, prompt: str, model: str = "deepseek-chat", max_tokens: int = 512) -> str:
    resp = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.choices[0].message.content.strip()


def topic_selector_node(state: dict) -> dict:
    print("🔍 [选题] 搜索热点话题...")
    trending = search_trending_topics()
    trending_text = "\n".join(
        f"- {r['title']}: {r['content'][:150]}" for r in trending[:15] if r.get("title")
    )

    used = state.get("used_topics", [])
    used_text = "\n".join(f"- {t}" for t in used) if used else "（无）"

    prompt = TOPIC_SELECTOR_PROMPT.format(
        trending_content=trending_text,
        used_topics=used_text,
    )

    client = get_client()
    print("🤔 [选题] DeepSeek 分析热点，选择最佳选题...")
    raw = chat(client, prompt, max_tokens=512)

    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    data = json.loads(raw)
    print(f"✅ [选题] 选定话题：{data['topic']} | 角度：{data['angle']}")

    return {
        **state,
        "topic": data["topic"],
        "topic_angle": data["angle"],
        "topic_reason": data["reason"],
        "topic_keywords": data.get("keywords", []),
        "status": "topic_selected",
    }
