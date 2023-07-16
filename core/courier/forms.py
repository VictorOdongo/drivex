from typing import ClassVar
from django import forms
from core.models import Courier
from django.core.exceptions import ValidationError


class PayoutForm(forms.ModelForm):
    class Meta:
        model = Courier
        fields = ('phone_number',)
        
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise ValidationError("Phone number must only contain numbers.")
        return phone_number
