import db_supabase as db

print('try delete with match...')
try:
    r = db.supabase.table('videos').delete().match({'id': 20}).execute()
    print('response:', r.data)
except Exception as e:
    print('error:', e)

vids = db.get_videos_by_spot(16)
print('after:', vids)
