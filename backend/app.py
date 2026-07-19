from flask import Flask, jsonify, request, send_from_directory, render_template, send_file, Response
from flask_cors import CORS
import os
import re
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
    all_spots = request.args.get("all", "") == "1"
    res = db.query_spots(city, tag)
    # 如果all=1则返回全部（管理员用），否则只返回active的
    if not all_spots:
        res = [s for s in res if s.get("status", "active") != "inactive"]
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
        "avatar_url": user.get("avatar_url", ""),
        "role": user.get("role", "user")
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

# 美食图片映射：景点名 -> 美食图片前缀
FOOD_IMG_MAP = {
    "西湖": "hangzhou", "故宫": "beijing", "张家界": "zhangjiajie",
    "鼓浪屿": "xiamen", "丽江": "lijiang", "西藏": "xizang",
    "新疆": "xinjiang", "成都": "chengdu", "重庆": "chongqing",
    "青岛": "qingdao", "上海": "shanghai", "南京": "nanjing"
}

# 根据景点ID获取美食图片列表
@app.route("/api/spots/<int:spot_id>/foods", methods=["GET"])
def get_spot_foods(spot_id):
    spot = db.get_spot_by_id(spot_id)
    if not spot:
        return jsonify({"code": 404, "msg": "景点不存在"}), 404
    prefix = FOOD_IMG_MAP.get(spot["name"])
    if not prefix:
        return jsonify({"code": 200, "data": []})
    # 读取 static/images/foods 目录下匹配前缀的图片
    foods_dir = os.path.join(app.static_folder, "images", "foods")
    images = []
    if os.path.isdir(foods_dir):
        for fname in sorted(os.listdir(foods_dir)):
            if fname.lower().startswith(prefix.lower()) and (
                fname.lower().endswith(".jpg") or
                fname.lower().endswith(".jpeg") or
                fname.lower().endswith(".png") or
                fname.lower().endswith(".webp")
            ):
                images.append({"url": f"/static/images/foods/{fname}"})
    return jsonify({"code": 200, "data": images, "spot": spot["name"]})


# 根据视频ID获取视频详情
@app.route("/api/videos/<int:video_id>", methods=["GET"])
def get_video_detail(video_id):
    video = db.get_video_by_id(video_id)
    if not video:
        return jsonify({"code": 404, "msg": "视频不存在"}), 404
    return jsonify({"code": 200, "data": video})


# 视频文件服务（支持 Range 请求，浏览器播放必需）
@app.route("/static/videos/<path:filename>")
def serve_video(filename):
    file_path = os.path.join(app.static_folder, "videos", filename)
    if not os.path.isfile(file_path):
        return jsonify({"code": 404, "msg": "视频不存在"}), 404

    file_size = os.path.getsize(file_path)
    range_header = request.headers.get("Range")

    if range_header:
        m = re.search(r"bytes=(\d+)-(\d*)", range_header)
        if m:
            start = int(m.group(1))
            end = int(m.group(2)) if m.group(2) else file_size - 1
        else:
            start, end = 0, file_size - 1

        if start >= file_size:
            return Response(status=416)

        end = min(end, file_size - 1)
        length = end - start + 1

        with open(file_path, "rb") as f:
            f.seek(start)
            data = f.read(length)

        resp = Response(data, 206, mimetype="video/mp4", direct_passthrough=True)
        resp.headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        resp.headers["Accept-Ranges"] = "bytes"
        resp.headers["Content-Length"] = str(length)
        return resp

    return send_file(file_path, mimetype="video/mp4")


# 获取景点评论列表
@app.route("/api/spots/<int:spot_id>/comments", methods=["GET"])
def get_spot_comments(spot_id):
    spot = db.get_spot_by_id(spot_id)
    if not spot:
        return jsonify({"code": 404, "msg": "景点不存在"}), 404
    comments = db.get_comments_by_spot(spot_id)
    return jsonify({"code": 200, "data": comments})


# 提交景点评论（含评分）
@app.route("/api/spots/<int:spot_id>/comments", methods=["POST"])
def post_spot_comment(spot_id):
    spot = db.get_spot_by_id(spot_id)
    if not spot:
        return jsonify({"code": 404, "msg": "景点不存在"}), 404
    data = request.get_json()
    username = (data.get("username", "") or "").strip()
    content = (data.get("content", "") or "").strip()
    user_id = data.get("user_id")
    rating = data.get("rating", 5)
    # 校验评分范围
    if not isinstance(rating, int) or rating < 1 or rating > 5:
        return jsonify({"code": 400, "msg": "评分须为1~5整数"}), 400
    if not username:
        return jsonify({"code": 400, "msg": "请输入昵称"}), 400
    if not content:
        return jsonify({"code": 400, "msg": "请输入评论内容"}), 400
    if len(username) > 50:
        return jsonify({"code": 400, "msg": "昵称不超过50字"}), 400
    if len(content) > 500:
        return jsonify({"code": 400, "msg": "评论内容不超过500字"}), 400
    if len(content) < 2:
        return jsonify({"code": 400, "msg": "评论内容不能少于2个字"}), 400
    comment = db.add_comment(spot_id, username, content, user_id, rating)
    return jsonify({"code": 200, "data": comment, "msg": "评论成功"})


