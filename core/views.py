import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import DiscoveryForm, UserPreferenceForm
from .models import UserPreference
from .place_service import LocalPlaceProvider, discover_places

place_provider = LocalPlaceProvider()

def home(request):
    form = DiscoveryForm(request.POST or None)
    places = []
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        places = discover_places(
            place_provider,
            data['latitude'],
            data['longitude'],
            data['budget'],
            data['available_time_minutes'],
            data['category'],
        )
    return render(request, 'core/home.html', {'form': form, 'places': places})


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