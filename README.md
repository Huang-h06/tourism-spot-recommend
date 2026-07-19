# 旅游景点推荐系统

全栈旅游景点推荐平台，支持景点浏览、评分评论、游记分享、地图定位和后台管理。

## 项目功能总览

| 功能模块 | 说明 |
|----------|------|
| 景点列表 | 首页轮播 Banner（12个景点动态加载）+ 卡片网格，支持城市、标签模糊筛选 |
| 景点详情 | 单景点完整信息、攻略面板、美食画廊、视频播放 |
| 用户系统 | 注册/登录、个人主页（收藏、浏览记录、评论、头像） |
| 评分评论 | 1~5 星评分、发表评论、点赞评论、删除自己的评论 |
| 游记模块 | 游记广场 `/notes`，发布图文游记，关联景点 |
| 地图定位 | Leaflet + 高德瓦片，详情页展示景点经纬度位置 |
| 管理后台 | `/admin`，景点新增/编辑/删除/上下架、用户管理（封禁/角色设置）、评论审核删除 |

## 技术栈

- **后端框架**：Flask 2.3.3
- **云数据库**：Supabase (PostgreSQL)
- **前端**：原生 HTML + CSS + JavaScript（无框架依赖）
- **地图**：Leaflet 1.9.4 + 高德瓦片
- **跨域**：Flask-CORS
- **环境变量**：python-dotenv
- **密码加密**：Werkzeug scrypt
- **部署**：Docker + ECS (Ubuntu 24.04)

## 项目目录结构

```
tourism-spot-recommend/
├── README.md
├── Dockerfile               # Docker 构建配置
├── .env                     # 环境变量（需自行创建，见部署章节）
├── backend/
│   ├── app.py               # Flask 主入口，路由和 API
│   ├── db_supabase.py       # Supabase 数据库操作层
│   ├── db_sqlite.py         # SQLite 备用数据库方案（未启用）
│   ├── migrate.sql          # 数据库迁移脚本
│   ├── requirements.txt     # Python 依赖
│   ├── static/
│   │   ├── images/          # 景点封面图、美食图片
│   │   │   └── foods/       # 12个城市美食图片
│   │   └── videos/          # 短视频素材（Git LFS 管理）
│   └── templates/
│       ├── index.html       # 首页（轮播+卡片列表+筛选）
│       ├── detail.html      # 详情页（攻略+地图+评论+美食）
│       ├── profile.html     # 个人主页
│       ├── notes.html       # 游记广场
│       └── admin.html       # 管理后台
└── docs/                    # 项目文档
```

## 本地开发

### 1. 克隆仓库

> 视频文件使用 Git LFS 管理，请先安装 git-lfs。

```bash
# 安装 Git LFS
# Windows: 下载 https://git-lfs.com/
# macOS: brew install git-lfs
# Linux: apt-get install git-lfs

git lfs install
git clone https://github.com/Huang-h06/tourism-spot-recommend.git
cd tourism-spot-recommend
git lfs pull
```

### 2. 安装 Python 依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
SECRET_KEY=your-secret-key
```

### 4. 初始化数据库

打开 Supabase SQL Editor，将 `backend/migrate.sql` 全部内容粘贴并执行。

可选：将某个用户设为管理员：

```sql
UPDATE users SET role = 'admin' WHERE username = '你的用户名';
```

### 5. 启动项目

```bash
cd backend
python app.py
```

访问 http://127.0.0.1:5000/

---

## ECS 服务器部署（Docker）

### 服务器要求

- Ubuntu 22.04 / 24.04
- 至少 2 vCPU / 2 GiB 内存
- 安全组/防火墙开放 **8080 端口**（TCP 入方向）

### 1. 安装 Docker

```bash
apt-get update && apt-get install -y docker.io git git-lfs
systemctl enable docker --now
```

### 2. 拉取代码

> 视频文件使用 Git LFS，必须先安装 git-lfs 并执行 `git lfs pull`。

```bash
git lfs install
git clone https://github.com/Huang-h06/tourism-spot-recommend.git /opt/tourism-app
cd /opt/tourism-app
git lfs pull
```

### 3. 配置 Supabase 环境变量

在项目根目录创建 `.env` 文件：

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-public-key
```

