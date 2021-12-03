import json

#  Construct a dictionary of keywords to keep track of when discovered while
#  traversing the result from google (ess compileResultTypes below).
#  Dictionary lookup is hashed O(1), so this provides an efficient way to
#  determining keyword relevance.  This list is a list of keywords to avoid.
#
non_relevant_types = { 
   'administrative_area_level_1':True,
   'administrative_area_level_2':True,
   'administrative_area_level_3':True,
   'administrative_area_level_4':True,
   'administrative_area_level_5':True,
   'continent':True,
   'country':True,
   'colloquial_area':True,
   'locality':True,
   'sublocality':True,
   'sublocality_level_1':True,
   'sublocality_level_2':True,
   'sublocality_level_3':True,
   'sublocality_level_4':True,
   'sublocality_level_5':True,
   'sublocality_area_level_1':True,
   'sublocality_area_level_2':True,
   'sublocality_area_level_3':True,
   'sublocality_area_level_4':True,
   'sublocality_area_level_5':True,
   'neighborhood':True,
   'political':True,
   'postal_code':True,
   'postal_town':True,
   'ward':True,
   'route':True,
   'premise':True
}

#  Create default google result values.  This provides a value even when
#  google returns no results.
#
def initGoogleValues():
   return {
      'google_result_type':[],
      'formatted_address':None,
      'latitude':None,
      'longitude':None,
      'google_place_id':None,
      'location_type':None,
      'long_street_number':None,
      'short_street_number':None,
      'long_route':None,
      'short_route':None,
      'long_postal_code':None,
      'short_postal_code':None,
      'long_postal_code_suffix':None,
      'short_postal_code_suffix':None,
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

#  Traverse the google result tree looking for the keyword "types" and when
#  found, add elements of the array it denotes.  The result tree is
#  hierarchial, and child elements may be found via traversal of both lists
#  and dictionaries, so do both. Only add interesting elements as defined by
#  not including in the non_relevant types dict.  At the end convert to a set
#  and then back to a list to remove duplicates.
#
def compileResultTypes(root):
   types = []
   if isinstance(root,dict):
      for k in root:
         v = root[k]
         if k == 'types': 
            for v1 in v: 
               if non_relevant_types.get(v1,None) == None: types.append(v1)
         elif isinstance(v,dict) or isinstance(v,list): types.extend(compileResultTypes(v))
   elif isinstance(root,list):
      for v in root:
         if isinstance(v,dict) or isinstance(v,list): types.extend(compileResultTypes(v))
   return list(set(types))

#  Extract relevant values from a google geocode result and place them in a
#  dictionary that will later be incorporated in a database.
#
#  Depending on the type of address and it's location, difference values will
#  be made available to check for their existance.  Use default values to fill
#  in for lack of them being available in the geocode result.
#
#  The political term seems to be a qualifier.  e.g. country, can be a
#  political thing, or it might be a postal thing.
#
def extractGoogleValues(geocodeResult):
   values = initGoogleValues()
   addressComponents = geocodeResult.get('address_components')
   formattedAddress = geocodeResult.get('formatted_address')
   geometry = geocodeResult.get('geometry')
   googlePlaceId = geocodeResult.get('place_id')
   #print(geocodeResult)
   if addressComponents != None:
      for v in addressComponents:
         if v.get('types') != None and len(v['types']) > 0:
            if v['types'][0] == 'street_number':
               values['long_street_number'] = v['long_name']
               values['short_street_number'] = v['short_name']
            elif v['types'][0] == 'route':
               values['long_route'] = v['long_name']
               values['short_route'] = v['short_name']
            elif v['types'][0] == 'postal_code':
               values['long_postal_code'] = v['long_name']
               values['short_postal_code'] = v['short_name']
            elif v['types'][0] == 'postal_code_suffix':
               values['long_postal_code_suffix'] = v['long_name']
               values['short_postal_code_suffix'] = v['short_name']
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
      values['location_type'] = json.dumps({ 'types':geometry['location_type'] })
   if formattedAddress != None: values['formatted_address'] = formattedAddress
   if googlePlaceId != None: values['google_place_id'] = googlePlaceId
   values['google_result_type'] = json.dumps({ 'types':compileResultTypes(geocodeResult) })
   return values
