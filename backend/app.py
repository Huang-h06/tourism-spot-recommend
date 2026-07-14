from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import os
import secrets
from werkzeug.security import check_password_hash
# import db_sqlite as db
import db_supabase as db

app = Flask(__name__, static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
CORS(app)


# 获取全部景点，支持按城市、标签模糊筛选
@app.route("/api/spots", methods=["GET"])
def get_all_spots():
    city = request.args.get("city", "")
    tag = request.args.get("tag", "")
    res = db.query_spots(city, tag)
    return jsonify({"code": 200, "data": res, "msg": "查询成功"})

# 根据ID获取单个景点详情
@app.route("/api/spots/<int:spot_id>", methods=["GET"])
def get_spot_detail(spot_id):
    spot = db.get_spot_by_id(spot_id)
    if not spot:
        return jsonify({"code": 404, "msg": "景点不存在"}), 404
    return jsonify({"code": 200, "data": spot})

# 根据标签推荐景点
@app.route("/api/recommend", methods=["GET"])
def recommend_spot():
    tag = request.args.get("tag", "自然风光")
    data = db.recommend_by_tag(tag)
    return jsonify({"code": 200, "recommend": data})


# 用户注册
@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()
    username = (data.get("username", "") or "").strip()
    password = (data.get("password", "") or "").strip()
    email = (data.get("email", "") or "").strip()
    if not username:
        return jsonify({"code": 400, "msg": "请输入用户名"}), 400
    if not password:
        return jsonify({"code": 400, "msg": "请输入密码"}), 400
    if len(username) > 50:
        return jsonify({"code": 400, "msg": "用户名不超过50字"}), 400
    if len(password) < 6:
        return jsonify({"code": 400, "msg": "密码至少6位"}), 400
    existing = db.get_user_by_username(username)
    if existing:
        return jsonify({"code": 400, "msg": "用户名已存在"}), 400
    db.register_user(username, password, email)
    return jsonify({"code": 200, "msg": "注册成功"})


# 用户登录
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = (data.get("username", "") or "").strip()
    password = (data.get("password", "") or "").strip()
    if not username or not password:
        return jsonify({"code": 400, "msg": "请输入用户名和密码"}), 400
    user = db.get_user_by_username(username)
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"code": 401, "msg": "用户名或密码错误"}), 401
    return jsonify({"code": 200, "msg": "登录成功", "data": {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"]
    }})


# 获取所有视频
@app.route("/api/videos", methods=["GET"])
def get_all_videos():
    data = db.get_all_videos()
    return jsonify({"code": 200, "data": data, "msg": "查询成功"})

# 根据景点ID获取视频列表
@app.route("/api/spots/<int:spot_id>/videos", methods=["GET"])
def get_spot_videos(spot_id):
    spot = db.get_spot_by_id(spot_id)
    if not spot:
        return jsonify({"code": 404, "msg": "景点不存在"}), 404
    videos = db.get_videos_by_spot(spot_id)
    return jsonify({"code": 200, "data": videos, "spot": spot["name"]})

# 根据视频ID获取视频详情
@app.route("/api/videos/<int:video_id>", methods=["GET"])
def get_video_detail(video_id):
    video = db.get_video_by_id(video_id)
    if not video:
        return jsonify({"code": 404, "msg": "视频不存在"}), 404
    return jsonify({"code": 200, "data": video})

# 获取景点评论列表
@app.route("/api/spots/<int:spot_id>/comments", methods=["GET"])
def get_spot_comments(spot_id):
    spot = db.get_spot_by_id(spot_id)
    if not spot:
        return jsonify({"code": 404, "msg": "景点不存在"}), 404
    comments = db.get_comments_by_spot(spot_id)
    return jsonify({"code": 200, "data": comments})


# 提交景点评论
@app.route("/api/spots/<int:spot_id>/comments", methods=["POST"])
def post_spot_comment(spot_id):
    spot = db.get_spot_by_id(spot_id)
    if not spot:
        return jsonify({"code": 404, "msg": "景点不存在"}), 404
    data = request.get_json()
    username = (data.get("username", "") or "").strip()
    content = (data.get("content", "") or "").strip()
    if not username:
        return jsonify({"code": 400, "msg": "请输入昵称"}), 400
    if not content:
        return jsonify({"code": 400, "msg": "请输入评论内容"}), 400
    if len(username) > 50:
        return jsonify({"code": 400, "msg": "昵称不超过50字"}), 400
    if len(content) > 500:
        return jsonify({"code": 400, "msg": "评论内容不超过500字"}), 400
    comment = db.add_comment(spot_id, username, content)
    return jsonify({"code": 200, "data": comment, "msg": "评论成功"})


# 全局异常捕获
@app.errorhandler(Exception)
def err_handler(e):
    return jsonify({"code": 500, "msg": f"服务器异常：{str(e)}"}), 500

# 首页路由
@app.route("/")
def index():
    return render_template("index.html")

# 详情页路由
@app.route("/detail")
def detail_page():
    return render_template("detail.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)