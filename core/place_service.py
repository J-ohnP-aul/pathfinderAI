from dataclasses import dataclass
import json
from math import asin, cos, radians, sin, sqrt
import os
from typing import Protocol
from urllib.parse import urlencode
from urllib.request import Request, urlopen


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
                # Additional Nature & Outdoors
        Place('uhuru-gardens', 'Uhuru Gardens', 'nature', -1.3092, 36.8178, 'Langata Road, Nairobi', 'Largest public park with memorial grounds, peaceful walking paths, and picnic areas with mature trees.', 0, 60, 4.3, 'Open daily, 06:00-19:00'),
        Place('nairobi-safari-walk', 'Nairobi Safari Walk', 'nature', -1.3667, 36.7417, 'Magadi Road, Nairobi', 'Elevated boardwalk through wildlife habitats with views of zebra, giraffe, and antelope near the National Park.', 600, 90, 4.5, 'Open daily, 09:00-18:00'),
        Place('oloolua-nature-trail', 'Oloolua Nature Trail', 'nature', -1.3142, 36.7144, 'Karen Road, Karen', 'Forest trail featuring caves, a small waterfall, and natural pools in a tranquil woodland setting.', 200, 120, 4.4, 'Open daily, 08:00-17:00'),
        Place('nairobi-dam', 'Nairobi Dam', 'nature', -1.3250, 36.7750, 'Magadi Road, Nairobi', 'Scenic reservoir popular for rowing, sunset walks, and birdwatching with views across the water.', 100, 90, 4.1, 'Open daily, 06:00-18:00'),
        Place('city-park', 'City Park', 'relaxation', -1.2842, 36.8367, 'Limuru Road, Nairobi', 'Historic park with mature trees, jogging trails, birdwatching, and quiet picnic spots in a lush setting.', 0, 90, 4.3, 'Open daily, 06:00-18:00'),
        Place('michuki-memorial-park', 'Michuki Memorial Park', 'relaxation', -1.2933, 36.8142, 'Uhuru Highway, Nairobi', 'Riverside park along the Mathare River with walking paths and views of the city skyline.', 0, 45, 4.2, 'Open daily, 06:00-18:00'),
        Place('kereita-forest', 'Kereita Forest', 'adventure', -1.1150, 36.6400, 'Kereita, Kiambu County', 'Mountain biking, zip-lining, and scenic hikes through indigenous forest with waterfall views.', 500, 240, 4.6, 'Open daily, 08:00-17:00'),

        # Museums & Cultural
        Place('karen-blixen-museum', 'Karen Blixen Museum', 'history', -1.3133, 36.7142, 'Karen Road, Karen', 'Historic farmhouse where Out of Africa author lived, with original furnishings and beautiful gardens.', 1200, 60, 4.6, 'Open daily, 09:00-18:00'),
        Place('railway-museum', 'Nairobi Railway Museum', 'history', -1.2917, 36.8292, 'Station Road, Nairobi', 'Vintage locomotives and railway carriages showcasing East Africa\'s colonial rail history.', 800, 90, 4.4, 'Open daily, 08:00-17:00'),
        Place('kazuri-beads', 'Kazuri Beads Factory', 'shopping', -1.3250, 36.7150, 'Karen Road, Karen', 'Handmade ceramic bead workshop offering factory tours and unique handcrafted jewellery shopping.', 0, 45, 4.3, 'Open Mon-Sat, 08:00-17:00'),
        Place('bomas-of-kenya', 'Bomas of Kenya', 'history', -1.3233, 36.7483, 'Magadi Road, Nairobi', 'Replica traditional villages with cultural dance performances and live music daily.', 1000, 180, 4.5, 'Open daily, 10:00-18:00'),
        Place('national-archives', 'National Archives', 'history', -1.2867, 36.8192, 'Moi Avenue, Nairobi', 'Historic photographs, maps and documents tracing Kenya\'s history from colonial times to independence.', 0, 60, 4.2, 'Open Mon-Fri, 08:30-17:00'),
        Place('nairobi-gallery', 'Nairobi Gallery', 'history', -1.2867, 36.8192, 'Moi Avenue, Nairobi', 'Art exhibitions in Point House, a historic downtown building with colonial architecture.', 500, 45, 4.0, 'Open daily, 09:00-17:00'),

        # Shopping & Markets (new)
        Place('village-market', 'Village Market', 'shopping', -1.2342, 36.7975, 'Limuru Road, Gigiri', 'Upscale shopping center featuring art galleries, outdoor craft markets, and international dining options.', 0, 150, 4.4, 'Open daily, 09:00-21:00'),
        Place('junction-mall', 'The Junction Mall', 'shopping', -1.3017, 36.7783, 'Ngong Road, Nairobi', 'Popular shopping mall with local and international brands, supermarket, and food court.', 0, 120, 4.2, 'Open daily, 08:00-20:00'),
        Place('sarit-centre', 'Sarit Centre', 'shopping', -1.2633, 36.8033, 'Westlands Road, Westlands', 'One of Nairobi\'s oldest malls featuring a large bookshop, cinema, and diverse dining options.', 0, 120, 4.1, 'Open daily, 08:00-20:00'),
        Place('two-rivers-mall', 'Two Rivers Mall', 'shopping', -1.2058, 36.8350, 'Northern Bypass, Ruaka', 'Massive modern mall with cinema, theme park, dining, ice skating, and entertainment for families.', 0, 180, 4.3, 'Open daily, 09:00-21:00'),
        Place('yaya-centre', 'Yaya Centre', 'shopping', -1.2858, 36.7917, 'Argwings Kodhek Road, Hurlingham', 'Mid-range shopping center with a good grocery store, cafes, and variety of retail shops.', 0, 90, 4.0, 'Open daily, 08:00-20:00'),
        Place('gikomba-market', 'Gikomba Market', 'shopping', -1.2783, 36.8358, 'Gikomba, Nairobi', 'East Africa\'s largest open-air second-hand clothes market, famous for affordable vintage finds.', 0, 180, 3.8, 'Open daily, 06:00-18:00'),
        Place('city-market', 'City Market', 'shopping', -1.2850, 36.8183, 'Moi Avenue, Nairobi', 'Historic covered market with fresh produce, flowers, and traditional Kenyan spices.', 0, 60, 4.1, 'Open daily, 06:00-18:00'),
        Place('muthurwa-market', 'Muthurwa Market', 'shopping', -1.2817, 36.8300, 'Muthurwa, Nairobi', 'Wholesale market specializing in electronics, hardware, and household goods at bargain prices.', 0, 90, 3.7, 'Open daily, 06:00-17:00'),

        # Food & Dining Hubs
        Place('kosewe-restaurant', 'K\'osewe Restaurant', 'food', -1.2750, 36.8050, 'Wood Avenue, Kilimani', 'Iconic Kenyan restaurant famous for traditional fish, nyama choma, and lively dining atmosphere.', 2000, 90, 4.3, 'Open daily, 11:00-23:00'),
        Place('carnivore-restaurant', 'Carnivore Restaurant', 'food', -1.3433, 36.7433, 'Langata Road, Nairobi', 'Legendary meat feast with game meats including ostrich, crocodile, and carving service.', 4000, 120, 4.5, 'Open daily, 12:00-23:00'),
        Place('nairobi-street-kitchen', 'Nairobi Street Kitchen', 'food', -1.2733, 36.8050, 'Wood Avenue, Kilimani', 'Vibrant container park with diverse street food vendors serving global and local flavours.', 1500, 90, 4.3, 'Open daily, 11:00-23:00'),
        Place('jiko-restaurant', 'Jiko Restaurant', 'food', -1.2933, 36.8033, 'Nairobi City Centre', 'Fine dining featuring Swahili and coastal cuisine with stunning city views.', 3000, 120, 4.4, 'Open daily, 12:00-22:00'),
        Place('talisman-restaurant', 'Talisman Restaurant', 'food', -1.3267, 36.7133, 'Karen Road, Karen', 'Popular garden restaurant with unique fusion cuisine and outdoor dining under the trees.', 2500, 90, 4.6, 'Open daily, 10:00-23:00'),
        Place('seven-seafood', 'Seven Seafood & Grill', 'food', -1.2650, 36.7983, 'Westlands Road, Westlands', 'Upscale seafood restaurant and grill with premium ocean-fresh offerings.', 3500, 90, 4.4, 'Open daily, 12:00-22:00'),
        Place('mama-oliech', 'Mama Oliech Restaurant', 'food', -1.2833, 36.8250, 'Kenyatta Avenue, Nairobi', 'Famous for fried tilapia and traditional Kenyan dishes in a casual downtown setting.', 1200, 60, 4.2, 'Open daily, 10:00-21:00'),
        Place('java-house', 'Java House', 'food', -1.2700, 36.8100, 'Multiple Locations, Nairobi', 'Kenya\'s favorite casual cafe chain known for great coffee, breakfast, and affordable meals.', 800, 60, 4.0, 'Open daily, 07:00-22:00'),

        # Nightlife
        Place('alchemist', 'Alchemist', 'adventure', -1.2667, 36.7983, 'Westlands, Nairobi', 'Popular outdoor bar with live music, DJ sets, and a vibrant social atmosphere.', 1000, 180, 4.4, 'Open daily, 17:00-03:00'),
        Place('brew-bistro', 'Brew Bistro', 'food', -1.2650, 36.8000, 'Westlands Road, Westlands', 'Microbrewery and restaurant offering craft beers, live music, and rooftop city views.', 1500, 120, 4.3, 'Open daily, 12:00-02:00'),
        Place('mercury-lounge', 'Mercury Lounge', 'food', -1.2833, 36.7950, 'Ngong Road, Nairobi', 'Rooftop lounge with panoramic views of the city, cocktails, and sophisticated dining.', 2000, 120, 4.2, 'Open daily, 17:00-02:00'),
        Place('k1-klub-house', 'K1 Klub House', 'food', -1.2667, 36.8000, 'Westlands, Nairobi', 'Long-standing outdoor entertainment spot with live bands, dining, and a friendly atmosphere.', 1000, 180, 4.0, 'Open daily, 10:00-03:00'),

        # Historical Sites
        Place('kicc', 'Kenyatta International Conference Centre', 'history', -1.2883, 36.8233, 'City Square, Nairobi', 'Iconic 32-story tower with observation deck offering stunning panoramic city views.', 500, 45, 4.4, 'Open daily, 08:00-18:00'),
        Place('august-7-memorial', 'August 7th Memorial Park', 'history', -1.2850, 36.8183, 'Moi Avenue, Nairobi', 'Peaceful memorial garden commemorating the 1998 US Embassy bombing victims.', 0, 30, 4.3, 'Open daily, 06:00-18:00'),
        Place('war-cemetery', 'Nairobi War Cemetery', 'history', -1.2917, 36.8250, 'Ngong Road, Nairobi', 'Commonwealth war graves from World War II with beautifully maintained grounds.', 0, 45, 4.2, 'Open daily, 07:00-17:00'),

        # Adventure & Activities
        Place('nairobi-national-park', 'Nairobi National Park', 'adventure', -1.3700, 36.7800, 'Magadi Road, Nairobi', 'Drive through a national park with wildlife viewing against a city skyline backdrop.', 1500, 180, 4.7, 'Open daily, 06:00-19:00'),
        Place('giraffe-centre', 'Giraffe Centre', 'adventure', -1.3300, 36.7183, 'Karen Road, Karen', 'Feed and interact with endangered Rothschild\'s giraffes at this conservation center.', 1200, 60, 4.8, 'Open daily, 09:00-17:00'),
        Place('sheldrick-elephants', 'Sheldrick Elephant Orphanage', 'adventure', -1.3567, 36.7433, 'Magadi Road, Nairobi', 'Rescue center for baby elephants with daily feeding sessions and educational talks.', 1500, 60, 4.9, 'Open daily, 11:00-12:00'),
        Place('mamba-village', 'Mamba Village', 'adventure', -1.3317, 36.7417, 'Langata Road, Nairobi', 'Crocodile farm with feeding demonstrations, boat rides, and natural history exhibits.', 800, 90, 4.1, 'Open daily, 09:00-18:00'),
        Place('paradise-lost', 'Paradise Lost', 'adventure', -1.1483, 36.7650, 'Kiambu Road, Kiambu', 'Cave exploration, boat rides, zip-lining, and birdwatching in a scenic natural setting.', 600, 180, 4.3, 'Open daily, 08:00-18:00'),
        Place('karura-caves', 'Karura Caves', 'adventure', -1.2350, 36.8400, 'Karura Forest, Nairobi', 'Historical caves within Karura Forest used during colonial times, accessible via forest trails.', 200, 60, 4.5, 'Open daily, 06:00-18:00'),

        # Sports & Recreation
        Place('nairobi-gymkhana', 'Nairobi Gymkhana', 'adventure', -1.2733, 36.8167, 'Ngong Road, Nairobi', 'Premier sports club with golf, swimming, tennis, and comprehensive fitness facilities.', 2000, 180, 4.2, 'Open daily, 06:00-22:00'),
        Place('royal-nairobi-golf', 'Royal Nairobi Golf Club', 'adventure', -1.2833, 36.8067, 'Ngong Road, Nairobi', 'Prestigious 18-hole golf course set in serene grounds with clubhouse dining.', 3000, 240, 4.4, 'Open daily, 06:00-19:00'),
        Place('gokart-nairobi', 'GoKart Nairobi', 'adventure', -1.2333, 36.8750, 'Kasarani, Nairobi', 'Thrilling go-kart racing track with competitive karts for adults and children.', 1200, 30, 4.3, 'Open daily, 10:00-20:00'),

        # Wellness
        Place('sankara-spa', 'Sankara Spa', 'relaxation', -1.2633, 36.7983, 'Woodvale Road, Westlands', 'Luxury urban spa offering massages, facials, and wellness treatments in a tranquil setting.', 5000, 90, 4.6, 'Open daily, 09:00-21:00'),
        Place('mango-tree-yoga', 'The Mango Tree', 'relaxation', -1.3167, 36.7200, 'Karen, Nairobi', 'Peaceful yoga and wellness center with classes, meditation, and healthy dining.', 1500, 90, 4.4, 'Open daily, 06:00-19:00'),
        Place('hemingways-spa', 'Hemingways Spa', 'relaxation', -1.3417, 36.7200, 'Karen, Nairobi', 'Luxury spa overlooking Ngong Hills with world-class treatments and serene environment.', 6000, 120, 4.7, 'Open daily, 08:00-20:00'),

        # Hidden Gems
        Place('nairobi-archery', 'Nairobi Archery Club', 'adventure', -1.2283, 36.8967, 'Kasarani, Nairobi', 'Archery ranges with beginner lessons and friendly competitions in a casual setting.', 1000, 60, 4.1, 'Open daily, 09:00-18:00'),
        Place('ice-rink-nairobi', 'Ice Rink Nairobi', 'adventure', -1.2742, 36.8583, 'Panari Hotel, Mombasa Road', 'Kenya\'s first indoor ice skating rink offering skating sessions and hockey games.', 1200, 60, 4.2, 'Open daily, 10:00-22:00'),
        Place('the-waterfront', 'The Waterfront', 'food', -1.3400, 36.7183, 'Karen, Nairobi', 'New entertainment hub in Karen with waterfront dining, activities, and family fun.', 2000, 180, 4.3, 'Open daily, 10:00-23:00'),
        Place('kitengela-glass', 'Kitengela Glass', 'shopping', -1.3750, 36.9500, 'Kitengela, Kajiado County', 'Unique art glass studio with whimsical sculptures, glassblowing demonstrations, and quirky decor.', 500, 90, 4.5, 'Open Mon-Sat, 09:00-17:00'),

        # Budget-Friendly Spots
        Place('uhuru-park', 'Uhuru Park', 'relaxation', -1.2867, 36.8142, 'Uhuru Highway, Nairobi', 'Downtown park featuring a lake, boat rides, and panoramic city views.', 0, 90, 4.1, 'Open daily, 06:00-18:00'),
        Place('ku-botanical-garden', 'Kenyatta University Botanical Garden', 'nature', -1.1767, 36.9283, 'Kenyatta University, Nairobi', 'Peaceful academic gardens with diverse plant collections and walking paths.', 0, 60, 4.0, 'Open daily, 08:00-17:00'),
        Place('nairobi-riverside', 'Nairobi Riverside Walk', 'relaxation', -1.2833, 36.8200, 'City Centre, Nairobi', 'Walking path along the river through downtown with art installations and green spaces.', 0, 45, 3.9, 'Open daily, 06:00-18:00'),
        Place('kibera-tours', 'Kibera Community Tours', 'history', -1.3133, 36.7833, 'Kibera, Nairobi', 'Community-led walking tours offering authentic insights into daily life in the famous settlement.', 1000, 120, 4.3, 'Open daily, 09:00-16:00'),
            )

    def nearby(self, latitude: float, longitude: float, radius_km: float = 15) -> list[Place]:
        results = []
        for place in self.PLACES:
            distance = distance_km(latitude, longitude, place.latitude, place.longitude)
            if distance <= radius_km:
                results.append(place)
        return sorted(results, key=lambda place: distance_km(latitude, longitude, place.latitude, place.longitude))


