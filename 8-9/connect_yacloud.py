import psycopg2

conn = psycopg2.connect("""
    host=c-c9qkbjmsg4qq096u2nqu.rw.mdb.yandexcloud.net
    port=6432
    sslmode=verify-ca
    dbname=db1
    user=user1
    password=therewasapassword
    target_session_attrs=read-write
""")

q = conn.cursor()
q.execute('SELECT version()')

print(q.fetchone())

conn.close()
