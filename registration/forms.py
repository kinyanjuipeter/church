from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Phone Number'})
    )
    location = forms.CharField(
        max_length=100, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Your Location'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'location', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if User.objects.filter(username=phone_number).exists():
            raise ValidationError("This phone number is already registered")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['phone_number']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
        return user
