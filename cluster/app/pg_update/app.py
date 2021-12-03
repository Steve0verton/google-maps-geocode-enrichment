import argparse
import json
import os
import psycopg2
import psycopg2.extras
import geocode_lib

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka import TopicPartition

def main(args):
   postgresHost = "localhost"
   kafkaHost = "localhost"

   if os.environ.get('POSTGRES_HOST') != None: postgresHost = os.environ.get('POSTGRES_HOST')
   if os.environ.get('POSTGRES_DB') != None: postgresDb = os.environ.get('POSTGRES_DB')
   if os.environ.get('POSTGRES_USER') != None: postgresUser = os.environ.get('POSTGRES_USER')
   if os.environ.get('POSTGRES_PASSWORD') != None: postgresPassword = os.environ.get('POSTGRES_PASSWORD')
   if os.environ.get('KAFKA_HOST') != None: kafkaHost = os.environ.get('KAFKA_HOST')
   if args.pg != None: postgresHost = args.pg
   if args.kafka != None: kafkaHost = args.kafka

   try:
      conn = psycopg2.connect(host=postgresHost,dbname=postgresDb,user=postgresUser,password=postgresPassword)
      consumer = KafkaConsumer('geocode_output',group_id='geocoders',auto_offset_reset='latest',enable_auto_commit=False,bootstrap_servers=kafkaHost)
      while True:
         raw_messages = consumer.poll(timeout_ms=2000,max_records=400)
         updates = []
         for _,messages in raw_messages.items():
            for message in messages:
               rec = json.loads(message.value.decode())
               updates.append(rec)
         if len(updates) != 0:
            print("Updating {0} records".format(len(updates)))
            geocode_lib.doPgUpdate(conn,updates)
            consumer.commit()
   except Exception as e:
      print(e)

parser = argparse.ArgumentParser()
parser.add_argument('--pg', help="PostgreSQL DB Server Hostname")
parser.add_argument('--kafka', help="Kafka Hostname")
args = parser.parse_args()
main(args)
