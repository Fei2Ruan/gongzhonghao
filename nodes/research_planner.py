"""节点2: 规划搜索策略"""
import json
import os
from openai import OpenAI
from prompts.writer_prompt import RESEARCH_PLANNER_PROMPT


def get_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )


def research_planner_node(state: dict) -> dict:
    print(f"📋 [规划] 为「{state['topic']}」规划搜索策略...")
    client = get_client()

    prompt = RESEARCH_PLANNER_PROMPT.format(
        topic=state["topic"],
        angle=state.get("topic_angle", ""),
    )
    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = resp.choices[0].message.content.strip()

    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    data = json.loads(raw)
    queries = [q["query"] for q in data.get("queries", [])]
    print(f"✅ [规划] 生成 {len(queries)} 个搜索查询")

    return {**state, "search_queries": queries, "status": "research_planned"}
