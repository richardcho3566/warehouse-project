from django import forms
from .models import Product
import re
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile

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

class CSVUploadForm(forms.Form):
    file = forms.FileField(label='CSV 파일 업로드')



class SignUpForm(UserCreationForm):
    username = forms.CharField(label='아이디')
    email = forms.EmailField(label='이메일')
    first_name = forms.CharField(label='이름')
    password1 = forms.CharField(label='비밀번호', widget=forms.PasswordInput)
    password2 = forms.CharField(label='비밀번호 확인', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'password1', 'password2']


class GradeUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['grade']
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-select'})
        }
