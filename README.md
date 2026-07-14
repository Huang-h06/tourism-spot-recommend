# 旅游景点推荐系统

前后端全栈项目，支持云端 PostgreSQL（Supabase）和本地 SQLite 两套数据库方案，默认使用 Supabase。

## 项目功能总览

| 功能模块 | 说明 |
|----------|------|
| 景点列表 | 首页 4 列网格展示全部景点，支持城市、标签模糊筛选 |
| 景点详情 | 单景点完整信息 + 关联视频播放 |
| 景点推荐 | 首页顶部横向滚动推荐卡片，基于标签相似匹配 |
| 视频播放 | 详情页加载当前景点关联的 mp4 短视频，支持播放/暂停 |
| 搜索筛选 | 按城市名称、标签关键词模糊搜索 |

## 技术栈

- **后端框架**：Flask 2.3.3
- **云数据库（默认）**：Supabase (PostgreSQL)
- **本地数据库（备选）**：SQLite（`db_sqlite.py`）
- **跨域支持**：Flask-CORS
- **环境变量**：python-dotenv
- **前端**：原生 HTML + CSS + JavaScript

## 数据库方案

### 方案 A：Supabase 云端数据库（默认，推荐）

1. 在项目根目录创建 `.env` 文件：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
```

2. 在 Supabase SQL Editor 中执行建表和初始数据脚本（确保已创建 `spots` 和 `videos` 两张表）。

3. `app.py` 默认导入 `db_supabase`，无需额外配置。

4. 注意：Supabase 需开启表的 RLS 读取策略，否则 anon key 无法读取数据：

```sql
CREATE POLICY "Allow anonymous read" ON public.spots FOR SELECT USING (true);
CREATE POLICY "Allow anonymous read" ON public.videos FOR SELECT USING (true);
```

### 方案 B：SQLite 本地数据库（备选）

1. 手动初始化本地数据库：

```bash
cd backend
python db_sqlite.py
```

2. 修改 `app.py` 第 4-5 行：

```python
import db_sqlite as db
# import db_supabase as db
```

3. 启动项目即可使用本地 `tourism.db`。

## 后端启动

```bash
cd backend
pip install -r requirements.txt
python app.py
```

访问 http://127.0.0.1:5000/

## 完整 API 清单

| 路由 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/` | GET | - | 首页，渲染景点列表 |
| `/detail` | GET | `?id=` | 详情页，展示单景点信息+视频 |
| `/api/spots` | GET | `?city=` `?tag=` | 景点列表，支持城市、标签模糊筛选 |
| `/api/spots/<id>` | GET | - | 根据 ID 获取景点详情 |
| `/api/recommend` | GET | `?tag=自然风光` | 根据标签推荐相似景点 |
| `/api/videos` | GET | - | 获取全部视频列表 |
| `/api/spots/<id>/videos` | GET | - | 根据景点 ID 获取关联视频 |
| `/api/videos/<id>` | GET | - | 根据视频 ID 获取视频详情 |

## 静态资源目录

```
backend/static/
├── images/          # 景点封面图片（10张：xihu, gugong, zhangjiajie, gulangyu, lijiang, xizang, xinjiang, chengdu, chongqing, qingdao）
└── videos/          # 景点短视频（7个：xihu, gugong, zhangjiajie, xiamen, lijiang, xizang, xinjiang）
```

## 景点数据

| ID | 名称 | 城市 | 等级 | 标签 |
|----|------|------|------|------|
| 1 | 西湖 | 杭州 | 5A | 自然风光 |
| 2 | 故宫 | 北京 | 5A | 人文古迹 |
| 3 | 张家界 | 张家界 | 5A | 自然风光 |
| 4 | 鼓浪屿 | 厦门 | 5A | 海岛休闲 |
| 5 | 丽江 | 丽江 | 5A | 古城风光 |
| 6 | 西藏 | 拉萨 | 5A | 高原圣地 |
| 7 | 新疆 | 乌鲁木齐 | 5A | 西域风情 |
| 8 | 成都 | 成都 | 5A | 休闲美食 |
| 9 | 重庆 | 重庆 | 5A | 山城夜景 |
| 10 | 青岛 | 青岛 | 5A | 海滨风光 |
