from django import forms
from cvhub_app.models import *


# FORMS TO ADD HEADER-LEVEL RESUME ITEMS
class UserInfoForm(forms.ModelForm):
    """
    Form for creating a new user
    """

    # name and contact information
    first_name = forms.CharField(label='First name', max_length=128)
    last_name = forms.CharField(label='Last name', max_length=128)
    website = forms.CharField(label='Website', max_length=500)
    phone_number = forms.CharField(label='Phone Number', max_length=500)
    email = forms.CharField(label='Email', max_length=500)

    # password
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

    # fields from UserInfo object to include
    class Meta:
        model = UserInfo
        fields = ['first_name', 'last_name', 'email', 'password', 'dob', 'website', 'phone_number']


class EducationForm(forms.ModelForm):
    """
    Form to create a new Education Resume Item
    """

    class Meta:
        model = Education
        fields = ['school', 'start_date', 'end_date', 'location', 'enabled']


class SkillCategoryForm(forms.ModelForm):
    """
    Add a header-level Skill Category Resume Item
    """

    class Meta:
        model = Skill
        fields = ['category', 'enabled']


class ExperienceForm(forms.ModelForm):
    """
    Add a header-level Experience Resume Item
    """

    def clean(self):
        current = self.cleaned_data.get('current')
        end_date = self.cleaned_data.get('end_date')
        if end_date is None and current is None:
            raise forms.ValidationError("You need to specify an end date or select current!")

    class Meta:
        model = Experience
        fields = ['title', 'employer', 'start_date', 'end_date', 'current', 'location', 'enabled']


class AwardForm(forms.ModelForm):
    """
    Add a header-level Award Resume Item
    """

    class Meta:
        model = Award
        fields = ['name', 'issuer', 'date_awarded', 'enabled']


# FORM TO ADD BULLET POINTS, & RELEVANT HELPER METHODS
class BulletPointForm(forms.Form):
    """
    Form to add bullet points
    """

    def __init__(self, user, *args, **kwargs):
        super(BulletPointForm, self).__init__(*args, **kwargs)

    def set_education(self, user, edu_id=None):
        self.fields['education_item_choices'] = forms.ChoiceField(choices=get_education_items(user, edu_id=edu_id))

    def set_skills(self, user, skill_id=None):
        self.fields['skill_item_choices'] = forms.ChoiceField(choices=get_skill_category_items(user, skill_id=skill_id))

    def set_experience(self, user, experience_id=None):
        self.fields['experience_item_choices'] = forms.ChoiceField(choices=get_experience_items(user, experience_id=experience_id))

    def set_awards(self, user, award_id=None):
        self.fields['award_item_choices'] = forms.ChoiceField(choices=get_award_items(user, award_id=award_id))

    bpText = forms.CharField(label='Text', max_length=1000)
    bpEnabled = forms.BooleanField(label='Enable this bullet point?', required=False)


def get_education_items(user, edu_id=None):
    """
    Retrieve all education items for the given user
    """

    # get Education objects
    choices_list = []
    if not edu_id:
        user_info = user.user_info
        education_objects = Education.objects.filter(owner=user_info)
    else:
        education_objects = Education.objects.filter(id=edu_id)

    # put education into choice list format, 
    # with pk as the key and school name as the string to display
    for x in education_objects:
        choices_list.append((x.pk, x.school))

    return choices_list


def get_skill_category_items(user, skill_id=None):
    """
    Retrieve all skill category items for the given user
    """

    # get Skill categories
    choices_list = []
    if not skill_id:
        user_info = user.user_info
        skill_objects = Skill.objects.filter(owner=user_info)
    else:
        skill_objects = Skill.objects.filter(id=skill_id)

    # put skills into choice list format,
    # with pk as the key and skill name as the string to display
    for x in skill_objects:
        choices_list.append((x.pk, x.category))

    return choices_list


def get_experience_items(user, experience_id=None):
    """
    Retrieve all experience items for the given user
    """

    # get experience items
    choices_list = []
    if not experience_id:
        user_info = user.user_info
        experience_objects = Experience.objects.filter(owner=user_info)
    else:
        experience_objects = Experience.objects.filter(id=experience_id)

    # put experience into choice list format,
    # with pk as the key and title + employer as the string to display
    for x in experience_objects:
        choices_list.append((x.pk, x.title + " at " + x.employer))

    return choices_list


def get_award_items(user, award_id=None):
    """
    Retrieve all award items for the given user
    """

    # get award items
    choices_list = []
    if not award_id:
        user_info = user.user_info
        award_objects = Award.objects.filter(owner=user_info)
    else:
        award_objects = Award.objects.filter(id=award_id)

    # put education into choice list format,
    # with pk as the key and award name + issuer as the string to display
    for x in award_objects:
        choices_list.append((x.pk, x.name + " from " + x.issuer))

    return choices_list


