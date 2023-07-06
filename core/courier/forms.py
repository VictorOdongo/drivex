from typing import ClassVar
from django import forms
from core.models import Courier


class PayoutForm(forms.ModelForm):
    class Meta:
        model = Courier
        fields = ('paypal_email',)
