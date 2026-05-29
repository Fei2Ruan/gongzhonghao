"""Tavily搜索工具封装"""
import os
from datetime import datetime
from typing import Optional
from tavily import TavilyClient


def get_tavily_client() -> TavilyClient:
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("TAVILY_API_KEY 未配置")
    return TavilyClient(api_key=api_key)


def search(query: str, max_results: int = 5, search_depth: str = "basic", days: int = 0) -> list[dict]:
    """执行搜索，返回结果列表。days=0 表示不限时间"""
    client = get_tavily_client()
    kwargs = {
        "query": query,
        "max_results": max_results,
        "search_depth": search_depth,
        "include_answer": True,
        "include_raw_content": False,
    }
    if days > 0:
        kwargs["days"] = days

    try:
        response = client.search(**kwargs)
        results = []
        if response.get("answer"):
            results.append({"type": "answer", "content": response["answer"], "url": ""})
        for r in response.get("results", []):
            results.append({
                "type": "article",
                "title": r.get("title", ""),
                "content": r.get("content", ""),
                "url": r.get("url", ""),
                "score": r.get("score", 0),
            })
        return results
    except Exception as e:
        return [{"type": "error", "content": str(e), "url": ""}]


def search_trending_topics() -> list[dict]:
    """搜索当前热点话题"""
    year = datetime.now().year
    today = datetime.now().strftime("%Y年%m月%d日")
    queries = [
        f"今日热点新闻 社会 {today}",
        f"{year}年 微博热搜 头条",
        f"知乎热榜 今日话题 {today}",
        f"抖音热搜 热门话题 {today}",
        f"抖音热榜 {today}",
    ]
    all_results = []
    client = get_tavily_client()
    for q in queries:
        try:
            resp = client.search(q, max_results=5, search_depth="basic")
            for r in resp.get("results", []):
                all_results.append({
                    "title": r.get("title", ""),
                    "content": r.get("content", "")[:300],
                    "url": r.get("url", ""),
                })
        except Exception:
            continue
    return all_results


def deep_search(query: str, max_results: int = 8, days: int = 0) -> list[dict]:
    """深度搜索，用于资料收集"""
    return search(query, max_results=max_results, search_depth="advanced", days=days)
