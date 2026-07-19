"""下载成都、重庆、青岛、上海、南京的旅游景点视频"""
import os
import sys
import re
import json
import requests
from urllib.parse import quote

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

cities = {
    "chengdu": "成都城市风光航拍",
    "chongqing": "重庆洪崖洞夜景",
    "qingdao": "青岛海滨栈桥",
    "shanghai": "上海外滩陆家嘴",
    "nanjing": "南京夫子庙秦淮河",
}

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "static", "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Referer": "https://www.pexels.com/",
}


def download_from_pexels_scrape():
    """从 Pexels 网站抓取视频下载链接"""
    for filename, keyword in cities.items():
        filepath = os.path.join(VIDEO_DIR, f"{filename}.mp4")
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            print(f"[跳过] {filename}.mp4 已存在")
            continue

        print(f"[搜索 Pexels] {keyword}")
        search_url = f"https://www.pexels.com/zh-cn/search/videos/{quote(keyword)}/"
        
        try:
            resp = requests.get(search_url, headers=HEADERS, timeout=30)
            if resp.status_code != 200:
                print(f"  状态码: {resp.status_code}")
                continue

            # 从 HTML 中提取视频数据
            html = resp.text
            
            # Pexels 用 __NEXT_DATA__ 或直接在页面中嵌入视频数据
            # 尝试从 script 标签中提取 JSON
            patterns = [
                r'<script[^>]*type="application/json"[^>]*>(.*?)</script>',
                r'<script[^>]*>\s*window\.__PRELOADED_STATE__\s*=\s*({.*?});\s*</script>',
                r'"video_files"\s*:\s*(\[.*?\])',
            ]
            
            video_url = None
            for pattern in patterns:
                matches = re.findall(pattern, html, re.DOTALL)
                for match in matches:
                    try:
                        data = json.loads(match) if match.startswith("{") else match
                        # 尝试各种 JSON 结构提取视频链接
                        text = json.dumps(data) if isinstance(data, (dict, list)) else str(match)
                        links = re.findall(r'https?://[^"\']+\.mp4[^"\']*', text)
                        if links:
                            video_url = links[0]
                            break
                    except:
                        continue
                if video_url:
                    break

            if not video_url:
                # 简单正则提取所有 mp4 链接
                all_mp4 = re.findall(r'(https?://[^\s"\'<>]+\.mp4[^\s"\'<>]*)', html)
                if all_mp4:
                    video_url = all_mp4[0]

            if video_url:
                print(f"[下载] {filename}.mp4")
                video_data = requests.get(video_url, headers=HEADERS, timeout=120)
                if video_data.status_code == 200 and len(video_data.content) > 10000:
                    with open(filepath, "wb") as f:
                        f.write(video_data.content)
                    size_mb = len(video_data.content) / (1024 * 1024)
                    print(f"  完成! {size_mb:.1f}MB")
                    continue
                else:
                    print(f"  下载失败: size={len(video_data.content)}")
            else:
                print(f"  未找到视频链接")

        except Exception as e:
            print(f"  错误: {e}")


def download_from_pexels_api():
    """使用 Pexels API 下载（需要 API Key）"""
    API_KEY = os.environ.get("PEXELS_API_KEY", "").strip()
    if not API_KEY:
        return False

    headers = {"Authorization": API_KEY}
    
    for filename, keyword in cities.items():
        filepath = os.path.join(VIDEO_DIR, f"{filename}.mp4")
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            print(f"[跳过] {filename}.mp4 已存在")
            continue

        print(f"[Pexels API] {keyword}")
        try:
            url = f"https://api.pexels.com/videos/search?query={quote(keyword)}&per_page=5&orientation=landscape&size=medium"
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code != 200:
                print(f"  API错误: {resp.status_code}")
                continue

            data = resp.json()
            videos = data.get("videos", [])
            if not videos:
                print(f"  无结果")
                continue

            # 找第一个带合适分辨率 mp4 的视频
            for video in videos:
                video_files = video.get("video_files", [])
                best = None
                for vf in video_files:
                    if vf.get("file_type") != "video/mp4":
                        continue
                    w, h = vf.get("width", 0), vf.get("height", 0)
                    if 480 <= w <= 1920:
                        if best is None or w > best[0]:
                            best = (w, vf)
                if best:
                    durl = best[1]["link"]
                    print(f"[下载] {filename}.mp4 ({best[0]}p)")
                    vresp = requests.get(durl, timeout=120)
                    if vresp.status_code == 200 and len(vresp.content) > 10000:
                        with open(filepath, "wb") as f:
                            f.write(vresp.content)
                        print(f"  完成! {len(vresp.content)/(1024*1024):.1f}MB")
                        break
                    else:
                        print(f"  下载失败")
        except Exception as e:
            print(f"  错误: {e}")
    return True


def download_from_sample_videos():
    """下载一些通用的样本风景视频作为备选"""
    # 使用公开的免费样本视频
    sample_urls = {
        "chengdu": "https://cdn.coverr.co/videos/coverr-city-traffic-at-night-2233/1080p.mp4",
        "chongqing": "https://cdn.coverr.co/videos/coverr-aerial-view-of-city-at-night-188/1080p.mp4",
        "qingdao": "https://cdn.coverr.co/videos/coverr-waves-crashing-on-the-shore-9476/1080p.mp4",
        "shanghai": "https://cdn.coverr.co/videos/coverr-city-skyline-at-sunset-9474/1080p.mp4",
        "nanjing": "https://cdn.coverr.co/videos/coverr-ancient-temple-in-the-mountains-1572/1080p.mp4",
    }
    
    for filename, url in sample_urls.items():
        filepath = os.path.join(VIDEO_DIR, f"{filename}.mp4")
        if os.path.exists(filepath) and os.path.getsize(filepath) > 10000:
            print(f"[跳过] {filename}.mp4 已存在")
            continue
        
        print(f"[下载 Coverr] {filename}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=60)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open(filepath, "wb") as f:
                    f.write(resp.content)
                print(f"  完成! {len(resp.content)/(1024*1024):.1f}MB")
            else:
                print(f"  失败: HTTP {resp.status_code}, size={len(resp.content)}")
        except Exception as e:
            print(f"  错误: {e}")


if __name__ == "__main__":
    print("=" * 50)
    print("旅游景点视频下载工具")
    print("=" * 50)

    # 方案1: 尝试 Pexels API
    if os.environ.get("PEXELS_API_KEY"):
        print("\n>>> 方案1: Pexels API")
        download_from_pexels_api()
    else:
        print("\n[提示] 设置 PEXELS_API_KEY 可下载高质量视频")
        print("  免费获取: https://www.pexels.com/api/")

    # 方案2: 尝试抓取 Pexels 网站
    print("\n>>> 方案2: Pexels 网站抓取")
    download_from_pexels_scrape()

    # 方案3: 下载通用风景视频
    print("\n>>> 方案3: 通用风景视频")
    download_from_sample_videos()

    # 显示结果
    print("\n" + "=" * 50)
    print("下载结果:")
    all_ok = True
    for filename in cities:
        filepath = os.path.join(VIDEO_DIR, f"{filename}.mp4")
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  [OK] {filename}.mp4 ({size_mb:.1f}MB)")
        else:
            print(f"  [FAIL] {filename}.mp4 (not downloaded)")
            all_ok = False

    if not all_ok:
        print("\n请手动在 Pexels/Pixabay 下载视频放到 static/videos/ 目录")
