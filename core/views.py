import json
from urllib.parse import urlencode

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import DiscoveryForm, UserPreferenceForm
from .models import UserPreference
import os

from .place_service import GeminiPlaceProvider, LocalPlaceProvider, discover_places, geocode_ip_location, PlaceProvider
from .recommendation_service import rank_recommendations
from AI.ll_service import generate_general_summary

place_provider = GeminiPlaceProvider() if os.getenv('PLACES_PROVIDER') == 'gemini' else LocalPlaceProvider()

def home(request):
    form = DiscoveryForm(request.POST or None)
    places = []
    summary = None
    ai_status = None
    map_data = None
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        location_name = data.get('location_name', '').strip()

        if latitude is None or longitude is None:
            if location_name.lower() == 'current location':
                ip_lat, ip_lon = geocode_ip_location()
                if ip_lat is not None and ip_lon is not None:
                    latitude, longitude = ip_lat, ip_lon
                    data['latitude'], data['longitude'] = latitude, longitude
                else:
                    form.add_error(None, 'Could not determine your location. Please enter a place name or coordinates manually.')
                    return render(request, 'core/home.html', {
                        'form': form,
                        'places': places,
                        'summary': summary,
                        'ai_status': ai_status,
                        'map_data': map_data,
                    })
            else:
                form.add_error(None, 'Enter a place name, use "Use my location", or enter both latitude and longitude.')
                return render(request, 'core/home.html', {
                    'form': form,
                    'places': places,
                    'summary': summary,
                    'ai_status': ai_status,
                    'map_data': map_data,
                })

        preferences = getattr(request.user, 'preferences', None)
        places = rank_recommendations(
            place_provider.nearby(latitude, longitude),
            latitude,
            longitude,
            preferences.interests if preferences else [],
            data['budget'],
            data['available_time_minutes'],
            data['category'],
        )
        summary, ai_status = generate_general_summary(data, places)
        map_data = {
            'latitude': latitude,
            'longitude': longitude,
            'places': places,
            'iframe_url': 'https://www.openstreetmap.org/export/embed.html?' + urlencode({
                'bbox': ','.join([
                    str(longitude - 0.03),
                    str(latitude - 0.03),
                    str(longitude + 0.03),
                    str(latitude + 0.03),
                ]),
                'layer': 'mapnik',
                'marker': f"{latitude},{longitude}",
            }),
        }
    return render(request, 'core/home.html', {
        'form': form,
        'places': places,
        'summary': summary,
        'ai_status': ai_status,
        'map_data': map_data,
    })


def answer(request):
    return JsonResponse({'error': 'The AI assistant is not configured yet.'}, status=503)


@require_http_methods(['POST'])
def nearby_places_api(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Request body must be valid JSON.'}, status=400)

    form = DiscoveryForm(payload)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

    data = form.cleaned_data
    places = discover_places(
        place_provider,
        data['latitude'],
        data['longitude'],
        data['budget'],
        data['available_time_minutes'],
        data['category'],
    )
    return JsonResponse({'places': places})


@require_http_methods(['GET'])
def ip_geolocation_api(request):
    latitude, longitude = geocode_ip_location()
    if latitude is not None and longitude is not None:
        return JsonResponse({'latitude': latitude, 'longitude': longitude})
    return JsonResponse({'error': 'Could not determine location from IP'}, status=503)


@login_required
@require_http_methods(['POST'])
def recommendations_api(request):
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Request body must be valid JSON.'}, status=400)

    form = DiscoveryForm(payload)
    if not form.is_valid():
        return JsonResponse({'errors': form.errors.get_json_data()}, status=400)

    data = form.cleaned_data
    preferences, _ = UserPreference.objects.get_or_create(user=request.user)
    recommendations = rank_recommendations(
        place_provider.nearby(data['latitude'], data['longitude']),
        data['latitude'],
        data['longitude'],
        preferences.interests,
        data['budget'],
        data['available_time_minutes'],
        data['category'],
    )
    summary, ai_status = generate_general_summary(data, recommendations)
    return JsonResponse({'recommendations': recommendations, 'ai_summary': summary, 'ai_status': ai_status})


@login_required
def profile_preferences(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserPreferenceForm(request.POST, instance=preference)
        if form.is_valid():
            form.save()
            return redirect('core:profile-preferences')
    else:
        form = UserPreferenceForm(instance=preference)
    return render(request, 'core/preferences.html', {'form': form})


@login_required
@require_http_methods(['GET', 'PUT'])
def preferences_api(request):
    preference, _ = UserPreference.objects.get_or_create(user=request.user)
    if request.method == 'PUT':
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Request body must be valid JSON.'}, status=400)

        form = UserPreferenceForm(payload, instance=preference)
        if not form.is_valid():
            return JsonResponse({'errors': form.errors.get_json_data()}, status=400)
        form.save()

    return JsonResponse({
        'interests': preference.interests,
        'budget_preference': preference.budget_preference,
        'preferred_transport': preference.preferred_transport,
        'available_time_minutes': preference.available_time_minutes,
        'travel_companions': preference.travel_companions,
        'dietary_preferences': preference.dietary_preferences,
        'mobility_preferences': preference.mobility_preferences,
    })