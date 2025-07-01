from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Challenge

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['weight', 'activity_level', 'age', 'weather_condition', 'custom_daily_goal', 'glass_volume', 'is_public_profile']
        widgets = {
            'weight': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your weight in kg',
                'min': '30',
                'max': '300',
                'step': '0.1'
            }),
            'activity_level': forms.Select(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter your age',
                'min': '1',
                'max': '120'
            }),
            'weather_condition': forms.Select(attrs={'class': 'form-control'}),
            'custom_daily_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional: Set custom daily goal in ml',
                'min': '500',
                'max': '5000'
            }),
            'glass_volume': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Default glass volume in ml',
                'min': '100',
                'max': '1000'
            }),
            'is_public_profile': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['custom_daily_goal'].required = False

class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ['name', 'description', 'challenge_type', 'start_date', 'end_date', 'goal_per_day', 'is_public']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Challenge name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Describe your challenge...'
            }),
            'challenge_type': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'goal_per_day': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Daily goal in ml',
                'min': '500',
                'max': '5000'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
