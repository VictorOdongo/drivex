from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from .models import Customer

import re


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=250)
    first_name = forms.CharField(max_length=150, validators=[RegexValidator(re.compile(r'^[a-zA-Z]+$'), 'Please enter a valid first name.')])
    last_name = forms.CharField(max_length=150, validators=[RegexValidator(re.compile(r'^[a-zA-Z]+$'), 'Please enter a valid last name.')])
    phone_regex = re.compile(r'^[0-9]+$')  # Regular expression for numbers only
    phone = forms.CharField(max_length=25, validators=[RegexValidator(phone_regex, 'Please enter a valid phone number.')])


    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("The email already exists.")
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower()
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

        if commit:
            customer, created = Customer.objects.get_or_create(user=user)
            customer.email = user.email
            customer.first_name = user.first_name
            customer.last_name = user.last_name
            customer.phone = self.cleaned_data['phone']
            customer.save()

        return user