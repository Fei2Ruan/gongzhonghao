"""节点7: 发布到微信公众号"""
import re
import os
from tools.wechat_api import (
    get_access_token,
    get_unsplash_image_url,
    upload_image_from_url,
    create_draft,
    publish_draft,
    poll_publish_status,
)


def publisher_node(state: dict) -> dict:
    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    draft_only = os.getenv("DRAFT_ONLY", "false").lower() == "true"

    if dry_run:
        print("🚫 [发布] DRY_RUN模式，跳过实际发布")
        return {**state, "status": "dry_run_complete", "publish_job_id": "dry_run"}

    print("🚀 [发布] 开始发布到微信公众号...")

    try:
        # 1. 获取access_token
        print("   获取access_token...")
        token = get_access_token()

        # 2. 获取封面图
        keywords = state.get("topic_keywords", [state.get("topic", "nature")])
        keyword = keywords[0] if keywords else "abstract"
        print(f"   获取封面图（关键词: {keyword}）...")
        img_url = get_unsplash_image_url(keyword)

        # 3. 上传封面图
        print("   上传封面图到微信素材库...")
        thumb_media_id = upload_image_from_url(img_url, token)

        # 4. 提取body内容（微信只需要 <body> 内的内容）
        html = state["html_content"]
        if "<body" in html:
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL)
            wechat_content = body_match.group(1).strip() if body_match else html
        else:
            wechat_content = html

        # 5. 创建草稿
        print("   创建草稿...")
        draft_media_id = create_draft(
            access_token=token,
            title=state["article_title"],
            content=wechat_content,
            digest=state.get("article_digest", ""),
            thumb_media_id=thumb_media_id,
        )
        print(f"✅ [草稿] 草稿创建成功！media_id: {draft_media_id}")

        if draft_only:
            print("📝 [发布] DRAFT_ONLY模式，草稿已保存，请登录公众号后台手动发布")
            return {
                **state,
                "thumb_media_id": thumb_media_id,
                "draft_media_id": draft_media_id,
                "publish_job_id": "",
                "status": "draft_saved",
            }

        # 6. 自动发布
        print("   提交发布...")
        publish_id = publish_draft(token, draft_media_id)

        # 7. 轮询状态
        print("   等待发布结果...")
        result = poll_publish_status(token, publish_id)

        if result["success"]:
            print(f"✅ [发布] 发布成功！publish_id: {publish_id}")
            return {
                **state,
                "thumb_media_id": thumb_media_id,
                "draft_media_id": draft_media_id,
                "publish_job_id": publish_id,
                "status": "published",
            }
        else:
            print(f"❌ [发布] 发布失败: {result}")
            return {**state, "error": str(result), "status": "publish_failed"}

    except Exception as e:
        print(f"❌ [发布] 异常: {e}")
        return {**state, "error": str(e), "status": "publish_failed"}

