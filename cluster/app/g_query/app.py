import argparse
import googlemaps
import json
import os
import geocode_lib
import traceback

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka import TopicPartition

#  This program performs geocode queries against Google.  It does so by repeatedly
#  gathering work via Kafka, and then in succession extract that query address,
#  send that work to Google, obtain the result transform it into a format that's
#  usable by the next program in the pipeline, and putting that transformed
#  data back into Kafka on an output topic.
def main(args):
   if os.environ.get('API_KEY') is None:
       sys.exit("No API Key Provided")
   else:
       apiKey = os.environ.get('API_KEY')

   kafkaHost = "localhost"

   if os.environ.get('KAFKA_HOST') != None: kafkaHost = os.environ.get('KAFKA_HOST')
   if args.kafka != None: kafkaHost = args.kafka

   try:
      gmaps = googlemaps.Client(key=apiKey)
      producer = KafkaProducer(bootstrap_servers='kafka')
      consumer = KafkaConsumer('geocode_input',group_id='geocoders',auto_offset_reset='latest',enable_auto_commit=False,bootstrap_servers='kafka')

      while True:
         raw_messages = consumer.poll(timeout_ms=2000,max_records=10)
         numUpdates = 0
         for _,messages in raw_messages.items():
            print("Recevied {0} messages from input queue".format(len(messages)))
            for message in messages:
               parsed = json.loads(message.value.decode('utf-8'))
               try:
                  geocode_results = gmaps.geocode(parsed[1])
               except Exception as e:
                  geocode_results = []
                  print("Google Geocode API Query Error: ",e)
               values = None
               if len(geocode_results) == 1:
                  values = geocode_lib.extractGoogleValues(geocode_results[0])
                  values['google_partial_match'] = False
               elif len(geocode_results) > 1:
                  values = geocode_lib.extractGoogleValues(geocode_results[0])
                  values['google_partial_match'] = True
               else:
                  values = geocode_lib.initGoogleValues()
                  values['google_partial_match'] = None
               values['location_hash'] = parsed[0]
               values['google_result_count'] = len(geocode_results)
               values['enrichment_api_response'] = json.dumps(geocode_results)
               value = json.dumps(values).encode('utf-8')
               producer.send('geocode_output',value=value)
               numUpdates = numUpdates + 1
         producer.flush()
         consumer.commit()
         if numUpdates != 0: print("Returned {0} messages from to output queue".format(numUpdates))
   except Exception as e:
      print("General Error",e)

parser = argparse.ArgumentParser()
parser.add_argument('--kafka', help="Kafka Hostname")
args = parser.parse_args()
main(args)
