from flask import Flask, jsonify, request
from flask_cors import CORS
import db_sqlite as db

app = Flask(__name__)
CORS(app)

# 获取全部景点，支持按城市、等级筛选
@app.route("/api/spots", methods=["GET"])
def get_all_spots():
    city = request.args.get("city", "")
    level = request.args.get("level", "")
    res = db.query_spots(city, level)
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

# 全局异常捕获
@app.errorhandler(Exception)
def err_handler(e):
    return jsonify({"code": 500, "msg": f"服务器异常：{str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)