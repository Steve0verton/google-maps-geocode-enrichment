import googlemaps
import json
import psycopg2
import geocode_lib
import traceback

try:
   conn = psycopg2.connect(dbname='postgres',user='postgres')
   gmaps = googlemaps.Client(key='{ENTER_YOUR_API_KEY}')
   cur = conn.cursor()
   cur.execute( """
      SELECT
        location_hash,location FROM core.ref_location
        WHERE
          (enrichment_enabled AND (enrichment_status = '' OR enrichment_status IS null))
          OR (now() - last_update_dttm > interval '30 days')
      """)
   rows = cur.fetchall()
   updates = []
   for row in rows:
      geocode_results = gmaps.geocode(row[1])
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
      values['location_hash'] = row[0]
      values['google_result_count'] = len(geocode_results)
      values['enrichment_api_response'] = json.dumps(geocode_results)
      updates.append(values)
   geocode_lib.doPgUpdate(conn,updates)

except Exception as e:
  traceback.print_exc(e)
