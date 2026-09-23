import json

from django.contrib.auth.models import User
from django.test import TestCase

from . import views
from .models import UserPreference
from .place_service import LocalPlaceProvider, distance_km, resolve_location
from .recommendation_service import rank_recommendations


class UserPreferenceTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='traveler', password='test-pass-123')

	def test_preferences_page_requires_login(self):
		response = self.client.get('/profile/preferences/')

		self.assertRedirects(response, '/accounts/login/?next=/profile/preferences/')

	def test_preferences_page_creates_and_updates_preferences(self):
		self.client.login(username='traveler', password='test-pass-123')

		response = self.client.post('/profile/preferences/', {
			'interests': ['nature', 'culture'],
			'budget_preference': '3000',
			'preferred_transport': 'walking',
			'available_time_minutes': '240',
			'travel_companions': 'friends',
			'dietary_preferences': 'Vegetarian',
			'mobility_preferences': '',
		})

		self.assertRedirects(response, '/profile/preferences/')
		preference = UserPreference.objects.get(user=self.user)
		self.assertEqual(preference.interests, ['nature', 'culture'])
		self.assertEqual(preference.budget_preference, 3000)
		self.assertEqual(preference.available_time_minutes, 240)

	def test_preferences_api_is_user_scoped(self):
		self.client.login(username='traveler', password='test-pass-123')

		response = self.client.put(
			'/api/profile/preferences',
			data=json.dumps({
				'interests': ['food'],
				'budget_preference': 1500,
				'preferred_transport': 'public_transport',
				'available_time_minutes': 90,
				'travel_companions': 'solo',
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.json()['interests'], ['food'])
		self.assertEqual(UserPreference.objects.get(user=self.user).budget_preference, 1500)

	def test_preferences_api_rejects_invalid_json(self):
		self.client.login(username='traveler', password='test-pass-123')

		response = self.client.put(
			'/api/profile/preferences',
			data='not-json',
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 400)


class DiscoveryTests(TestCase):
	def setUp(self):
		views.place_provider = LocalPlaceProvider()

	def test_named_location_resolves_to_coordinates(self):
		self.assertEqual(resolve_location('Nairobi CBD'), (-1.2833, 36.8167))
		self.assertEqual(resolve_location('Kisumu'), (-0.1022, 34.7617))

	def test_provider_returns_nearby_places_in_distance_order(self):
		places = LocalPlaceProvider().nearby(-1.27, 36.82)

		self.assertGreater(len(places), 0)
		self.assertEqual(places, sorted(
			places,
			key=lambda place: distance_km(-1.27, 36.82, place.latitude, place.longitude),
		))

	def test_home_filters_places_by_budget_and_time(self):
		response = self.client.post('/', {
			'location_name': 'Nairobi',
			'latitude': '-1.27',
			'longitude': '36.82',
			'budget': '500',
			'available_time_minutes': '120',
			'category': '',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'August 7th Memorial Park')
		self.assertNotContains(response, 'Westlands Food Market')

	def test_home_accepts_named_location_without_coordinates(self):
		response = self.client.post('/', {
			'location_name': 'Nairobi CBD',
			'budget': '3000',
			'available_time_minutes': '240',
			'category': '',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Nearby places')
		self.assertContains(response, 'discovery-map')
		self.assertContains(response, '"latitude": -1.2833')
		self.assertContains(response, 'openstreetmap.org/export/embed.html')

	def test_location_coordinates_are_manual_inputs(self):
		response = self.client.get('/')

		self.assertContains(response, 'name="latitude"')
		self.assertContains(response, 'name="longitude"')

	def test_home_uses_leaflet_for_current_location(self):
		response = self.client.get('/')

		self.assertContains(response, 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css')
		self.assertContains(response, 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js')
		self.assertContains(response, 'id="current-location-map"')
		self.assertContains(response, 'navigator.geolocation.getCurrentPosition')

	def test_current_location_requires_browser_coordinates(self):
		response = self.client.post('/', {
			'location_name': 'Current location',
			'budget': '3000',
			'available_time_minutes': '240',
			'category': '',
		})

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'We need your device location before searching')

	def test_nearby_places_api_supports_category_filter(self):
		response = self.client.post('/api/places/nearby', data={
			'location_name': 'Nairobi',
			'latitude': -1.27,
			'longitude': 36.82,
			'budget': 3000,
			'available_time_minutes': 240,
			'category': 'nature',
		}, content_type='application/json')

		self.assertEqual(response.status_code, 200)
		places = response.json()['places']
		self.assertTrue(places)
		self.assertTrue(all(place['category'] == 'nature' for place in places))

	def test_nearby_places_api_validates_coordinates(self):
		response = self.client.post('/api/places/nearby', data={
			'latitude': 'invalid',
			'longitude': 36.82,
			'budget': 3000,
			'available_time_minutes': 240,
			'category': '',
		}, content_type='application/json')

		self.assertEqual(response.status_code, 400)


class RecommendationTests(TestCase):
	def setUp(self):
		views.place_provider = LocalPlaceProvider()
		self.user = User.objects.create_user(username='planner', password='test-pass-123')
		UserPreference.objects.create(
			user=self.user,
			interests=['nature'],
			budget_preference=3000,
			available_time_minutes=240,
		)

	def test_interest_match_ranks_first(self):
		recommendations = rank_recommendations(
			LocalPlaceProvider().nearby(-1.27, 36.82),
			-1.27,
			36.82,
			['nature'],
			3000,
			240,
		)

		self.assertTrue(recommendations)
		self.assertEqual(recommendations[0]['category'], 'nature')
		self.assertIn('matches your interest', recommendations[0]['reason'])

	def test_recommendations_api_requires_login(self):
		response = self.client.post('/api/recommendations', data={}, content_type='application/json')

		self.assertEqual(response.status_code, 302)

	def test_recommendations_api_returns_scored_places(self):
		self.client.login(username='planner', password='test-pass-123')
		response = self.client.post('/api/recommendations', data={
			'location_name': 'Nairobi CBD',
			'budget': 3000,
			'available_time_minutes': 240,
			'category': '',
		}, content_type='application/json')

		self.assertEqual(response.status_code, 200)
		self.assertTrue(response.json()['recommendations'])
		self.assertIn('recommendation_score', response.json()['recommendations'][0])
