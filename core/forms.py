from django import forms

from .models import UserPreference
from .place_service import resolve_location


INTEREST_CHOICES = [
    ('food', 'Food'),
    ('nature', 'Nature'),
    ('history', 'History'),
    ('culture', 'Culture'),
    ('adventure', 'Adventure'),
    ('nightlife', 'Nightlife'),
    ('shopping', 'Shopping'),
    ('relaxation', 'Relaxation'),
]

CATEGORY_CHOICES = [('', 'All categories')] + INTEREST_CHOICES


class DiscoveryForm(forms.Form):
    location_name = forms.CharField(max_length=120, required=False, initial='Current location', help_text='Type a place, such as Nairobi CBD, or enter coordinates below.')
    latitude = forms.FloatField(label='Latitude', required=False, help_text='Example: -1.27')
    longitude = forms.FloatField(label='Longitude', required=False, help_text='Example: 36.82')
    budget = forms.IntegerField(min_value=0, initial=3000)
    available_time_minutes = forms.IntegerField(min_value=1, initial=240)
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False)

    def clean(self):
        cleaned_data = super().clean()
        latitude = cleaned_data.get('latitude')
        longitude = cleaned_data.get('longitude')
        location_name = cleaned_data.get('location_name', '').strip()
        if latitude is None and longitude is None and location_name and location_name.lower() != 'current location':
            coordinates = resolve_location(location_name)
            if coordinates:
                cleaned_data['latitude'], cleaned_data['longitude'] = coordinates
            else:
                raise forms.ValidationError('We could not find that place. Try Nairobi CBD or enter latitude and longitude.')
        elif latitude is None or longitude is None:
            raise forms.ValidationError('Enter a place name or both latitude and longitude.')
        return cleaned_data


class UserPreferenceForm(forms.ModelForm):
    interests = forms.MultipleChoiceField(
        choices=INTEREST_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = UserPreference
        fields = [
            'interests',
            'budget_preference',
            'preferred_transport',
            'available_time_minutes',
            'travel_companions',
            'dietary_preferences',
            'mobility_preferences',
        ]
        widgets = {
            'budget_preference': forms.NumberInput(attrs={'min': 0}),
            'available_time_minutes': forms.NumberInput(attrs={'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.interests:
            self.initial['interests'] = self.instance.interests

    def save(self, commit=True):
        preference = super().save(commit=False)
        preference.interests = self.cleaned_data.get('interests', [])
        if commit:
            preference.save()
        return preference
