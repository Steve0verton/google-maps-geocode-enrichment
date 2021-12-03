import psycopg2

# Try to connect

try:
    conn=psycopg2.connect(dbname='postgres',user='postgres')
except:
    print("I am unable to connect to the database.")

cur = conn.cursor()
try:
    cur.execute("""SELECT * from ref_location""")
except:
    print("I can't SELECT")

rows = cur.fetchall()
for row in rows:
    print("   ", row[1])
