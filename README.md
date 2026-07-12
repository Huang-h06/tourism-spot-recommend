# 旅游景点推荐系统

前后端项目：Flask + SQLite

## 后端启动方式

1. 进入 backend 文件夹
```bash
cd backend
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 运行项目
```bash
python app.py
```

4. 访问测试接口
- 获取全部景点：http://127.0.0.1:5000/api/spots
- 获取景点详情：http://127.0.0.1:5000/api/spots/1
- 标签推荐景点：http://127.0.0.1:5000/api/recommend?tag=自然风光

## API 接口说明

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/spots` | GET | 获取全部景点，支持 `city`、`level` 参数筛选 |
| `/api/spots/<id>` | GET | 根据 ID 获取景点详情 |
| `/api/recommend` | GET | 根据 `tag` 参数推荐景点，默认"自然风光" |

## 技术栈

- **后端框架**：Flask
- **数据库**：SQLite
- **跨域支持**：Flask-CORS
