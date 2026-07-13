from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS
import os
import db_sqlite as db

app = Flask(__name__, static_folder="static")
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

# 全局异常捕获
@app.errorhandler(Exception)
def err_handler(e):
    return jsonify({"code": 500, "msg": f"服务器异常：{str(e)}"}), 500

# 首页路由
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)