# 删除评论
@app.route("/api/comments/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    result = db.delete_comment(comment_id, user_id)
    if not result:
        return jsonify({"code": 404, "msg": "评论不存在或无权删除"}), 404
    return jsonify({"code": 200, "msg": "删除成功"})


# 点赞评论
@app.route("/api/comments/<int:comment_id>/like", methods=["POST"])
def like_comment(comment_id):
    new_likes = db.like_comment(comment_id)
    if new_likes is None:
        return jsonify({"code": 404, "msg": "评论不存在"}), 404
    return jsonify({"code": 200, "data": {"likes": new_likes}, "msg": "点赞成功"})


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

# 游记列表页
@app.route("/notes")
def notes_page():
    return render_template("notes.html")

# 管理员后台
@app.route("/admin")
def admin_page():
    return render_template("admin.html")


# ========== 游记 API ==========
# 获取所有游记
@app.route("/api/notes", methods=["GET"])
def get_notes():
    data = db.get_all_notes()
    return jsonify({"code": 200, "data": data})

# 获取当前用户的游记
@app.route("/api/notes/my", methods=["GET"])
def get_my_notes():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    data = db.get_user_notes(user_id)
    return jsonify({"code": 200, "data": data})

# 发布游记
@app.route("/api/notes", methods=["POST"])
def create_note():
    data = request.get_json()
    user_id = data.get("user_id")
    title = (data.get("title", "") or "").strip()
    content = (data.get("content", "") or "").strip()
    spot_id = data.get("spot_id")
    images = data.get("images", "[]")
    if not user_id:
        return jsonify({"code": 400, "msg": "请先登录"}), 400
    if not title:
        return jsonify({"code": 400, "msg": "请输入标题"}), 400
    if not content:
        return jsonify({"code": 400, "msg": "请输入游记内容"}), 400
    if len(title) > 200:
        return jsonify({"code": 400, "msg": "标题不超过200字"}), 400
    note = db.create_note(user_id, title, content, spot_id, images)
    return jsonify({"code": 200, "data": note, "msg": "发布成功"})

# 删除游记
@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    result = db.delete_note(note_id, user_id)
    if not result:
        return jsonify({"code": 404, "msg": "游记不存在或无权删除"}), 404
    return jsonify({"code": 200, "msg": "删除成功"})


# ========== 管理员 API ==========
# 检查是否是管理员
@app.route("/api/admin/check", methods=["GET"])
def admin_check():
    user_id = request.args.get("user_id", type=int)
    if not user_id:
        return jsonify({"code": 400, "msg": "缺少用户ID"}), 400
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    is_admin = user.get("role") == "admin"
    return jsonify({"code": 200, "data": {"is_admin": is_admin, "role": user.get("role")}})

# 获取所有用户
@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    data = db.admin_get_users()
    return jsonify({"code": 200, "data": data})

# 封禁/解封用户
@app.route("/api/admin/users/<int:user_id>/toggle", methods=["POST"])
def admin_toggle_user(user_id):
    data = request.get_json()
    enabled = data.get("enabled", True)
    db.admin_toggle_user(user_id, enabled)
    return jsonify({"code": 200, "msg": "操作成功"})

# 设置用户角色
@app.route("/api/admin/users/<int:user_id>/role", methods=["POST"])
def admin_set_role(user_id):
    data = request.get_json()
    role = data.get("role", "user")
    db.admin_set_role(user_id, role)
    return jsonify({"code": 200, "msg": "角色更新成功"})

# 新增景点
@app.route("/api/admin/spots", methods=["POST"])
def admin_add_spot():
    data = request.get_json()
    name = (data.get("name", "") or "").strip()
    city = (data.get("city", "") or "").strip()
    level = (data.get("level", "") or "").strip()
    tag = (data.get("tag", "") or "").strip()
    desc = (data.get("desc", "") or "").strip()
    if not name or not city:
        return jsonify({"code": 400, "msg": "景点名和城市不能为空"}), 400
    result = db.admin_add_spot(name, city, level, tag, desc, data.get("lat", 0), data.get("lng", 0), data.get("best_season", ""), data.get("duration", ""), data.get("ticket", ""), data.get("open_time", ""), data.get("transport", ""))
    return jsonify({"code": 200, "data": result, "msg": "添加成功"})

# 编辑景点
@app.route("/api/admin/spots/<int:spot_id>", methods=["PUT"])
def admin_update_spot(spot_id):
    data = request.get_json()
    db.admin_update_spot(spot_id, data)
    return jsonify({"code": 200, "msg": "更新成功"})

# 删除景点
@app.route("/api/admin/spots/<int:spot_id>", methods=["DELETE"])
def admin_delete_spot(spot_id):
    db.admin_delete_spot(spot_id)
    return jsonify({"code": 200, "msg": "删除成功"})

# 上下架景点
@app.route("/api/admin/spots/<int:spot_id>/toggle", methods=["POST"])
def admin_toggle_spot(spot_id):
    data = request.get_json()
    status = data.get("status", "active")
    db.admin_toggle_spot(spot_id, status)
    return jsonify({"code": 200, "msg": "操作成功"})

# 管理员删除评论
@app.route("/api/admin/comments/<int:comment_id>", methods=["DELETE"])
def admin_delete_comment(comment_id):
    db.admin_delete_comment(comment_id)
    return jsonify({"code": 200, "msg": "删除成功"})


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
