from werkzeug.security import generate_password_hash, check_password_hash
from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 根据用户名查询用户
def get_user_by_username(username):
    res = supabase.table("users").select("*").eq("username", username).execute()
    if len(res.data) == 0:
        return None
    return res.data[0]


# 根据id查询用户

def get_user_by_id(user_id):
    res = supabase.table("users").select("id,username,email,avatar_url,created_at").eq("id", user_id).execute()
    if len(res.data) == 0:
        return None
    return res.data[0]


# 更新用户头像
def update_user_avatar(user_id, avatar_url):
    res = supabase.table("users").update({"avatar_url": avatar_url}).eq("id", user_id).execute()
    return res.data


# 注册新用户
def register_user(username, password, email):
    hashed = generate_password_hash(password)
    res = supabase.table("users").insert({
        "username": username,
        "password": hashed,
        "email": email
    }).execute()
    return res.data


# 查询所有景点（支持城市、标签模糊筛选）
def query_spots(city="", tag=""):
    query = supabase.table("spots").select("*")
    if city:
        query = query.ilike("city", f"%{city}%")
    if tag:
        query = query.ilike("tag", f"%{tag}%")
    res = query.execute()
    return res.data


# 根据id查询单个景点（含攻略信息）
def get_spot_by_id(spot_id):
    res = supabase.table("spots").select("*").eq("id", spot_id).execute()
    if len(res.data) == 0:
        return None
    return res.data[0]


# 根据标签推荐景点（精确匹配）
def recommend_by_tag(tag):
    res = supabase.table("spots").select("*").eq("tag", tag).execute()
    return res.data


# 根据景点ID获取评论列表（按时间倒序）
def get_comments_by_spot(spot_id):
    res = supabase.table("comments").select("*").eq("spot_id", spot_id).order("created_at", desc=True).execute()
    return res.data


# 新增评论（含评分）
def add_comment(spot_id, username, content, user_id=None, rating=5):
    data = {
        "spot_id": spot_id,
        "username": username,
        "content": content
    }
    if user_id:
        data["user_id"] = user_id
    # 如果 rating/likes 列存在才传入，否则走旧版兼容
    try:
        data["rating"] = rating
        data["likes"] = 0
        res = supabase.table("comments").insert(data).execute()
    except Exception:
        data.pop("rating", None)
        data.pop("likes", None)
        res = supabase.table("comments").insert(data).execute()
    # 尝试更新景点的平均评分
    try:
        _update_spot_avg_rating(spot_id)
    except Exception:
        pass
    return res.data


# 更新景点平均评分
def _update_spot_avg_rating(spot_id):
    res = supabase.table("comments").select("rating").eq("spot_id", spot_id).execute()
    ratings = [r["rating"] for r in res.data if r.get("rating")]
    if ratings:
        avg = round(sum(ratings) / len(ratings), 1)
        supabase.table("spots").update({
            "avg_rating": avg,
            "rating_count": len(ratings)
        }).eq("id", spot_id).execute()
    else:
        supabase.table("spots").update({
            "avg_rating": 0,
            "rating_count": 0
        }).eq("id", spot_id).execute()


# 删除评论
def delete_comment(comment_id, user_id=None):
    query = supabase.table("comments").delete().eq("id", comment_id)
    if user_id:
        query = query.eq("user_id", user_id)
    res = query.execute()
    return res.data


# 点赞评论
def like_comment(comment_id):
    try:
        res = supabase.table("comments").select("likes").eq("id", comment_id).execute()
        if res.data:
            current = res.data[0].get("likes", 0) or 0
            supabase.table("comments").update({"likes": current + 1}).eq("id", comment_id).execute()
            return current + 1
    except Exception:
        pass
    return None


# 获取某用户的所有评论
def get_comments_by_user(user_id):
    res = supabase.table("comments").select("*, spots(name)").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data


# 添加收藏
def add_favorite(user_id, spot_id):
    res = supabase.table("favorites").upsert({
        "user_id": user_id,
        "spot_id": spot_id
    }).execute()
    return res.data


# 取消收藏
def remove_favorite(user_id, spot_id):
    res = supabase.table("favorites").delete().eq("user_id", user_id).eq("spot_id", spot_id).execute()
    return res.data


# 获取用户收藏列表
def get_user_favorites(user_id):
    res = supabase.table("favorites").select("*, spots(*)").eq("user_id", user_id).order("created_at", desc=True).execute()
    return res.data


# 检查是否已收藏
def is_favorited(user_id, spot_id):
    res = supabase.table("favorites").select("id").eq("user_id", user_id).eq("spot_id", spot_id).execute()
    return len(res.data) > 0


# 添加浏览记录
def add_browsing_history(user_id, spot_id):
    res = supabase.table("browsing_history").upsert({
        "user_id": user_id,
        "spot_id": spot_id,
        "viewed_at": "now()"
    }).execute()
    return res.data


# 获取用户浏览记录
def get_user_browsing_history(user_id):
    res = supabase.table("browsing_history").select("*, spots(*)").eq("user_id", user_id).order("viewed_at", desc=True).execute()
    return res.data


# 获取所有视频
def get_all_videos():
    res = supabase.table("videos").select("*").order("id").execute()
    return res.data


# 根据景点ID获取视频列表
def get_videos_by_spot(spot_id):
    res = supabase.table("videos").select("*").eq("spot_id", spot_id).order("id").execute()
    return res.data


# 根据视频ID获取单个视频
def get_video_by_id(video_id):
    res = supabase.table("videos").select("*").eq("id", video_id).execute()
    if len(res.data) == 0:
        return None
    return res.data[0]
