"""节点6: 校验格式"""
import re


def validator_node(state: dict) -> dict:
    print("✔️  [校验] 检查HTML格式...")
    html = state.get("html_content", "")
    errors = []

    # 基础检查
    if len(html) < 500:
        errors.append("HTML内容过短（<500字符）")
    if "<script" in html.lower():
        errors.append("包含script标签（微信不支持）")
    if 'class="' in html:
        errors.append("包含class属性（微信不支持外部CSS）")
    if "<link" in html.lower():
        errors.append("包含link标签（微信不支持）")

    # 检查是否有内容
    text_content = re.sub(r'<[^>]+>', '', html)
    text_content = text_content.replace('&nbsp;', ' ').strip()
    if len(text_content) < 1000:
        errors.append(f"文字内容过少（{len(text_content)}字）")

    # 检查标题
    if not state.get("article_title"):
        errors.append("缺少文章标题")

    # 检查摘要
    if not state.get("article_digest"):
        errors.append("缺少文章摘要")

    retry_count = state.get("format_retry_count", 0)

    if errors:
        print(f"⚠️  [校验] 发现问题: {errors}")
        if retry_count < 2:
            print(f"   将重新排版（第{retry_count + 1}次重试）")
            return {
                **state,
                "format_retry_count": retry_count + 1,
                "validation_errors": errors,
                "status": "format_failed",
            }
        else:
            print("   已达最大重试次数，继续发布")

    print("✅ [校验] 格式检查通过")
    return {**state, "validation_errors": [], "status": "validated"}
