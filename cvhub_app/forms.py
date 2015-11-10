from django import forms
from cvhub_app.models import *


class UserInfoForm(forms.ModelForm):

    first_name = forms.CharField(label='First name', max_length=128)
    last_name = forms.CharField(label='Last name', max_length=128)
    email = forms.CharField(label='Email', max_length=128)
    password = forms.CharField(label='Password', max_length=128, widget=forms.PasswordInput)

    # validator method for email, enforcing uniqueness
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).count():
            raise forms.ValidationError('Email addresses must be unique.')
        return email

    # enforce password length more than 6 characters
    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) <= 6:
            raise forms.ValidationError('Password must be longer than 6 characters.')
        return password

    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'email', 'password', 'dob']


class EducationForm(forms.ModelForm):

    class Meta:
        model = Education
        fields = ['school', 'degree_type', 'start_date', 'end_date', 'gpa', 'location']

# Form to add bullet points to education
class BulletPointForm(forms.Form):

    bpText = forms.CharField(label='Text', max_length=1000)
    def __init__(self, user, *args, **kwargs):
        super(BulletPointForm, self).__init__(*args, **kwargs)
        self.fields['education_item_choices'] = forms.ChoiceField(choices=get_education_items(user))

# retrieve all education items for the given user
def get_education_items(user):
    user_info = user.user_info

    choices_list = []
    education_objects = Education.objects.filter(owner=user_info)

    # put education into choice list format, 
    # with pk as the key and school name as the string to display
    for x in education_objects:
        choices_list.append((x.pk, x.school))

    return choices_list



