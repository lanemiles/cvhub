from django import forms
from cvhub_app.models import *


class UserInfoForm(forms.ModelForm):

    first_name = forms.CharField(label='First name', max_length=128)
    last_name = forms.CharField(label='Last name', max_length=128)
    website = forms.CharField(label='Website', max_length=500)
    phone_number = forms.CharField(label='Phone Number', max_length=500)
    email = forms.CharField(label='Email', max_length=500)
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
        fields = ['first_name', 'last_name', 'email', 'password', 'dob', 'website', 'phone_number']


class EducationForm(forms.ModelForm):

    class Meta:
        model = Education
        fields = ['school', 'start_date', 'end_date', 'location', 'enabled']


class EducationBulletPointForm(EducationForm):

    class Meta(EducationForm.Meta):
        fields = EducationForm.Meta.fields

    def __init__(self, user, *args, **kwargs):
        super(EducationBulletPointForm, self).__init__(*args, **kwargs)

    def add_bp_fields(self, bps):
        print bps
        for bp in bps:
            self.fields["BP"+str(bp.pk)] = forms.CharField(label=("Bullet Point" + str(bp.order)), initial=bp.text)


# Form to add bullet points to education
class BulletPointForm(forms.Form):

    def __init__(self, user, *args, **kwargs):
        super(BulletPointForm, self).__init__(*args, **kwargs)

    def set_education(self, user, edu_id=None):
        self.fields['education_item_choices'] = forms.ChoiceField(choices=get_education_items(user, edu_id=edu_id))

    def set_skills(self, user, skill_id=None):
        self.fields['skill_item_choices'] = forms.ChoiceField(choices=get_skill_category_items(user, skill_id=skill_id))

    def set_experience(self, user, skill_id=None):
        self.fields['experience_item_choices'] = forms.ChoiceField(choices=get_experience_items(user, experience_id=skill_id))

    bpText = forms.CharField(label='Text', max_length=1000)
    bpEnabled = forms.BooleanField(label='Enable this bullet point?', required=False)


# retrieve all education items for the given user
def get_education_items(user, edu_id=None):
    user_info = user.user_info

    choices_list = []
    if not edu_id:
        education_objects = Education.objects.filter(owner=user_info)
    else:
        education_objects = Education.objects.filter(id=edu_id)

    # put education into choice list format, 
    # with pk as the key and school name as the string to display
    for x in education_objects:
        choices_list.append((x.pk, x.school))

    return choices_list


# retrieve all education items for the given user
def get_skill_category_items(user, skill_id=None):
    user_info = user.user_info

    choices_list = []
    if not skill_id:
        skill_objects = Skill.objects.filter(owner=user_info)
    else:
        skill_objects = Skill.objects.filter(id=skill_id)

    # put education into choice list format,
    # with pk as the key and school name as the string to display
    for x in skill_objects:
        choices_list.append((x.pk, x.category))

    return choices_list


# retrieve all education items for the given user
def get_experience_items(user, experience_id=None):
    user_info = user.user_info

    choices_list = []
    if not experience_id:
        experience_objects = Experience.objects.filter(owner=user_info)
    else:
        experience_objects = Experience.objects.filter(id=experience_id)

    # put education into choice list format,
    # with pk as the key and school name as the string to display
    for x in experience_objects:
        choices_list.append((x.pk, x.title + " at " + x.employer))

    return choices_list

# Form to choose a user's resume to edit
class ChooseResumeToEditForm(forms.Form):

    # TODO: add a button to choose a random resume

    # dynamically generate dropdown box of users
    def __init__(self, *args, **kwargs):
        super(ChooseResumeToEditForm, self).__init__(*args, **kwargs)
        self.fields['user_choice'] = forms.ChoiceField(choices=get_all_users())

# retrieve a list of all the users
def get_all_users():

    choices_list = []
    all_users = UserInfo.objects.all()

    # put users into choice list format, 
    # with pk as the key and username/email as display value
    for x in all_users:
        choices_list.append((x.pk, x.user.username))

    return choices_list

# add experience
class ExperienceForm(forms.ModelForm):

    class Meta:
        model = Experience
        fields = ['title', 'employer', 'start_date', 'end_date', 'current', 'location', 'enabled']

# add an award
class AwardForm(forms.ModelForm):

    class Meta:
        model = Award
        fields = ['name', 'issuer', 'date_awarded', 'enabled']

# add a skill category
class SkillCategoryForm(forms.ModelForm):

    class Meta:
        model = Skill
        fields = ['category', 'enabled']


class SkillBulletPointForm(SkillCategoryForm):

    class Meta(SkillCategoryForm.Meta):
        fields = SkillCategoryForm.Meta.fields

    def __init__(self, user, *args, **kwargs):
        super(SkillBulletPointForm, self).__init__(*args, **kwargs)

    def add_bp_fields(self, bps):
        print bps
        for bp in bps:
            self.fields["BP"+str(bp.pk)] = forms.CharField(label=("Bullet Point" + str(bp.order)), initial=bp.text)


class ExperienceBulletPointForm(ExperienceForm):

    class Meta(ExperienceForm.Meta):
        fields = ExperienceForm.Meta.fields

    def __init__(self, user, *args, **kwargs):
        super(ExperienceBulletPointForm, self).__init__(*args, **kwargs)

    def add_bp_fields(self, bps):
        print bps
        for bp in bps:
            self.fields["BP"+str(bp.pk)] = forms.CharField(label=("Bullet Point" + str(bp.order)), initial=bp.text)