class OpenStreetMapPlaceProvider:
    """Fetch nearby mapped places from the free Overpass API."""

    def __init__(self, fallback: PlaceProvider | None = None):
        self.fallback = fallback or LocalPlaceProvider()

    def nearby(self, latitude: float, longitude: float, radius_km: float = 15) -> list[Place]:
        radius_m = min(int(radius_km * 1000), 25000)
        query = f'''[out:json][timeout:10];(
          nwr(around:{radius_m},{latitude},{longitude})[amenity~"restaurant|cafe|fast_food|pub|bar|cinema|theatre|arts_centre|museum"];
          nwr(around:{radius_m},{latitude},{longitude})[tourism~"attraction|museum|gallery|hotel|viewpoint"];
          nwr(around:{radius_m},{latitude},{longitude})[leisure~"park|garden|nature_reserve|sports_centre"];
          nwr(around:{radius_m},{latitude},{longitude})[shop];
        );out center tags;'''
        request = Request(
            'https://overpass-api.de/api/interpreter',
            data=query.encode(),
            headers={'User-Agent': os.getenv('OSM_USER_AGENT', 'PathfinderAI/1.0')},
        )
        try:
            with urlopen(request, timeout=15) as response:
                elements = json.load(response).get('elements', [])
            places = [place_from_osm_data(item) for item in elements]
            places = [
                place for place in places
                if place is not None
                and distance_km(latitude, longitude, place.latitude, place.longitude) <= radius_km
            ]
            if places:
                return sorted(places, key=lambda place: distance_km(
                    latitude, longitude, place.latitude, place.longitude,
                ))
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
            pass
        return self.fallback.nearby(latitude, longitude, radius_km)


