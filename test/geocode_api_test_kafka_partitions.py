import googlemaps
import json
import geocode_lib
import traceback

from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka import TopicPartition

try:
   gmaps = googlemaps.Client(key='AIzaSyAt84GkL8eHaJaPy5OE_ZszKMR7pMQNCrM')
   producer = KafkaProducer(bootstrap_servers='kafka')
   consumer = KafkaConsumer('geocode_input',group_id='geocoders',auto_offset_reset='latest',enable_auto_commit=False,bootstrap_servers='kafka')

   while True:
      raw_messages = consumer.poll(timeout_ms=2000,max_records=10)
      for _,messages in raw_messages.items():
         print("got {0} messages from input queue".format(len(messages)))
         for message in messages:
            parsed = json.loads(message.value.decode('utf-8'))
            geocode_results = gmaps.geocode(parsed[1])
            values = None
            if len(geocode_results) == 1:
               values = geocode_lib.extractGoogleValues(geocode_results[0])
               values['google_partial_match'] = False
               print("single result")
            elif len(geocode_results) > 1:
               values = geocode_lib.extractGoogleValues(geocode_results[0])
               values['google_partial_match'] = True
               print("multiple results")
            else:
               values = geocode_lib.initGoogleValues()
               values['google_partial_match'] = None
               print("no results")
            values['location_hash'] = parsed[0]
            values['google_result_count'] = len(geocode_results)
            values['enrichment_api_response'] = json.dumps(geocode_results)
            value = json.dumps(values).encode('utf-8')
            producer.send('geocode_output',value=value)
      consumer.commit()

except Exception as e:
  traceback.print_exc(e)
