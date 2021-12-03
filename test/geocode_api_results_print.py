import googlemaps
gmaps = googlemaps.Client(key='{ENTER_YOUR_API_KEY}')
geocode_result = gmaps.geocode('1600 Amphitheatre Parkway, Mountain View, CA')
print(geocode_result)
