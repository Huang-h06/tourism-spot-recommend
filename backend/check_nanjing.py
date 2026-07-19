import db_supabase as db

vids = db.get_videos_by_spot(16)
print('count:', len(vids))
for v in vids:
    print(v)
