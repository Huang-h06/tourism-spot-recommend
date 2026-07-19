import db_supabase as db

all_vids = db.get_all_videos()
print('total:', len(all_vids))
for v in all_vids:
    print(v)