class GeminiPlaceProvider:
    """Use Gemini for live place suggestions, with a local fallback."""

    def __init__(self, fallback: PlaceProvider | None = None):
        self.fallback = fallback or OpenStreetMapPlaceProvider()

    def nearby(self, latitude: float, longitude: float, radius_km: float = 15) -> list[Place]:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return self.fallback.nearby(latitude, longitude, radius_km)

        prompt = (
            'Return real places near the supplied coordinates. Use only places that are '
            'likely to exist, and return valid JSON only as an array of objects. '
            'Each object must contain: id, name, category, latitude, longitude, address, '
            'description, estimated_cost (integer KSh), visit_duration_minutes (integer), '
            'rating (number from 0 to 5), and opening_info. '
            f'Coordinates: {latitude}, {longitude}. Radius: {radius_km} km. '
            'Include up to 20 varied food, nature, history, culture, adventure, nightlife, '
            'shopping, and relaxation places.'
        )

        try:
            model_name = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
            try:
                from google import genai
                from google.genai import types

                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.1,
                        max_output_tokens=4000,
                        response_mime_type='application/json',
                    ),
                )
            except ImportError:
                import google.generativeai as legacy_genai

                legacy_genai.configure(api_key=api_key)
                response = legacy_genai.GenerativeModel(model_name).generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.1,
                        'max_output_tokens': 4000,
                        'response_mime_type': 'application/json',
                    },
                )

            places = json.loads(getattr(response, 'text', '') or '')
            parsed_places = [place_from_ai_data(item) for item in places]
            parsed_places = [
                place for place in parsed_places
                if place is not None
                and distance_km(latitude, longitude, place.latitude, place.longitude) <= radius_km
            ]
            if parsed_places:
                return parsed_places
        except (ValueError, TypeError, json.JSONDecodeError, ImportError):
            pass
        except Exception:
            pass

        return self.fallback.nearby(latitude, longitude, radius_km)


