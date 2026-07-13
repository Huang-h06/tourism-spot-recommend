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
            ("西湖", "杭州", "5A", "自然风光", "西湖位于浙江省杭州市西湖区，是中国十大风景名胜之一，以湖光山色和人文景观著称。景区总面积约49平方千米，湖面面积6.38平方千米，主要有断桥残雪、雷峰夕照、三潭印月、苏堤春晓、平湖秋月等著名景点。西湖三面环山，一面靠城，山水与城市融为一体，被誉为'天下西湖三十六，其中最美在杭州'。"),
            ("故宫", "北京", "5A", "人文古迹", "故宫又名紫禁城，位于北京市中心，是明清两代的皇家宫殿，始建于明永乐四年（1406年），历时14年建成。故宫占地72万平方米，建筑面积约15万平方米，共有大小宫殿七十多座、房屋九千余间，是世界上现存规模最大、保存最为完整的木质结构古建筑群之一。"),
            ("张家界", "张家界", "5A", "自然风光", "张家界国家森林公园位于湖南省张家界市武陵源区，是中国第一个国家森林公园。景区以石英砂岩峰林地貌著称，三千奇峰拔地而起，形态各异，被誉为'扩大的盆景，缩小的仙境'。电影《阿凡达》中的悬浮山原型便取材于张家界哈利路亚山。主要景点包括黄石寨、金鞭溪、袁家界、天子山等。"),
            ("鼓浪屿", "厦门", "5A", "海岛休闲", "鼓浪屿位于福建省厦门市思明区，是一座面积仅1.88平方公里的海上花园小岛。岛上气候宜人，四季如春，钢琴拥有密度居全国前列，素有'海上花园'和'音乐之岛'的美誉。岛上保存有大量中西合璧的历史建筑，如八卦楼、日光岩、菽庄花园、钢琴博物馆等，2017年被列入世界文化遗产名录。"),
            ("丽江", "丽江", "5A", "古城风光", "丽江古城位于云南省丽江市古城区，又名大研古城，始建于宋末元初，距今已有八百多年历史。古城依山傍水，纳西族传统建筑错落有致，小桥流水、石板古巷别具韵味。这里有世界文化遗产丽江古城、玉龙雪山、泸沽湖、拉市海等众多著名景点，是纳西族东巴文化的发源地和传承地。"),
            ("西藏", "拉萨", "5A", "高原圣地", "西藏位于中国西南边陲，平均海拔4000米以上，素有'世界屋脊'之称。首府拉萨是藏传佛教圣地，布达拉宫、大昭寺、罗布林卡等历史建筑见证了悠久的藏文化。这里有雄伟的喜马拉雅山脉、神圣的冈仁波齐峰、圣湖纳木错和羊卓雍错，以及辽阔的藏北草原，是无数人心中的朝圣之地与旅行梦想。"),
            ("新疆", "乌鲁木齐", "5A", "西域风情", "新疆维吾尔自治区位于中国西北边陲，是中国陆地面积最大的省级行政区，地域辽阔、风光多样。这里有天山天池、喀纳斯湖、吐鲁番火焰山、塔克拉玛干沙漠、那拉提草原、赛里木湖等壮美景观。作为古丝绸之路的重要通道，新疆融合了多元民族文化，瓜果飘香、歌舞动人，是体验西域风情的绝佳目的地。")
        ]
        cursor.executemany('INSERT INTO spots(name,city,level,tag,desc) VALUES(?,?,?,?,?)', init_data)
    # 判断视频表是否有数据，没有则插入初始视频（本地静态文件路径）
    cursor.execute("SELECT COUNT(*) FROM videos")
    video_count = cursor.fetchone()[0]
    if video_count == 0:
        video_data = [
            (1, "西湖十景·航拍全景", "/static/videos/xihu.mp4", "/static/images/xihu.jpg", "08:30"),
            (2, "故宫600年·皇城中轴线", "/static/videos/gugong.mp4", "/static/images/gugong.jpg", "12:15"),
            (3, "张家界·峰林云海", "/static/videos/zhangjiajie.mp4", "/static/images/zhangjiajie.jpg", "10:00"),
            (4, "鼓浪屿·文艺慢生活", "/static/videos/xiamen.mp4", "/static/images/gulangyu.jpg", "07:25"),
            (5, "丽江古城·玉龙雪山", "/static/videos/lijiang.mp4", "/static/images/lijiang.jpg", "05:30"),
            (6, "西藏·世界屋脊", "/static/videos/xizang.mp4", "/static/images/xizang.jpg", "06:20"),
            (7, "新疆·大美西域", "/static/videos/xinjiang.mp4", "/static/images/xinjiang.jpg", "06:10")
        ]
        cursor.executemany('INSERT INTO videos(spot_id,title,url,cover,duration) VALUES(?,?,?,?,?)', video_data)
    conn.commit()
    conn.close()

# 查询所有景点（支持城市、标签模糊筛选）
def query_spots(city="", tag=""):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    sql = "SELECT * FROM spots WHERE 1=1"
    params = []
    if city:
        sql += " AND city LIKE ?"
        params.append(f"%{city}%")
    if tag:
        sql += " AND tag LIKE ?"
        params.append(f"%{tag}%")
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