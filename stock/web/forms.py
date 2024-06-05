from django import forms
from .models import *

class StockCreateForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['category', 'item_name', 'quantity']