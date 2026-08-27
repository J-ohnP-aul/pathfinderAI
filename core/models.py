from django.db import models
from django.contrib.auth.models import User


class UserPreference(models.Model):
	TRANSPORT_CHOICES = [
		('walking', 'Walking'),
		('public_transport', 'Public transport'),
		('driving', 'Driving'),
		('cycling', 'Cycling'),
	]
	COMPANION_CHOICES = [
		('solo', 'Solo'),
		('partner', 'Partner'),
		('friends', 'Friends'),
		('family', 'Family'),
	]

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
	interests = models.JSONField(default=list, blank=True)
	budget_preference = models.PositiveIntegerField(default=0)
	preferred_transport = models.CharField(max_length=30, choices=TRANSPORT_CHOICES, default='walking')
	available_time_minutes = models.PositiveIntegerField(default=120)
	travel_companions = models.CharField(max_length=20, choices=COMPANION_CHOICES, default='solo')
	dietary_preferences = models.CharField(max_length=120, blank=True)
	mobility_preferences = models.CharField(max_length=120, blank=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f'{self.user.username} preferences'
