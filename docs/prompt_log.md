# AI Prompt 日志

以下记录了开发过程中使用 AI（CodeBuddy）进行辅助编程的关键 Prompt 及 AI 返回的原始输出。

---

## Prompt 1：数据库迁移需求

**Prompt**：
```
数据库要上传什么
```

**AI 输出简述**：分析了项目数据库结构，说明了需要执行 `backend/migrate.sql`，给出了 3 部分 SQL 的内容说明（景点表加字段、评论表加字段、攻略数据填充），并提供了 Supabase SQL Editor 的操作步骤。

**对应文件/功能**：`backend/migrate.sql` / 数据库表结构初始化

---

## Prompt 2：轮播图展示全部景点

**Prompt**：
```
上面的轮播图要所有景点而不是只有四个
```

**AI 输出简述**：

修改了 `index.html` 中的轮播图实现：

1. 删除了硬编码的 4 张幻灯片 HTML
2. 改为 `buildBanner()` 函数，从 `/api/spots` API 获取全部 12 个景点
3. 动态生成幻灯片 DOM 和圆点导航，添加了 sloganMap 映射标语

**对应文件/功能**：`backend/templates/index.html` / 轮播 Banner 动态化

---

## Prompt 3：评分显示问题排查

**Prompt**：
```
（附截图）已经评分了为什么还是显示暂无评分
```

**AI 输出简述**：

分析原因是数据库迁移 SQL 未执行，`spots` 表缺少 `avg_rating` 和 `rating_count` 字段。在 `migrate.sql` 最后添加了第 4 部分：根据已有评论重新计算每个景点的平均分的 SQL。执行后已有评论的景点会自动算出平均分。

**对应文件/功能**：`backend/migrate.sql` / 评分显示修复

---

## Prompt 4：新增三大功能模块

**Prompt**：
```
游记模块：用户可以发布图文游记（游玩心得 + 多张图片），独立游记列表页面
地图定位：接入地图组件，展示景点地理位置
管理员后台：景点新增、编辑、删除、上下架 + 用户管理（查看/封禁）+ 评论管理（审核、删除）
给我增添这些功能
```

**AI 输出简述**：

实现了 3 个完整功能模块：

1. **游记模块**：
   - 数据库新建 `travel_notes` 表（id, user_id, spot_id, title, content, images, created_at）
   - `db_supabase.py` 添加 `create_note`、`get_all_notes`、`get_user_notes`、`get_note_by_id`、`delete_note` 函数
   - `app.py` 添加 4 个游记 API：GET `/api/notes`、GET `/api/notes/my`、POST `/api/notes`、DELETE `/api/notes/<id>`
   - 新建 `templates/notes.html` 游记广场页面（列表+发布表单）

2. **地图定位**：
   - `migrate.sql` 添加 spots 表的 `lat`、`lng` 字段，并更新 12 个景点经纬度
   - `detail.html` 引入 Leaflet CSS/JS CDN，添加 `mapContainer` 地图区域
   - 景点详情加载后自动初始化地图并标记位置

3. **管理员后台**：
   - `migrate.sql` 添加 `spots.status`（上下架）、`users.role`（角色）、`users.enabled`（封禁状态）字段
   - `db_supabase.py` 添加 8 个管理员函数
   - `app.py` 添加 9 个管理员 API
   - 新建 `templates/admin.html`，含景点管理/用户管理/评论管理三个 Tab

**对应文件/功能**：`backend/app.py`、`backend/db_supabase.py`、`backend/migrate.sql`、`backend/templates/detail.html`、`backend/templates/notes.html`、`backend/templates/admin.html` / 三大模块

---

## Prompt 5：地图底图修复

**Prompt**：
```
（附截图）地图就这样吗
```

**AI 输出简述**：

分析发现 OpenStreetMap 瓦片在国内被墙导致底图灰色。将 Leaflet tileLayer 由 OpenStreetMap 替换为高德地图瓦片：

```javascript
L.tileLayer('https://webrd0{s}.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}', {
    subdomains: '1234',
    attribution: '&copy; 高德地图',
    maxZoom: 18
}).addTo(map);
```

**对应文件/功能**：`backend/templates/detail.html` / 地图底图国内可用性修复

---

## Prompt 6：管理员权限判断修复

**Prompt**：
```
（附截图）我登了admin为什么不能管理后台
```

**AI 输出简述**：

定位到两个问题：

1. `db_supabase.py` 的 `get_user_by_id()` 只查询了 `id,username,email,avatar_url,created_at`，遗漏了 `role` 和 `enabled` 字段
2. `app.py` 的 `login()` 接口返回数据里没有包含 `role` 字段

修复：`get_user_by_id` 添加 `role, enabled` 字段；`login` 返回增加 `role` 字段；`admin.html` 在权限检查通过后同步更新 localStorage 中的 role。

**对应文件/功能**：`backend/db_supabase.py`、`backend/app.py`、`backend/templates/admin.html` / 管理员权限修复

---

## Prompt 7：数据库 SQL 问题排查

**Prompt**：
```
migrate.sql不是和之前一样吗
```

**AI 输出简述**：

说明了 migrate.sql 的新增部分（第 28~72 行），包含：
- 第 4 部分：经纬度 + 上下架状态字段
- 第 5 部分：用户角色 + 封禁状态字段
- 第 6 部分：游记表创建
- 第 7 部分：12 个景点经纬度数据
- 第 8 部分：已有评论平均分重算

**对应文件/功能**：`backend/migrate.sql` / 数据库迁移更新说明

---

## Prompt 8：项目文档生成

**Prompt**：
```
（附考核细则完整内容）帮我做个文档
```

**AI 输出简述**：

根据考核细则要求，生成了完整的项目文档：

1. `README.md`：包含项目介绍、功能总览、技术栈、目录结构、安装运行指南、44 个完整 API 列表、数据库表结构、页面路由说明
2. `prompt_log.md`：记录 8 条关键 Prompt，每条标注对应文件/功能
3. `docs/个人总结报告.md`：500+ 字实训总结

**对应文件/功能**：`README.md`、`docs/prompt_log.md`、`docs/个人总结报告.md` / 项目文档