def place_from_ai_data(data: dict) -> Place | None:
    """Convert and validate one model result before it reaches the UI."""
    try:
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
            return None
        return Place(
            id=str(data['id']),
            name=str(data['name']),
            category=str(data['category']),
            latitude=latitude,
            longitude=longitude,
            address=str(data.get('address', '')),
            description=str(data.get('description', '')),
            estimated_cost=max(0, int(data.get('estimated_cost', 0))),
            visit_duration_minutes=max(1, int(data.get('visit_duration_minutes', 60))),
            rating=min(5, max(0, float(data.get('rating', 0)))),
            opening_info=str(data.get('opening_info', 'Hours not available')),
        )
    except (KeyError, TypeError, ValueError):
        return None


def place_from_osm_data(data: dict) -> Place | None:
    tags = data.get('tags', {})
    coordinates = data.get('center', data)
    name = tags.get('name')
    if not name or 'lat' not in coordinates or 'lon' not in coordinates:
        return None
    category = osm_category(tags)
    return Place(
        id=f"osm-{data.get('type', 'place')}-{data.get('id')}",
        name=name,
        category=category,
        latitude=float(coordinates['lat']),
        longitude=float(coordinates['lon']),
        address=', '.join(value for value in [tags.get('addr:street'), tags.get('addr:city')] if value),
        description=f'{name} in the selected area.',
        estimated_cost=0,
        visit_duration_minutes=60,
        rating=0,
        opening_info=tags.get('opening_hours', 'Opening hours not available'),
    )