### 4. 构建并启动

```bash
cd /opt/tourism-app
docker build -t tourism-app .
docker run -d \
  --name tourism-app \
  -p 8080:8080 \
  --restart=always \
  tourism-app:latest
```

### 5. 验证

```bash
curl -s http://localhost:8080 | head -5
```

外网访问：`http://你的服务器IP:8080`

### Docker 日常运维

```bash
# 查看状态
docker ps -a

# 查看日志
docker logs -f tourism-app

# 重启
docker restart tourism-app

# 更新代码并重建
cd /opt/tourism-app
git pull origin main && git lfs pull
docker stop tourism-app && docker rm tourism-app
docker build --no-cache -t tourism-app .
docker run -d --name tourism-app -p 8080:8080 --restart=always tourism-app:latest
```

### 部署常⻅问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 外网访问不通 | 安全组没开放 8080 | 阿里云/腾讯云控制台添加 TCP 8080 入方向规则 |
| 容器反复重启 | `.env` 未进入容器或 SUPABASE_URL 为空 | 确保 `.env` 在项目根目录，或在 Dockerfile 中 COPY |
| 视频只有 132 字节 | 未安装 git-lfs，下载的是 LFS 指针 | 安装 git-lfs 并执行 `git lfs pull` |
| 视频无法播放 | Flask 开发服务器不支持 Range 请求 | 已内置 `/static/videos/` 路由处理 Range 请求 |

---

## 完整 API 文档

## 完整 API 文档

### 统一响应格式

```json
{
  "code": 200,       // 200=成功, 400=参数错误, 401=未授权, 404=不存在, 500=服务器异常
  "msg": "操作描述",
  "data": {}         // 返回数据
}
```

### 景点 API

| 方法 | 路由 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/spots` | `?city=` `?tag=` `?all=1` | 获取景点列表，支持筛选。all=1 含下架景点（管理员） |
| GET | `/api/spots/<id>` | — | 根据 ID 获取景点详情（含攻略、经纬度） |
| GET | `/api/recommend` | `?tag=` | 根据标签推荐相似景点 |

### 视频 API

| 方法 | 路由 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/videos` | — | 获取全部视频列表 |
| GET | `/api/spots/<id>/videos` | — | 根据景点 ID 获取关联视频 |
| GET | `/api/videos/<id>` | — | 获取单个视频详情 |

### 美食 API

