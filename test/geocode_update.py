import json
import psycopg2
import psycopg2.extras
import geocode_lib
import traceback

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka import TopicPartition

try:
   consumer = KafkaConsumer('geocode_output',group_id='geocoders',auto_offset_reset='latest',enable_auto_commit=False,bootstrap_servers='kafka')
   conn = psycopg2.connect(dbname='postgres',user='postgres')
   while True:
      raw_messages = consumer.poll(timeout_ms=2000,max_records=100)
      updates = []
      for _,messages in raw_messages.items():
         for message in messages:
            rec = json.loads(message.value.decode())
            updates.append(rec)
      if len(updates) != 0:
         print("updating {0} records".format(len(updates)))
         geocode_lib.doPgUpdate(conn,updates)
         consumer.commit()

except Exception as e:
  traceback.print_exc(e)
