import asyncio
from winrt.windows.devices.geolocation import Geolocator


async def get_location():
    locator = Geolocator()
    pos = await locator.get_geoposition_async()

    lat = pos.coordinate.point.position.latitude
    lon = pos.coordinate.point.position.longitude

    return (lat,lon)

