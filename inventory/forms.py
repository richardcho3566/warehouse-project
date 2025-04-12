from django import forms
from .models import Product
import re

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'warehouse', 'shelf_number', 'column', 'level']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': 'form-control'}),
            'warehouse': forms.TextInput(attrs={'class': 'form-control'}),
            'shelf_number': forms.TextInput(attrs={'class': 'form-control'}),
            'column': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.NumberInput(attrs={'class': 'form-control'}),
        }

    def clean_product_name(self):
        name = self.cleaned_data['product_name']
        if re.search(r'[a-z]', name):
            raise forms.ValidationError("소문자는 입력할 수 없습니다.")
        return name