# FORMS TO EDIT EXISTING CONTENT
class EditInformationForm(forms.ModelForm):
    """
    Form to edit the user's contact and general information
    """

    class Meta:
        model = UserInfo
        fields = ['dob', 'display_name', 'phone_number', 'website', 'resume_url']


class EducationBulletPointForm(EducationForm):
    """
    Form to edit an Education resume item and associated bullet points
    """

    class Meta(EducationForm.Meta):
        fields = EducationForm.Meta.fields

    def __init__(self, user, *args, **kwargs):
        super(EducationBulletPointForm, self).__init__(*args, **kwargs)

    # create a prepopulated slot for each associated bullet point
    def add_bp_fields(self, bps):
        order = 1
        for bp in bps:
            self.fields["BP"+str(bp.pk)] = forms.CharField(widget=forms.Textarea, label=("Bullet Point: (#" + str(order)) + ")", initial=bp.text)
            order += 1


class SkillBulletPointForm(SkillCategoryForm):
    """
    Edit a Skill Category and its associated bullet points
    """

    class Meta(SkillCategoryForm.Meta):
        fields = SkillCategoryForm.Meta.fields

    def __init__(self, user, *args, **kwargs):
        super(SkillBulletPointForm, self).__init__(*args, **kwargs)

    # create a prepopulated slot for each associated bullet point
    def add_bp_fields(self, bps):
        print bps
        order = 1
        for bp in bps:
            self.fields["BP"+str(bp.pk)] = forms.CharField(widget=forms.Textarea, label=("Bullet Point: (#" + str(order)) + ")", initial=bp.text)
            order += 1


class ExperienceBulletPointForm(ExperienceForm):
    """
    Form to edit an Experience item and its associated bullet points
    """

    class Meta(ExperienceForm.Meta):
        fields = ExperienceForm.Meta.fields

    def __init__(self, user, *args, **kwargs):
        super(ExperienceBulletPointForm, self).__init__(*args, **kwargs)

    # create a prepopulated slot for each associated bullet point
    def add_bp_fields(self, bps):
        print bps
        order = 1
        for bp in bps:
            self.fields["BP"+str(bp.pk)] = forms.CharField(widget=forms.Textarea, label=("Bullet Point: (#" + str(order)) + ")", initial=bp.text)
            order += 1


class AwardBulletPointForm(AwardForm):
    """
    Form to edit an Award item and its associated bullet points
    """

    class Meta(AwardForm.Meta):
        fields = AwardForm.Meta.fields

    def __init__(self, user, *args, **kwargs):
        super(AwardBulletPointForm, self).__init__(*args, **kwargs)

    # create a prepopulated slot for each associated bullet point
    def add_bp_fields(self, bps):
        print bps
        order = 1
        for bp in bps:
            self.fields["BP"+str(bp.pk)] = forms.CharField(widget=forms.Textarea, label=("Bullet Point: (#" + str(order)) + ")", initial=bp.text)
            order += 1


# FORMS FOR RESUME REVIEWERS TO BROWSE RESUMES
class ChooseResumeToEditForm(forms.Form):
    """
    Form for resume reviewers to search by keyword for a resume to review
    """

    def __init__(self, *args, **kwargs):
        super(ChooseResumeToEditForm, self).__init__(*args, **kwargs)


class SearchResumeResultsForm(forms.Form):
    """
    Form to display resume search results in a dropdown box
    """

    def __init__(self, *args, **kwargs):
        super(SearchResumeResultsForm, self).__init__(*args, **kwargs)

    # populates dropdown box with results
    def set_resumes_to_display(self, resume_list):
        self.fields['results_list'] = forms.ChoiceField(choices=resume_list)


class MostRecentlyCommentedResumesForm(forms.Form):
    """
    Form to display most recently commented resumes in a dropdown box
    """

    def __init__(self, *args, **kwargs):
        super(MostRecentlyCommentedResumesForm, self).__init__(*args, **kwargs)

    # populate dropdown box with most recently commented resumes
    def set_mrc_resumes(self, mrc_resume_list):
        self.fields['Resumes'] = forms.ChoiceField(choices=mrc_resume_list)


class MostPopularResume(forms.Form):
    """
    Form to display most popular resumes in a dropdown box
    """

    def __init__(self, *args, **kwargs):
        super(MostPopularResume, self).__init__(*args, **kwargs)

    # populate dropdown box with top resumes
    def set_mp_resumes(self, mp_resume_list):
        self.fields['Resumes'] = forms.ChoiceField(choices=mp_resume_list)
