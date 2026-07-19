import db_supabase as db

try:
    r = db.supabase.rpc('exec_sql', {'sql': "SELECT policyname, permissive, roles, cmd, qual, with_check FROM pg_policies WHERE schemaname='public' AND tablename='videos';"}).execute()
    print(r)
except Exception as e:
    print('error', e)

try:
    r = db.supabase.table('videos').select('*').limit(0).execute()
    print('rls test select ok')
except Exception as e:
    print('select error', e)
