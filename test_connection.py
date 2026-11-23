import storage as db

try:
    con = db.connect()
    cur = con.cursor()

    cur.execute("SELECT version()")
    result = cur.fetchone()

    print("Supabase connection successful!")
    print(result[0])

    cur.close()
    con.close()

except Exception as e:
    print("Connection failed:")
    print(e)