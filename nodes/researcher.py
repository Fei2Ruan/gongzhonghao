"""节点3: 执行搜索并整理资料"""
import os
from openai import OpenAI
from tools.search_tool import deep_search


def get_client():
    return OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )


def researcher_node(state: dict) -> dict:
    queries = state.get("search_queries", [])
    print(f"🔎 [研究] 执行 {len(queries)} 个搜索查询...")

    all_results = []
    for i, query in enumerate(queries):
        print(f"   [{i+1}/{len(queries)}] 搜索: {query}")
        results = deep_search(query, max_results=5)
        for r in results:
            if r.get("type") != "error" and r.get("content"):
                all_results.append({
                    "query": query,
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:600],
                    "url": r.get("url", ""),
                })

    print("📝 [研究] 整理资料摘要...")
    raw_text = "\n\n".join(
        f"【来源: {r['title']}】\n{r['content']}\n链接: {r['url']}"
        for r in all_results[:20]
    )

    client = get_client()
    summary_prompt = f"""请将以下搜索资料整理成结构化的写作素材，供撰写公众号文章使用。

选题：{state['topic']}
切入角度：{state.get('topic_angle', '')}

原始资料：
{raw_text}

请整理为：
1. 核心事实与数据（带来源）
2. 相关案例与故事
3. 专家观点与理论
4. 历史背景与文化关联
5. 争议与反思

保留重要引用和数据来源，去除重复内容。"""

    resp = client.chat.completions.create(
        model="deepseek-chat",
        max_tokens=3000,
        messages=[{"role": "user", "content": summary_prompt}],
    )
    summary = resp.choices[0].message.content.strip()
    print(f"✅ [研究] 资料整理完成，共 {len(all_results)} 条原始资料")

    return {
        **state,
        "research_results": all_results,
        "research_summary": summary,
        "status": "research_done",
    }
