from django import forms
from .models import *


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['category', 'item_name', 'quantity', 'price', 'reorder_level']

    def clean_category(self):
        category = self.cleaned_data.get('category')
        if not category:
            raise forms.ValidationError('This field is required')

        # if stock.objects.filter(category=category).exists():
        #     raise forms.ValidationError(f"Category '{category.name}' is already created")
        
        return category

    def clean_item_name(self):
        item_name = self.cleaned_data.get('item_name')
        if not item_name:
            raise forms.ValidationError('This field is required')
        
        return item_name


class ItemFilterForm(forms.Form):
    export_to_CSV = forms.BooleanField(required=False)

    class Meta:
        model = stock
        fields = ['category', 'item_name', 'issue_by']

class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['category','item_name','quantity', 'price']

class IssueForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['category','item_name','issue_quantity', 'issue_to', 'price']


class RecieveForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['category','item_name','receive_from','received_quantity', 'price']

class ReorderLevelForm(forms.ModelForm):
    class Meta:
        model = stock
        fields = ['reorder_level']

class StockSearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    class Meta:
        model = stock
        fields = ['category', 'item_name']

class StockHistorySearchForm(forms.ModelForm):
    export_to_CSV = forms.BooleanField(required=False)
    class Meta:
        model = StockHistory
        fields = ['category','item_name']