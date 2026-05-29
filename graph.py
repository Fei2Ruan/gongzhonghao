"""LangGraph 图定义 - 银渐层沉思录智能体"""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, START, END

from nodes.topic_selector import topic_selector_node
from nodes.research_planner import research_planner_node
from nodes.researcher import researcher_node
from nodes.writer import writer_node
from nodes.formatter import formatter_node
from nodes.validator import validator_node
from nodes.publisher import publisher_node


class ArticleState(TypedDict, total=False):
    # 输入
    used_topics: list

    # 选题
    topic: str
    topic_angle: str
    topic_reason: str
    topic_keywords: list

    # 研究
    search_queries: list
    research_results: list
    research_summary: str

    # 写作
    article_title: str
    article_content: str
    article_digest: str

    # 排版
    html_content: str
    format_retry_count: int
    validation_errors: list

    # 发布
    thumb_media_id: str
    draft_media_id: str
    publish_job_id: str

    # 状态
    error: str
    status: str


def should_reformat(state: ArticleState) -> str:
    """校验后的路由：失败且未超重试次数则重新排版，否则继续发布"""
    if state.get("status") == "format_failed":
        return "formatter"
    return "publisher"


def build_graph() -> StateGraph:
    graph = StateGraph(ArticleState)

    graph.add_node("topic_selector", topic_selector_node)
    graph.add_node("research_planner", research_planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("formatter", formatter_node)
    graph.add_node("validator", validator_node)
    graph.add_node("publisher", publisher_node)

    graph.add_edge(START, "topic_selector")
    graph.add_edge("topic_selector", "research_planner")
    graph.add_edge("research_planner", "researcher")
    graph.add_edge("researcher", "writer")
    graph.add_edge("writer", "formatter")
    graph.add_edge("formatter", "validator")
    graph.add_conditional_edges(
        "validator",
        should_reformat,
        {"formatter": "formatter", "publisher": "publisher"},
    )
    graph.add_edge("publisher", END)

    return graph.compile()


# 单例
agent = build_graph()
