from django import forms
from cvhub_app.models import *


class UserInfoForm(forms.ModelForm):

    first_name = forms.CharField(label='First name', max_length=128)
    last_name = forms.CharField(label='Last name', max_length=128)
    email = forms.CharField(label='Email', max_length=128)
    password = forms.CharField(label='Password', max_length=128)
    forms.CharField(label='First name', max_length=128)

    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'email', 'password', 'dob']
