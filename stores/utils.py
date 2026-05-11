import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat / 2) ** 2 + \
        math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2

    c = 2 * math.asin(math.sqrt(a))
    return R * c
def estimate_time(distance_km, speed_kmh=30):
    return (distance_km / speed_kmh) * 60  # phút
