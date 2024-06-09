from django import forms
from .models import *

class StockCreateForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['category', 'item_name', 'quantity']

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('This Field is Required')

        for instance in stock.objects.all():
            if instance.category ==category:
                raise forms.ValidationError(category + ' is already created')
            return category
    
    def clean_item_name(self):
        item_name = self.cleaned_data.get('item_name')
        if not item_name:
            raise forms.ValidationError('This field is required')
            return item_name
            

class ItemFilterForm(forms.Form):
    export_to_CSV = forms.BooleanField(required=False)
    category = forms.CharField(required=False, label='Category')
    class Meta:
        model = stock
        fields = ['category','item_name']

class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['category','item_name','quantity']