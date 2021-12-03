import argparse
import json
import os
import psycopg2
import psycopg2.extras
import time

from kafka import KafkaProducer

def doUpdate(conn,cur,updateValues):
   sql = """
      UPDATE ref_location AS t SET enrichment_status = 'IN_PROCESS'
      FROM (VALUES %s) AS e(location_hash)
      WHERE e.location_hash = t.location_hash
   """
   updateTmpl = """(%(location_hash)s)"""
   psycopg2.extras.execute_values(cur,sql,updateValues,template=updateTmpl,page_size=100)
   conn.commit()
   cur.close()

def main(args):

   postgresHost = "localhost"
   kafkaHost = "localhost"
   fetchSize = 120
   sleepInterval = 5
   first = True

   if os.environ.get('POSTGRES_HOST') != None: postgresHost = os.environ.get('POSTGRES_HOST')
   if os.environ.get('POSTGRES_DB') != None: postgresDb = os.environ.get('POSTGRES_DB')
   if os.environ.get('POSTGRES_USER') != None: postgresUser = os.environ.get('POSTGRES_USER')
   if os.environ.get('POSTGRES_PASSWORD') != None: postgresPassword = os.environ.get('POSTGRES_PASSWORD')
   if os.environ.get('KAFKA_HOST') != None: kafkaHost = os.environ.get('KAFKA_HOST')
   if os.environ.get('SLEEP_INTERVAL') != None: sleepInterval = int(os.environ.get('SLEEP_INTERVAL'))
   if os.environ.get('FETCH_SIZE') != None: fetchSize = int(os.environ.get('FETCH_SIZE'))

   if args.pg != None: postgresHost = args.pg
   if args.kafka != None: kafkaHost = args.kafka
   if args.sleep != None: sleepInterval = int(args.sleep)
   if args.fetch != None: fetchSize = int(args.fetch)

   try:
      conn = psycopg2.connect(host=postgresHost,dbname=postgresDb,user=postgresUser,password=postgresPassword)
      producer = KafkaProducer(bootstrap_servers=kafkaHost)
      while True:
         fsize = fetchSize
         if first:
            fsize = 3 * fsize
            first = False
         cur = conn.cursor()
         cur.execute( """
            SELECT
               location_hash,location
            FROM ref_location
            WHERE
               (enrichment_enabled AND (enrichment_status = '' OR enrichment_status IS null))
               OR (now() - last_update_dttm > interval '30 days')
            LIMIT {0}
            FOR UPDATE
            """.format(fsize))
         rows = cur.fetchall()
         updates = []
         for row in rows:
            value = json.dumps([row[0],row[1]]).encode('utf-8')
            producer.send('geocode_input',value=value)
            updates.append({ 'location_hash':row[0] })
         producer.flush()
         if len(updates) != 0:
            print("Queued {0} query requests".format(len(updates)))
            doUpdate(conn,cur,updates)
         time.sleep(sleepInterval)
   except Exception as e:
      print(e)

parser = argparse.ArgumentParser()
parser.add_argument('--pg', help="PostgreSQL DB Server Hostname")
parser.add_argument('--kafka', help="Kafka Hostname")
parser.add_argument('--sleep', help="Sleep Interval (seconds)")
parser.add_argument('--fetch', help="Number of rows to fetch in each interval")
args = parser.parse_args()
main(args)
