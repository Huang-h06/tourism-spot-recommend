from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 查询所有景点（支持城市、标签模糊筛选）
def query_spots(city="", tag=""):
    query = supabase.table("spots").select("*")
    if city:
        query = query.ilike("city", f"%{city}%")
    if tag:
        query = query.ilike("tag", f"%{tag}%")
    res = query.execute()
    return res.data


# 根据id查询单个景点
def get_spot_by_id(spot_id):
    res = supabase.table("spots").select("*").eq("id", spot_id).execute()
    if len(res.data) == 0:
        return None
    return res.data[0]


# 根据标签推荐景点（精确匹配）
def recommend_by_tag(tag):
    res = supabase.table("spots").select("*").eq("tag", tag).execute()
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
