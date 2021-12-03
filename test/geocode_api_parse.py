import psycopg2
import psycopg2.extras
import googlemaps
import json
import traceback

def initValues():
   return {
      'formatted_address':None,
      'latitude':None,
      'longitude':None,
      'long_street_number':None,
      'short_street_number':None,
      'long_route':None,
      'short_route':None,
      'long_postal_code':None,
      'short_postal_code':None,
      'long_country':None,
      'short_country':None,
      'long_locality':None,
      'short_locality':None,
      'long_admin_area_level_1':None,
      'short_admin_area_level_1':None,
      'long_admin_area_level_2':None,
      'short_admin_area_level_2':None,
      'long_admin_area_level_3':None,
      'short_admin_area_level_3':None,
      'long_admin_area_level_4':None,
      'short_admin_area_level_4':None,
      'long_admin_area_level_5':None,
      'short_admin_area_level_5':None
   }

#
#  The political term seems to be a qualifier.  e.g. country, can be a political thing, or it might
#  be a postal thing.
#
def extractValues(geocodeResult):
   values = initValues()
   addressComponents = geocodeResult.get('address_components')
   formattedAddress = geocodeResult.get('formatted_address')
   geometry = geocodeResult.get('geometry')
   #print(geocodeResult)
   if addressComponents != None:
      for v in addressComponents:
         if v['types'][0] == 'street_number':
            values['long_street_number'] = v['long_name']
            values['short_street_number'] = v['short_name']
         elif v['types'][0] == 'route':
            values['long_route'] = v['long_name']
            values['short_route'] = v['short_name']
         elif v['types'][0] == 'postal_code':
            values['long_postal_code'] = v['long_name']
            values['short_postal_code'] = v['short_name']
         elif v['types'][0] == 'country':
            values['long_country'] = v['long_name']
            values['short_country'] = v['short_name']
         elif v['types'][0] == 'locality':
            values['long_locality'] = v['long_name']
            values['short_locality'] = v['short_name']
         elif v['types'][0] == 'administrative_area_level_1':
            values['long_admin_area_level_1'] = v['long_name']
            values['short_admin_area_level_1'] = v['short_name']
         elif v['types'][0] == 'administrative_area_level_2':
            values['long_admin_area_level_2'] = v['long_name']
            values['short_admin_area_level_2'] = v['short_name']
         elif v['types'][0] == 'administrative_area_level_3':
            values['long_admin_area_level_3'] = v['long_name']
            values['short_admin_area_level_3'] = v['short_name']
         elif v['types'][0] == 'administrative_area_level_4':
            values['long_admin_area_level_4'] = v['long_name']
            values['short_admin_area_level_4'] = v['short_name']
         elif v['types'][0] == 'administrative_area_level_5':
            values['long_admin_area_level_5'] = v['long_name']
            values['short_admin_area_level_5'] = v['short_name']
   if geometry != None:
      values['latitude'] = geometry['location']['lat']
      values['longitude'] = geometry['location']['lng']
   if formattedAddress != None: values['formatted_address'] = formattedAddress
   return values
#
#  multi update given an array of records
#
def doUpdate(db,updateValues):
   c = db.cursor()
   sql = """
      UPDATE core.ref_location_2 AS t
         SET
           last_update_dttm = now(),
           enrichment_api_response = e.enrichment_api_response::jsonb,
           enrichment_status = 'COMPLETE',
           google_partial_match = e.google_partial_match::boolean,
           formatted_address = e.formatted_address,
           latitude = e.latitude::numeric,
           longitude = e.longitude::numeric,
           long_street_number = e.long_street_number,
           short_street_number = e.short_street_number,
           long_route = e.long_route,
           short_route = e.short_route,
           long_postal_code = e.long_postal_code,
           short_postal_code = e.short_postal_code,
           long_country = e.long_country,
           short_country = e.short_country,
           long_locality = e.long_locality,
           short_locality = e.short_locality,
           long_admin_area_level_1 = e.long_admin_area_level_1,
           short_admin_area_level_1 = e.short_admin_area_level_1,
           long_admin_area_level_2 = e.long_admin_area_level_2,
           short_admin_area_level_2 = e.short_admin_area_level_2,
           long_admin_area_level_3 = e.long_admin_area_level_3,
           short_admin_area_level_3 = e.short_admin_area_level_3,
           long_admin_area_level_4 = e.long_admin_area_level_4,
           short_admin_area_level_4 = e.short_admin_area_level_4,
           long_admin_area_level_5 = e.long_admin_area_level_5,
           short_admin_area_level_5 = e.short_admin_area_level_5
      FROM (VALUES %s) AS
      e(
         location_hash,
         enrichment_api_response,
         google_partial_match,
         formatted_address,
         latitude,
         longitude,
         long_street_number,
         short_street_number,
         long_route,
         short_route,
         long_postal_code,
         short_postal_code,
         long_country,
         short_country,
         long_locality,
         short_locality,
         long_admin_area_level_1,
         short_admin_area_level_1,
         long_admin_area_level_2,
         short_admin_area_level_2,
         long_admin_area_level_3,
         short_admin_area_level_3,
         long_admin_area_level_4,
         short_admin_area_level_4,
         long_admin_area_level_5,
         short_admin_area_level_5
      )
      WHERE e.location_hash = t.location_hash
   """
   updateTmpl = """(
      %(location_hash)s,
      %(enrichment_api_response)s,
      %(google_partial_match)s,
      %(formatted_address)s,
      %(latitude)s,
      %(longitude)s,
      %(long_street_number)s,
      %(short_street_number)s,
      %(long_route)s,
      %(short_route)s,
      %(long_postal_code)s,
      %(short_postal_code)s,
      %(long_country)s,
      %(short_country)s,
      %(long_locality)s,
      %(short_locality)s,
      %(long_admin_area_level_1)s,
      %(short_admin_area_level_1)s,
      %(long_admin_area_level_2)s,
      %(short_admin_area_level_2)s,
      %(long_admin_area_level_3)s,
      %(short_admin_area_level_3)s,
      %(long_admin_area_level_4)s,
      %(short_admin_area_level_4)s,
      %(long_admin_area_level_5)s,
      %(short_admin_area_level_5)s
   )"""
   psycopg2.extras.execute_values (c,sql,updateValues,template=updateTmpl,page_size=100)
   db.commit()


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
         values = extractValues(geocode_results[0])
         values['google_partial_match'] = False
         print("single result")
      elif len(geocode_results) > 1:
         values = extractValues(geocode_results[0])
         values['google_partial_match'] = True
         print("multiple results")
      else:
         values = initValues()
         values['google_partial_match'] = None
         print("no results")
      values['location_hash'] = row[0]
      values['enrichment_api_response'] = json.dumps(geocode_results)
      updates.append(values)
   doUpdate(conn,updates)

except Exception as e:
  traceback.print_exc(e)
