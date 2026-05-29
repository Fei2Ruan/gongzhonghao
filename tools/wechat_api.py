"""微信公众号API封装（基于wechatpy）"""
import os
import time
import requests
from typing import Optional


def get_access_token() -> str:
    """获取微信access_token"""
    app_id = os.getenv("WECHAT_APP_ID")
    app_secret = os.getenv("WECHAT_APP_SECRET")
    if not app_id or not app_secret:
        raise ValueError("WECHAT_APP_ID 或 WECHAT_APP_SECRET 未配置")

    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {"grant_type": "client_credential", "appid": app_id, "secret": app_secret}
    resp = requests.get(url, params=params, timeout=10)
    data = resp.json()
    if "access_token" not in data:
        raise RuntimeError(f"获取access_token失败: {data}")
    return data["access_token"]


def upload_image_from_url(image_url: str, access_token: str) -> str:
    """从URL下载图片并上传到微信素材库，返回thumb_media_id"""
    # 下载图片
    img_resp = requests.get(image_url, timeout=15)
    img_resp.raise_for_status()
    content_type = img_resp.headers.get("Content-Type", "image/jpeg")
    ext = "jpg" if "jpeg" in content_type else content_type.split("/")[-1]

    # 上传到微信
    upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material"
    params = {"access_token": access_token, "type": "thumb"}
    files = {"media": (f"cover.{ext}", img_resp.content, content_type)}
    resp = requests.post(upload_url, params=params, files=files, timeout=30)
    data = resp.json()
    if "media_id" not in data:
        raise RuntimeError(f"上传封面图失败: {data}")
    return data["media_id"]


def get_unsplash_image_url(keyword: str) -> str:
    """从Unsplash获取封面图URL"""
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        # 使用picsum作为fallback
        return "https://picsum.photos/900/500"

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": keyword,
        "per_page": 1,
        "orientation": "landscape",
        "client_id": access_key,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        results = data.get("results", [])
        if results:
            return results[0]["urls"]["regular"]
    except Exception:
        pass
    return "https://picsum.photos/900/500"


def create_draft(
    access_token: str,
    title: str,
    content: str,
    digest: str,
    thumb_media_id: str,
    author: str = "银渐层",
) -> str:
    """创建草稿，返回media_id"""
    url = "https://api.weixin.qq.com/cgi-bin/draft/add"
    params = {"access_token": access_token}
    payload = {
        "articles": [{
            "title": title,
            "author": author,
            "digest": digest,
            "content": content,
            "thumb_media_id": thumb_media_id,
            "need_open_comment": 1,
            "only_fans_can_comment": 0,
        }]
    }
    resp = requests.post(url, params=params, json=payload, timeout=30)
    data = resp.json()
    if "media_id" not in data:
        raise RuntimeError(f"创建草稿失败: {data}")
    return data["media_id"]


def publish_draft(access_token: str, media_id: str) -> str:
    """提交发布，返回publish_id"""
    url = "https://api.weixin.qq.com/cgi-bin/freepublish/submit"
    params = {"access_token": access_token}
    payload = {"media_id": media_id}
    resp = requests.post(url, params=params, json=payload, timeout=30)
    data = resp.json()
    if "publish_id" not in data:
        raise RuntimeError(f"发布失败: {data}")
    return data["publish_id"]


def poll_publish_status(access_token: str, publish_id: str, max_retries: int = 10) -> dict:
    """轮询发布状态"""
    url = "https://api.weixin.qq.com/cgi-bin/freepublish/get"
    params = {"access_token": access_token}
    payload = {"publish_id": publish_id}

    for i in range(max_retries):
        resp = requests.post(url, params=params, json=payload, timeout=10)
        data = resp.json()
        publish_status = data.get("publish_status", -1)
        # 0=发布成功, 1=发布中, 2=原创失败, 3=常规失败, 4=平台审核不通过, 5=成功后用户删除
        if publish_status == 0:
            return {"success": True, "status": publish_status, "data": data}
        if publish_status in (2, 3, 4):
            return {"success": False, "status": publish_status, "data": data}
        time.sleep(3)

    return {"success": False, "status": -1, "data": {"msg": "超时"}}
