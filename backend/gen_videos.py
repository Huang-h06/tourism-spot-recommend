"""生成5个城市的简单旅游宣传视频"""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import imageio

VIDEO_DIR = os.path.join(os.path.dirname(__file__), "static", "videos")
os.makedirs(VIDEO_DIR, exist_ok=True)

# 每个城市的视频配置
cities = [
    {"name": "chengdu", "label": "成都", "sub": "天府之国 · 熊猫故乡", "color": (220, 80, 60)},
    {"name": "chongqing", "label": "重庆", "sub": "山城雾都 · 火锅之都", "color": (200, 60, 40)},
    {"name": "qingdao", "label": "青岛", "sub": "帆船之都 · 碧海蓝天", "color": (30, 120, 200)},
    {"name": "shanghai", "label": "上海", "sub": "东方明珠 · 国际都市", "color": (40, 80, 180)},
    {"name": "nanjing", "label": "南京", "sub": "六朝古都 · 金陵胜地", "color": (100, 60, 140)},
]

W, H = 640, 360
FPS = 24
DURATION = 5  # 5 seconds
TOTAL_FRAMES = FPS * DURATION

# 尝试加载中文字体
font_paths = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",    # 黑体
    "C:/Windows/Fonts/simsun.ttc",    # 宋体
]


def get_font(size):
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except:
                continue
    return ImageFont.load_default()


def create_video(city):
    filepath = os.path.join(VIDEO_DIR, f"{city['name']}.mp4")
    if os.path.exists(filepath) and os.path.getsize(filepath) > 1000:
        print(f"  [跳过] {city['name']}.mp4 已存在")
        return

    print(f"  [生成] {city['label']}...")
    writer = imageio.get_writer(filepath, fps=FPS, format='ffmpeg', codec='libx264', quality=8)
    
    font_big = get_font(52)
    font_small = get_font(22)
    font_tiny = get_font(16)
    
    r, g, b = city["color"]
    
    for i in range(TOTAL_FRAMES):
        # 创建渐变背景
        progress = i / TOTAL_FRAMES
        
        # 背景色动画：从深到浅再回到深
        brightness = 0.5 + 0.3 * np.sin(progress * np.pi * 2)
        bg_r = int(r * brightness)
        bg_g = int(g * brightness)
        bg_b = int(b * brightness)
        
        img = Image.new("RGB", (W, H), (bg_r, bg_g, bg_b))
        draw = ImageDraw.Draw(img)
        
        # 装饰圆点
        for j in range(20):
            cx = int((W * (j * 37 + i * 2) % W))
            cy = int((H * (j * 53 + i * 3) % H))
            radius = 2 + int(3 * np.sin(progress * 5 + j))
            alpha = 40 + int(20 * np.sin(progress * 3 + j))
            dot_color = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
            draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=dot_color)
        
        # 主标题
        title = city["label"]
        bbox = draw.textbbox((0, 0), title, font=font_big)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # 弹跳动画
        y_offset = int(10 * np.sin(progress * np.pi * 2))
        tx = (W - tw) // 2
        ty = (H - th) // 2 - 30 + y_offset
        
        # 文字阴影
        draw.text((tx + 2, ty + 2), title, fill=(0, 0, 0, 100), font=font_big)
        draw.text((tx, ty), title, fill=(255, 255, 255), font=font_big)
        
        # 副标题
        sub = city["sub"]
        bbox2 = draw.textbbox((0, 0), sub, font=font_small)
        sw, sh = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        sx = (W - sw) // 2
        sy = ty + th + 20
        draw.text((sx + 1, sy + 1), sub, fill=(0, 0, 0, 80), font=font_small)
        draw.text((sx, sy), sub, fill=(255, 255, 240), font=font_small)
        
        # 进度条
        bar_w = int(W * 0.4)
        bar_h = 3
        bar_x = (W - bar_w) // 2
        bar_y = H - 40
        filled = int(bar_w * progress)
        draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], fill=(255, 255, 255, 60))
        draw.rectangle([bar_x, bar_y, bar_x + filled, bar_y + bar_h], fill=(255, 255, 255))
        
        # 旅游宣传文字
        tag = "China Tourism"
        bbox3 = draw.textbbox((0, 0), tag, font=font_tiny)
        tw3, th3 = bbox3[2] - bbox3[0], bbox3[3] - bbox3[1]
        draw.text(((W - tw3) // 2, bar_y + 12), tag, fill=(255, 255, 255, 150), font=font_tiny)
        
        frame = np.array(img)
        writer.append_data(frame)
    
    writer.close()
    size_kb = os.path.getsize(filepath) / 1024
    print(f"    完成! {size_kb:.0f}KB")


if __name__ == "__main__":
    print("生成城市旅游视频...")
    for city in cities:
        create_video(city)
    print("全部完成!")
