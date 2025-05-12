import os
from geopy.geocoders import GoogleV3
from geopy.extra.rate_limiter import RateLimiter

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

geolocator = GoogleV3(api_key=API_KEY, timeout=5)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)



def geocode_address(area: str, address: str):
    """Return (latitude, longitude) 或 (None, None)"""
    query = f"{address}, {area}, Western Australia, Australia"
    loc = geocode(query)
    if loc:
        return loc.latitude, loc.longitude
    return None, None