def osm_category(tags: dict) -> str:
    if tags.get('amenity') in {'restaurant', 'cafe', 'fast_food'}:
        return 'food'
    if tags.get('amenity') in {'pub', 'bar'}:
        return 'nightlife'
    if tags.get('amenity') in {'museum', 'theatre', 'arts_centre'} or tags.get('tourism') in {'museum', 'gallery'}:
        return 'history'
    if tags.get('shop'):
        return 'shopping'
    if tags.get('leisure') in {'park', 'garden', 'nature_reserve'}:
        return 'nature'
    return 'adventure'


KNOWN_LOCATIONS = {
    'nairobi cbd': (-1.2833, 36.8167),
    'nairobi city centre': (-1.2833, 36.8167),
    'nairobi city center': (-1.2833, 36.8167),
    'kisumu': (-0.1022, 34.7617),
    'kisumu cbd': (-0.1022, 34.7617),
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
        latitude, longitude = geocode_kenyan_location(location_name)
        return (latitude, longitude) if latitude is not None and longitude is not None else None
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None
    return latitude, longitude


def geocode_kenyan_location(location_name: str) -> tuple[float | None, float | None]:
    """Resolve an arbitrary Kenyan place name using free OSM geocoding."""
    query = urlencode({
        'q': location_name,
        'format': 'jsonv2',
        'limit': 1,
        'countrycodes': 'ke',
    })
    request = Request(
        f'https://nominatim.openstreetmap.org/search?{query}',
        headers={'User-Agent': os.getenv('OSM_USER_AGENT', 'PathfinderAI/1.0')},
    )
    try:
        with urlopen(request, timeout=5) as response:
            results = json.load(response)
        if not results:
            return None, None
        return float(results[0]['lat']), float(results[0]['lon'])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        return None, None


def geocode_ip_location() -> tuple[float | None, float | None]:
    """Resolve approximate location from IP address using ip-api.com."""
    request = Request(
        'http://ip-api.com/json/',
        headers={'User-Agent': os.getenv('OSM_USER_AGENT', 'PathfinderAI/1.0')},
    )
    try:
        with urlopen(request, timeout=5) as response:
            data = json.load(response)
        if data.get('status') == 'success' and data.get('lat') and data.get('lon'):
            return float(data['lat']), float(data['lon'])
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError):
        pass
    return None, None


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
