from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt
from typing import Protocol


@dataclass(frozen=True)
class Place:
    id: str
    name: str
    category: str
    latitude: float
    longitude: float
    address: str
    description: str
    estimated_cost: int
    visit_duration_minutes: int
    rating: float
    opening_info: str


class PlaceProvider(Protocol):
    def nearby(self, latitude: float, longitude: float, radius_km: float = 15) -> list[Place]:
        ...


class LocalPlaceProvider:
    """Offline provider used until a configured external places API is added."""

    PLACES = (
        Place('karura-forest', 'Karura Forest', 'nature', -1.2465, 36.8330, 'Limuru Road, Nairobi', 'Quiet forest trails and waterfalls for an easy outdoor escape.', 500, 150, 4.7, 'Open daily, 06:00-18:00'),
        Place('nairobi-national-museum', 'Nairobi National Museum', 'history', -1.2692, 36.8172, 'Museum Hill Road, Nairobi', 'Galleries covering Kenyan history, art, and natural heritage.', 800, 120, 4.5, 'Open daily, 08:30-17:30'),
        Place('maasai-market', 'Maasai Market', 'shopping', -1.2833, 36.8167, 'City Centre, Nairobi', 'A lively market for locally made crafts, art, and gifts.', 1000, 90, 4.3, 'Open on selected days, 09:00-18:00'),
        Place('arboretum', 'Nairobi Arboretum', 'relaxation', -1.2700, 36.8015, 'State House Road, Nairobi', 'Shaded walking paths and open lawns close to the city centre.', 300, 90, 4.4, 'Open daily, 06:00-18:00'),
        Place('westlands-food-market', 'Westlands Food Market', 'food', -1.2640, 36.8040, 'Westlands, Nairobi', 'A casual mix of local flavours and international street food.', 1800, 120, 4.2, 'Open daily, 10:00-22:00'),
        Place('ngong-hills', 'Ngong Hills', 'adventure', -1.3830, 36.6560, 'Ngong, Kajiado County', 'Rolling ridge trails with broad views across the Great Rift Valley.', 700, 240, 4.6, 'Open daily, 08:00-17:00'),
    )

    def nearby(self, latitude: float, longitude: float, radius_km: float = 15) -> list[Place]:
        results = []
        for place in self.PLACES:
            distance = distance_km(latitude, longitude, place.latitude, place.longitude)
            if distance <= radius_km:
                results.append(place)
        return sorted(results, key=lambda place: distance_km(latitude, longitude, place.latitude, place.longitude))


KNOWN_LOCATIONS = {
    'nairobi cbd': (-1.2833, 36.8167),
    'nairobi city centre': (-1.2833, 36.8167),
    'nairobi city center': (-1.2833, 36.8167),
    'westlands': (-1.2640, 36.8040),
    'karura forest': (-1.2465, 36.8330),
    'ngong hills': (-1.3830, 36.6560),
}


def resolve_location(location_name: str) -> tuple[float, float] | None:
    normalized_name = ' '.join(location_name.lower().split())
    if normalized_name in KNOWN_LOCATIONS:
        return KNOWN_LOCATIONS[normalized_name]
    try:
        latitude, longitude = (float(value.strip()) for value in location_name.split(',', 1))
    except (ValueError, TypeError):
        return None
    return latitude, longitude


def distance_km(latitude_a: float, longitude_a: float, latitude_b: float, longitude_b: float) -> float:
    earth_radius_km = 6371
    latitude_delta = radians(latitude_b - latitude_a)
    longitude_delta = radians(longitude_b - longitude_a)
    haversine = sin(latitude_delta / 2) ** 2 + cos(radians(latitude_a)) * cos(radians(latitude_b)) * sin(longitude_delta / 2) ** 2
    return earth_radius_km * 2 * asin(sqrt(haversine))


def serialize_place(place: Place, latitude: float, longitude: float) -> dict:
    return {
        'id': place.id,
        'name': place.name,
        'category': place.category,
        'latitude': place.latitude,
        'longitude': place.longitude,
        'address': place.address,
        'description': place.description,
        'estimated_cost': place.estimated_cost,
        'visit_duration_minutes': place.visit_duration_minutes,
        'rating': place.rating,
        'opening_info': place.opening_info,
        'distance_km': round(distance_km(latitude, longitude, place.latitude, place.longitude), 2),
    }


def discover_places(provider: PlaceProvider, latitude: float, longitude: float,
                    budget: int, available_time_minutes: int,
                    category: str = '', limit: int = 5) -> list[dict]:
    places = provider.nearby(latitude, longitude)
    if category:
        places = [place for place in places if place.category == category]
    return [
        serialize_place(place, latitude, longitude)
        for place in places
        if place.estimated_cost <= budget
        and place.visit_duration_minutes <= available_time_minutes
    ][:limit]
