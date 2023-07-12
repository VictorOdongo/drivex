from core.models import Customer, Job
from django import forms
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.validators import RegexValidator

import re


class BasicUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class BasicCustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('avatar',)


class JobCreateStep1Form(forms.ModelForm):
    class Meta:
        model = Job
        fields = ('name', 'description', 'category',
                  'size', 'quantity', 'photo')


class JobCreateStep2Form(forms.ModelForm):
    pickup_address = forms.CharField(required=True)
    pickup_name = forms.CharField(required=True)
    phone_regex = re.compile(r'^[0-9]+$')  # Regular expression for numbers only
    pickup_phone = forms.CharField(required=True, max_length=25, validators=[RegexValidator(phone_regex, 'Please enter a valid phone number.')])

    class Meta:
        model = Job
        fields = ('pickup_address', 'pickup_lat',
                  'pickup_lng', 'pickup_name', 'pickup_phone')


class JobCreateStep3Form(forms.ModelForm):
    delivery_address = forms.CharField(required=True)
    delivery_name = forms.CharField(required=True)
    phone_regex = re.compile(r'^[0-9]+$')  # Regular expression for numbers only
    delivery_phone = forms.CharField(required=True, max_length=25, validators=[RegexValidator(phone_regex, 'Please enter a valid phone number.')])

    class Meta:
        model = Job
        fields = ('delivery_address', 'delivery_lat',
                  'delivery_lng', 'delivery_name', 'delivery_phone')
        

class PayPalEmailForm(forms.Form):
    paypal_email = forms.EmailField(label='PayPal Email')