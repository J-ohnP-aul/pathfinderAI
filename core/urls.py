from django.urls import path

from .views import answer, home, nearby_places_api, preferences_api, profile_preferences

app_name = 'core'

urlpatterns = [
  path('', home, name='home'),
  path('answer/', answer, name='answer'),
  path('api/places/nearby', nearby_places_api, name='nearby-places-api'),
  path('profile/preferences/', profile_preferences, name='profile-preferences'),
  path('api/profile/preferences', preferences_api, name='preferences-api'),
]