import sqlite3
import os

DB_FILE = "tourism.db"

# 初始化数据表
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # 创建景点表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS spots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city TEXT,
        level TEXT,
        tag TEXT,
        desc TEXT
    )
    ''')
    # 创建视频表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        spot_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        cover TEXT,
        duration TEXT,
        FOREIGN KEY (spot_id) REFERENCES spots(id)
    )
    ''')
    # 判断表内是否有数据，没有则插入初始景点
    cursor.execute("SELECT COUNT(*) FROM spots")
    count = cursor.fetchone()[0]
    if count == 0:
        init_data = [
            ("西湖", "杭州", "5A", "自然风光", "西湖十景，江南水乡代表"),
            ("故宫", "北京", "5A", "人文古迹", "明清皇家宫殿建筑群"),
            ("张家界", "张家界", "5A", "自然风光", "石英砂岩峰林地貌"),
            ("鼓浪屿", "厦门", "5A", "海岛休闲", "文艺海岛，万国建筑")
        ]
        cursor.executemany('INSERT INTO spots(name,city,level,tag,desc) VALUES(?,?,?,?,?)', init_data)
    # 判断视频表是否有数据，没有则插入初始视频
    cursor.execute("SELECT COUNT(*) FROM videos")
    video_count = cursor.fetchone()[0]
    if video_count == 0:
        video_data = [
            (1, "西湖十景·航拍全景", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4", "https://picsum.photos/seed/xihu/640/360", "08:30"),
            (1, "西湖雪景·冬日断桥", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4", "https://picsum.photos/seed/xihu2/640/360", "05:20"),
            (2, "故宫600年·皇城中轴线", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4", "https://picsum.photos/seed/gugong/640/360", "12:15"),
            (2, "故宫珍宝馆探秘", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerJoyrides.mp4", "https://picsum.photos/seed/gugong2/640/360", "09:45"),
            (3, "张家界·峰林云海", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerMeltdowns.mp4", "https://picsum.photos/seed/zjj/640/360", "10:00"),
            (3, "张家界玻璃栈道挑战", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4", "https://picsum.photos/seed/zjj2/640/360", "06:40"),
            (4, "鼓浪屿·文艺慢生活", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WeAreGoingOnBullrun.mp4", "https://picsum.photos/seed/gly/640/360", "07:25"),
            (4, "鼓浪屿万国建筑巡礼", "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4", "https://picsum.photos/seed/gly2/640/360", "11:10")
        ]
        cursor.executemany('INSERT INTO videos(spot_id,title,url,cover,duration) VALUES(?,?,?,?,?)', video_data)
    conn.commit()
    conn.close()

# 查询所有景点（支持筛选）
def query_spots(city="", level=""):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = "SELECT * FROM spots WHERE 1=1"
    params = []
    if city:
        sql += " AND city LIKE ?"
        params.append(f"%{city}%")
    if level:
        sql += " AND level = ?"
        params.append(level)
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    result = [dict(row) for row in rows]
    conn.close()
    return result

# 根据id查询单个景点
def get_spot_by_id(spot_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spots WHERE id=?", (spot_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# 根据标签推荐景点
def recommend_by_tag(tag):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spots WHERE tag=?", (tag,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 获取所有视频
def get_all_videos():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 根据景点ID获取视频列表
def get_videos_by_spot(spot_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos WHERE spot_id=? ORDER BY id", (spot_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# 根据视频ID获取单个视频
def get_video_by_id(video_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM videos WHERE id=?", (video_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

# 程序启动自动建表初始化
init_db()