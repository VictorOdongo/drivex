from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

import re


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=250)
    first_name = forms.CharField(max_length=150, validators=[RegexValidator(re.compile(r'^[a-zA-Z]+$'), 'Please enter a valid first name.')])
    last_name = forms.CharField(max_length=150, validators=[RegexValidator(re.compile(r'^[a-zA-Z]+$'), 'Please enter a valid last name.')])
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("The email already exists.")
        return email
    