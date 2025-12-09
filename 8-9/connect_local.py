import psycopg2

conn = psycopg2.connect("""
    host=localhost
    port=5002
    sslmode=disable
    dbname=postgres
    user=postgres
    password=postgres
    target_session_attrs=read-write
""")

q = conn.cursor()
q.execute('SELECT version()')

print(q.fetchone())

conn.close()
