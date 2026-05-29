"""图片搜索工具 - 支持 Unsplash / Pexels，为文章配图提供真实图片"""
import os
import time
import requests
from typing import Optional
from functools import lru_cache


# 图片缓存：{keyword: url}
_image_cache: dict[str, str] = {}


def _unsplash_search(keyword: str, orientation: str = "landscape") -> Optional[str]:
    """Unsplash 搜图，返回图片 URL"""
    access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    if not access_key:
        return None

    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": keyword,
        "per_page": 1,
        "orientation": orientation,
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
    return None


def _pexels_search(keyword: str, orientation: str = "landscape") -> Optional[str]:
    """Pexels 搜图，返回图片 URL"""
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return None

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {
        "query": keyword,
        "per_page": 1,
        "orientation": orientation,
    }
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        data = resp.json()
        photos = data.get("photos", [])
        if photos:
            return photos[0]["src"]["large"]
    except Exception:
        pass
    return None


def search_image(keyword: str, orientation: str = "landscape") -> str:
    """搜索图片，优先级：Unsplash > Pexels > picsum 占位图

    Returns:
        图片 URL
    """
    # 去掉过长的关键词（保留前50个字符做搜索）
    search_key = keyword.strip()[:50]

    # 检查缓存
    if search_key in _image_cache:
        print(f"   📦 使用缓存图片: {search_key[:30]}...")
        return _image_cache[search_key]

    # 尝试 Unsplash
    img_url = _unsplash_search(search_key, orientation)
    if img_url:
        print(f"   🖼️  Unsplash 配图: {search_key[:30]}...")
        _image_cache[search_key] = img_url
        return img_url

    # 尝试 Pexels
    img_url = _pexels_search(search_key, orientation)
    if img_url:
        print(f"   🖼️  Pexels 配图: {search_key[:30]}...")
        _image_cache[search_key] = img_url
        return img_url

    # 兜底：picsum 占位图（用关键词哈希保证同一关键词总是同一张）
    seed = abs(hash(search_key)) % 1000
    fallback_url = f"https://picsum.photos/seed/{seed}/1200/675"
    print(f"   ⚠️  未配置图片API，使用占位图: {search_key[:30]}...")
    _image_cache[search_key] = fallback_url
    return fallback_url


def clear_cache():
    """清空图片缓存"""
    _image_cache.clear()