| 方法 | 路由 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/spots/<id>/foods` | — | 根据景点 ID 获取美食图片列表 |

### 用户 API

| 方法 | 路由 | 请求体 | 说明 |
|------|------|------|------|
| POST | `/api/register` | `{username, password, email}` | 用户注册，密码至少6位 |
| POST | `/api/login` | `{username, password}` | 用户登录，返回用户信息含 role |
| POST | `/api/avatar` | `{user_id, avatar_url}` | 更新用户头像 |

### 评论 API

| 方法 | 路由 | 参数/请求体 | 说明 |
|------|------|------|------|
| GET | `/api/spots/<id>/comments` | — | 获取景点评论列表 |
| POST | `/api/spots/<id>/comments` | `{user_id, username, content, rating}` | 提交评论（rating 1~5） |
| GET | `/api/comments/my` | `?user_id=` | 获取用户的评论列表 |
| DELETE | `/api/comments/<id>` | `{user_id}` | 删除自己的评论 |
| POST | `/api/comments/<id>/like` | — | 点赞评论 |

### 收藏 API

| 方法 | 路由 | 参数/请求体 | 说明 |
|------|------|------|------|
| GET | `/api/favorites` | `?user_id=` | 获取用户收藏列表 |
| POST | `/api/favorites` | `{user_id, spot_id}` | 添加收藏 |
| DELETE | `/api/favorites` | `?user_id=&spot_id=` | 取消收藏 |
| GET | `/api/favorites/check` | `?user_id=&spot_id=` | 检查是否已收藏 |

### 浏览记录 API

| 方法 | 路由 | 参数/请求体 | 说明 |
|------|------|------|------|
| GET | `/api/history` | `?user_id=` | 获取用户浏览记录 |
| POST | `/api/history` | `{user_id, spot_id}` | 添加浏览记录 |

### 游记 API

| 方法 | 路由 | 参数/请求体 | 说明 |
|------|------|------|------|
| GET | `/api/notes` | — | 获取全部游记 |
| GET | `/api/notes/my` | `?user_id=` | 获取用户发布的游记 |
| POST | `/api/notes` | `{user_id, title, content, spot_id?, images?}` | 发布游记 |
| DELETE | `/api/notes/<id>` | `{user_id}` | 删除自己的游记 |

### 管理员 API

| 方法 | 路由 | 参数/请求体 | 说明 |
|------|------|------|------|
| GET | `/api/admin/check` | `?user_id=` | 检查是否为管理员 |
| GET | `/api/admin/users` | — | 获取所有用户列表 |
| POST | `/api/admin/users/<id>/toggle` | `{enabled}` | 封禁/解封用户 |
| POST | `/api/admin/users/<id>/role` | `{role}` | 设置用户角色 |
| POST | `/api/admin/spots` | `{name, city, level, tag, desc, ...}` | 新增景点 |
| PUT | `/api/admin/spots/<id>` | `{...}` | 编辑景点 |
| DELETE | `/api/admin/spots/<id>` | — | 删除景点 |
| POST | `/api/admin/spots/<id>/toggle` | `{status}` | 上下架景点 |
| DELETE | `/api/admin/comments/<id>` | — | 删除评论 |

### 页面路由

| 路由 | 说明 |
|------|------|
| `/` | 首页 |
| `/detail?id=` | 景点详情页 |
| `/profile` | 个人主页 |
| `/notes` | 游记广场 |
| `/admin` | 管理后台 |

---

## 数据库表结构

| 表名 | 说明 | 关键字段 |
|------|------|------|
| `spots` | 景点 | id, name, city, level, tag, desc, avg_rating, rating_count, best_season, duration, ticket, open_time, transport, lat, lng, status |
| `users` | 用户 | id, username, email, password, avatar_url, role, enabled |
| `comments` | 评论 | id, spot_id, user_id, username, content, rating, likes |
| `favorites` | 收藏 | id, user_id, spot_id |
| `browsing_history` | 浏览记录 | id, user_id, spot_id, viewed_at |
| `videos` | 视频 | id, spot_id, title, url, thumbnail |
| `travel_notes` | 游记 | id, user_id, spot_id, title, content, images |

---

## 前端页面独立路由

项目包含 5 个独立页面路由：

1. **首页** `/` — 轮播 Banner + 景点卡片 + 城市/标签筛选 + 登录注册
2. **详情页** `/detail?id=1` — 景点信息 + 攻略面板 + 美食画廊 + Leaflet 地图 + 评论评分
3. **个人主页** `/profile` — 头像、收藏列表、浏览记录、我的评论
4. **游记广场** `/notes` — 全部游记列表 + 发布游记表单
5. **管理后台** `/admin` — 景点 CRUD + 用户管理 + 评论审核

---

## 访问地址

| 环境 | 地址 |
|------|------|
| 本地开发 | http://127.0.0.1:5000/ |
| 线上部署 | http://8.217.15.166:8080 |

> 线上环境通过阿里云 ECS (Ubuntu 24.04) + Docker 部署，运行在 8080 端口。

## 项目文档

- 数据库迁移脚本：`backend/migrate.sql`
- 接口文档：见本文档 API 清单章节
- Prompt 日志：`docs/prompt_log.md`
- 个人总结报告：`docs/个人总结报告.md`
- 部署脚本：`deploy-ecs.sh`（快速部署）、`fix-server.sh`（Git LFS + 重建修复）
