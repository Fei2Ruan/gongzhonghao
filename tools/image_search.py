"""图片搜索工具 - 百度实图 > Pexels > Unsplash > 占位图"""
import os
import re
import time
import requests
from typing import Optional
from urllib.parse import quote


_image_cache: dict[str, str] = {}


def _baidu_image_search(keyword: str) -> Optional[str]:
    """百度图片搜索，搜新闻实图（无需 API Key，国内秒开）"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/plain, */*; q=0.01",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Referer": f"https://image.baidu.com/search/index?tn=baiduimage&word={quote(keyword)}",
        "X-Requested-With": "XMLHttpRequest",
    }

    try:
        ts = int(time.time() * 1000)
        url = (
            f"https://image.baidu.com/search/acjson"
            f"?tn=resultjson_com&ipn=rj&ct=201326592&is=&fp=result"
            f"&queryWord={quote(keyword)}&cl=2&lm=-1&ie=utf-8&oe=utf-8"
            f"&word={quote(keyword)}&pn=0&rn=10&{ts}="
        )
        resp = requests.get(url, headers=headers, timeout=10)
        data = resp.json()
        items = data.get("data", [])

        for item in items:
            if not item:
                continue
            # thumbURL 是可直接访问的图片链接
            img_url = item.get("thumbURL") or item.get("middleURL")
            if img_url and img_url.startswith("http"):
                return img_url
    except Exception:
        pass

    return None


def _pexels_search(keyword: str, orientation: str = "landscape") -> Optional[str]:
    """Pexels 搜图"""
    api_key = os.getenv("PEXELS_API_KEY")
    if not api_key:
        return None

    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": api_key}
    params = {"query": keyword, "per_page": 1, "orientation": orientation}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        data = resp.json()
        photos = data.get("photos", [])
        if photos:
            return photos[0]["src"]["large"]
    except Exception:
        pass
    return None


def _unsplash_search(keyword: str, orientation: str = "landscape") -> Optional[str]:
    """Unsplash 搜图"""
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


def search_image(keyword: str, orientation: str = "landscape") -> str:
    """搜索图片，优先级：百度实图 > Pexels > Unsplash > picsum占位图"""
    search_key = keyword.strip()[:50]

    if search_key in _image_cache:
        print(f"   [缓存] {search_key[:30]}...")
        return _image_cache[search_key]

    # 1. 百度图片搜索（新闻实图，无需 API Key，国内最佳）
    img_url = _baidu_image_search(search_key)
    if img_url:
        print(f"   [百度实图] {search_key[:30]}...")
        _image_cache[search_key] = img_url
        return img_url

    # 2. Pexels
    img_url = _pexels_search(search_key, orientation)
    if img_url:
        print(f"   [Pexels] {search_key[:30]}...")
        _image_cache[search_key] = img_url
        return img_url

    # 3. Unsplash
    img_url = _unsplash_search(search_key, orientation)
    if img_url:
        print(f"   [Unsplash] {search_key[:30]}...")
        _image_cache[search_key] = img_url
        return img_url

    # 4. 兜底
    seed = abs(hash(search_key)) % 1000
    fallback_url = f"https://picsum.photos/seed/{seed}/1200/675"
    print(f"   [占位图] {search_key[:30]}...")
    _image_cache[search_key] = fallback_url
    return fallback_url


def clear_cache():
    """清空图片缓存"""
    _image_cache.clear()
