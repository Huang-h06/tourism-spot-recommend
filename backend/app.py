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
        "email": user["email"],
        "avatar_url": user.get("avatar_url", "")
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
    user_id = data.get("user_id")
    if not username:
        return jsonify({"code": 400, "msg": "请输入昵称"}), 400
    if not content:
        return jsonify({"code": 400, "msg": "请输入评论内容"}), 400
    if len(username) > 50:
        return jsonify({"code": 400, "msg": "昵称不超过50字"}), 400
    if len(content) > 500:
        return jsonify({"code": 400, "msg": "评论内容不超过500字"}), 400
    comment = db.add_comment(spot_id, username, content, user_id)
    return jsonify({"code": 200, "data": comment, "msg": "评论成功"})


# 获取用户评论列表
@app.route("/api/comments/my", methods=["GET"])
def get_my_comments():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    comments = db.get_comments_by_user(user_id)
    return jsonify({"code": 200, "data": comments})


# 更新用户头像
@app.route("/api/avatar", methods=["POST"])
def update_avatar():
    data = request.get_json()
    user_id = data.get("user_id")
    avatar_url = (data.get("avatar_url", "") or "").strip()
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    if not avatar_url:
        return jsonify({"code": 400, "msg": "请输入头像URL"}), 400
    db.update_user_avatar(user_id, avatar_url)
    return jsonify({"code": 200, "msg": "头像更新成功", "data": {"avatar_url": avatar_url}})


# 获取用户收藏列表
@app.route("/api/favorites", methods=["GET"])
def get_favorites():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    favorites = db.get_user_favorites(user_id)
    return jsonify({"code": 200, "data": favorites})


# 添加收藏
@app.route("/api/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json()
    user_id = data.get("user_id")
    spot_id = data.get("spot_id")
    if not user_id or not spot_id:
        return jsonify({"code": 400, "msg": "参数不完整"}), 400
    db.add_favorite(user_id, spot_id)
    return jsonify({"code": 200, "msg": "收藏成功"})


# 取消收藏
@app.route("/api/favorites", methods=["DELETE"])
def remove_favorite():
    user_id = request.args.get("user_id", type=int)
    spot_id = request.args.get("spot_id", type=int)
    if not user_id or not spot_id:
        return jsonify({"code": 400, "msg": "参数不完整"}), 400
    db.remove_favorite(user_id, spot_id)
    return jsonify({"code": 200, "msg": "取消收藏"})


# 检查是否已收藏
@app.route("/api/favorites/check", methods=["GET"])
def check_favorite():
    user_id = request.args.get("user_id", type=int)
    spot_id = request.args.get("spot_id", type=int)
    if not user_id or not spot_id:
        return jsonify({"code": 400, "msg": "参数不完整"}), 400
    fav = db.is_favorited(user_id, spot_id)
    return jsonify({"code": 200, "data": fav})


# 获取用户浏览记录
@app.route("/api/history", methods=["GET"])
def get_history():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    history = db.get_user_browsing_history(user_id)
    return jsonify({"code": 200, "data": history})


# 添加浏览记录
@app.route("/api/history", methods=["POST"])
def add_history():
    data = request.get_json()
    user_id = data.get("user_id")
    spot_id = data.get("spot_id")
    if not user_id or not spot_id:
        return jsonify({"code": 400, "msg": "参数不完整"}), 400
    db.add_browsing_history(user_id, spot_id)
    return jsonify({"code": 200, "msg": "记录成功"})


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

# 个人主页路由
@app.route("/profile")
def profile_page():
    return render_template("profile.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)