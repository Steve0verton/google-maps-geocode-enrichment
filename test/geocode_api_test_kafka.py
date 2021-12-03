import json
import psycopg2
import psycopg2.extras
import traceback

from kafka import KafkaProducer

try:
   conn = psycopg2.connect(dbname='postgres',user='postgres')
   producer = KafkaProducer(bootstrap_servers='kafka')
   cur = conn.cursor()
   cur.execute( """
      SELECT
        location_hash,location FROM core.ref_location
        WHERE
          (enrichment_enabled AND (enrichment_status = '' OR enrichment_status IS null))
          OR (now() - last_update_dttm > interval '1 year')
      """)
   rows = cur.fetchall()
   updates = []
   for row in rows:
      value = json.dumps([row[0],row[1]]).encode('utf-8')
      print("sending {0} to kafka...".format(row[0]))
      producer.send('geocode_input',value=value)
   producer.flush()
      
except Exception as e:
  traceback.print_exc(e)