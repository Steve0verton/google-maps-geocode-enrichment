import psycopg2
import psycopg2.extras

#  multi update given an array of records.  Efficiently update database
#  records using 1 statement for multiple records.  Assume the items
#  are stored in a dictionary.  For convenience, the names of the columns
#  in the database are the same as the fields in the dict.  Type convert
#  from string by using postgres implicit conversion though applying
#  the type conversion operator.
#
def doPgUpdate(conn,updateValues):
   cur = conn.cursor()
   sql = """
      UPDATE ref_location AS t
         SET
           last_update_dttm = now(),
           enrichment_api_response = e.enrichment_api_response::jsonb,
           google_result_type = e.google_result_type::jsonb,
           enrichment_status = 'COMPLETE',
           google_partial_match = e.google_partial_match::boolean,
           google_result_count = e.google_result_count,
           formatted_address = e.formatted_address,
           google_place_id = e.google_place_id,
           location_type = e.location_type::jsonb,
           latitude = e.latitude::numeric,
           longitude = e.longitude::numeric,
           long_street_number = e.long_street_number,
           short_street_number = e.short_street_number,
           long_route = e.long_route,
           short_route = e.short_route,
           long_postal_code = e.long_postal_code,
           short_postal_code = e.short_postal_code,
           long_postal_code_suffix = e.long_postal_code_suffix,
           short_postal_code_suffix = e.short_postal_code_suffix,
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
         google_result_type,
         google_partial_match,
         google_result_count,
         formatted_address,
         google_place_id,
         location_type,
         latitude,
         longitude,
         long_street_number,
         short_street_number,
         long_route,
         short_route,
         long_postal_code,
         short_postal_code,
         long_postal_code_suffix,
         short_postal_code_suffix,
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
      %(google_result_type)s,
      %(google_partial_match)s,
      %(google_result_count)s,
      %(formatted_address)s,
      %(google_place_id)s,
      %(location_type)s,
      %(latitude)s,
      %(longitude)s,
      %(long_street_number)s,
      %(short_street_number)s,
      %(long_route)s,
      %(short_route)s,
      %(long_postal_code)s,
      %(short_postal_code)s,
      %(long_postal_code_suffix)s,
      %(short_postal_code_suffix)s,
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
   psycopg2.extras.execute_values(cur,sql,updateValues,template=updateTmpl)
   conn.commit()
   cur.close()
