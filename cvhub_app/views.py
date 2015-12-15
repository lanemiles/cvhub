from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from cvhub_app.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Max
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
import os
from django.conf import settings
from django.template import Context
from django.template.loader import get_template
import datetime
from xhtml2pdf import pisa
from django.db.models import Q
import collections
import random
import math
from django.core import serializers
import json


# USER/PROFILE RELATED VIEWS
def create_user(request):
    """
    CREATE_USER: This view is called when are creating or processing a new user sign up
    """

    # if a POST, process the form data
    if request.method == 'POST':

        print "POST"

        # create a form instance and populate it with data from the request:
        form = UserInfoForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            print "VALID"

            # make the User object
            user = User.objects.create_user(form.cleaned_data.get('email'),
                form.cleaned_data.get('email'), form.cleaned_data.get('password'))
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()

            print "MADE USER"

            # make the UserInfo object
            user_wrapper = UserInfo()
            user_wrapper.dob = form.cleaned_data.get('dob')
            user_wrapper.phone_number = form.cleaned_data.get('phone_number')
            user_wrapper.display_name = user.first_name + " " + user.last_name
            user_wrapper.website = form.cleaned_data.get('website')
            user_wrapper.user = user
            user_wrapper.save()

            print "SAVE"

            # redirect to the profile page:
            user = authenticate(username=request.POST.get('email'), password=request.POST.get('password'))
            if user is not None:
                print "NOT NONE"
                if user.is_active:
                    print "ACTIVE"
                    login(request, user)
            return redirect('/profile/')

    # if a GET, present the sign up form
    else:

        form = UserInfoForm()
        return render(request, 'create_user.html', {'form': form})


@login_required
def user_profile(request):
    """
    USER_PROFILE: This view is where users get to edit their resume content.
    """

    return render(request, 'profile.html', user_profile_dict(request.user))


@login_required
def logout_view(request):
    """
    LOGOUT_VIEW: This view simply logs out a user and redirects them to login
    """
    logout(request)
    # Redirect to a success page.
    return redirect('/login/')


@login_required
def view_my_resume(request):
    """
    VIEW_MY_RESUME: Displays the HTML version of all enabled resume items
    """

    return render(request, 'view-my-resume.html', user_profile_dict(request.user, only_enabled=True))


def view_user_resume(request, user_id):
    """
    VIEW_USER_RESUME: Displays HTML for resume as a helper function for PDF generation
    """

    # we pass in user and user info
    return render(request, 'resume_pdf_template.html', user_profile_dict(User.objects.get(id=user_id), only_enabled=True))


def user_profile_dict(user, only_enabled=False):
    """
    USER_PROFILE_DICT: View called whenever we want to render profile.html.
    Gets user's info, education, skills, experience, awards, and bullet points.
    """

    # get the user info
    user_info = user.user_info

    # get bullet points for user
    if only_enabled:

        bps = BulletPoint.objects.filter(resume_owner=user_info, enabled=True).order_by('order')
        user_bps = {}
        for bp in bps:
            if bp.resume_owner == user_info:
                if bp.get_parent() in user_bps:
                    user_bps[bp.get_parent()].append(bp)
                else:
                    user_bps[bp.get_parent()] = [bp]

    else:

        bps = BulletPoint.objects.filter(resume_owner=user_info).order_by('order')
        user_bps = {}
        for bp in bps:
            if bp.resume_owner == user_info:
                if bp.get_parent() in user_bps:
                    user_bps[bp.get_parent()].append(bp)
                else:
                    user_bps[bp.get_parent()] = [bp]

    if only_enabled:

        # create dictionary
        dictionary = {'user': user, \
                        'user_info': user_info, \
                        'education_list': Education.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'skill_category_list': Skill.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'experience_list': Experience.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'award_list': Award.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'bps': user_bps}

    else:

        # create dictionary
        dictionary = {'user': user, \
                        'user_info': user_info, \
                        'education_list': Education.objects.filter(owner=user_info).order_by('order'), \
                        'skill_category_list': Skill.objects.filter(owner=user_info).order_by('order'), \
                        'experience_list': Experience.objects.filter(owner=user_info).order_by('order'), \
                        'award_list': Award.objects.filter(owner=user_info).order_by('order'), \
                        'bps': user_bps}

    return dictionary


# INFORMATION RELATED VIEWS
@login_required
def edit_information(request):
    """
    EDIT_INFORMATION: A user can edit certain parts of their information
    """

   # if this is a POST request we need to process the form data
    if request.method == 'POST':

        form = EditInformationForm(request.POST)

        if form.is_valid():

            # update user_info object per new information from form
            user_info = request.user.user_info
            user_info.dob = form.cleaned_data.get('dob')
            user_info.display_name = form.cleaned_data.get('display_name')
            user_info.phone_number = form.cleaned_data.get('phone_number')
            user_info.website = form.cleaned_data.get('website')

            # set a unique public resume url
            proposed_resume_url = form.cleaned_data.get('resume_url')

            # if the url is already taken, ask the user for a new url
            name_taken = UserInfo.objects.exclude(id=request.user.user_info.id).filter(resume_url=proposed_resume_url).count()
            if name_taken > 0 or (proposed_resume_url == "None"):
                return render(request, 'edit_information.html', {'form': form, 'name_taken': True, 'url_is_none': False})

            # unique url requested, so finish updating information
            else:
                user_info.resume_url = proposed_resume_url
                user_info.save()

        return redirect('/profile/')

    # if a GET
    else:

        # return form to edit information
        form = EditInformationForm(instance=request.user.user_info)

        return render(request, 'edit_information.html', {'form': form, 'name_taken': False, 'url_is_none': False})


# EDUCATION RELATED VIEWS
@login_required
def create_education(request):
    """
    CREATE_EDUCATION: This view processes Education object data or presents the form to make one
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = EducationForm(request.POST)

        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required

            # get user info
            user_info = request.user.user_info

            # create education from form data
            education = Education(**form.cleaned_data)
            education.owner = user_info

            # set order to last item
            order_max = Education.objects.filter(owner=user_info).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                education.order = order_max + 1
            else:
                education.order = 1

            education.save()

            return redirect('/profile/')

        else:

            return render(request, 'add_education.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = EducationForm()
        return render(request, 'add_education.html', {'form': form})


@login_required
def remove_education(request, education_id=None):
    """
    REMOVE_EDUCATION: This view is called by the Edit Profile page and
    redirects to the profile page on completion
    """

    # get content types
    education_type = ContentType.objects.get_for_model(Education)
    bp_type = ContentType.objects.get_for_model(BulletPoint)

    # get associated bullet points
    bps = BulletPoint.objects.filter(content_type=education_type, object_id=education_id)

    # for every bp under this education
    for bp in bps:

        # get and delete its associated comments
        comments_to_delete = Comment.objects.filter(content_type=bp_type, object_id=bp.id)
        for ctd in comments_to_delete:
            ctd.delete()

        # delete the bp
        bp.delete()

    # delete comments on this education item
    comments_to_delete = Comment.objects.filter(content_type=education_type, id=education_id)
    for ctd in comments_to_delete:
        ctd.delete()

    # finally, delete the education item itself
    Education.objects.get(id=education_id).delete()

    return redirect('/profile/')


@login_required
def edit_education(request, education_id=None):
    """
    EDIT_EDUCATION: This view presents and processes the form data
    for editing an education item and its bullet points
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # get the user
        user_info = request.user.user_info

        # create a form instance and populate it with data from the request:
        form = EducationForm(request.POST)
        form2 = EducationForm(request.POST, instance=Education.objects.get(id=form.data.get('edu_id')))

        # check whether it's valid:
        if form2.is_valid():
            # process the data in form.cleaned_data as required

            form2.save()
            bp_dict = {}

            # pull out the BP stuff
            for thing in request.POST:

                if 'BP' in thing:
                    bp_dict[thing] = request.POST.get(thing)

            # save modified BulletPoints
            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

            return redirect('/profile/')

        else:

            # get associated bullet points
            bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
            education_bps = []
            for bp in bps:
                if bp.get_parent() == Education.objects.get(id=request.POST.get('edu_id')):
                    education_bps.append(bp)

            form = EducationBulletPointForm(education_bps, instance=Education.objects.get(id=request.POST.get('edu_id')))
            form.add_bp_fields(education_bps)

            return render(request, 'edit_education.html', {'form': form, 'edu_id': request.POST.get('edu_id'), 'errors': "There was an error in processing your form."})

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        education_bps = []
        for bp in bps:
            if bp.get_parent() == Education.objects.get(id=education_id):
                education_bps.append(bp)

        # display form
        form = EducationBulletPointForm(education_bps, instance=Education.objects.get(id=education_id))
        form.add_bp_fields(education_bps)

        return render(request, 'edit_education.html', {'form': form, 'edu_id': education_id})


@login_required
def move_up_education(request, education_id):

    return move_up_resume_item(request, 'education', education_id)


@login_required
def move_down_education(request, education_id):

    return move_down_resume_item(request, 'education', education_id)


@login_required
def add_education_bp(request, item_id=None):
    """
    ADD_EDUCATION_BP: This view presents and processes the data for a BP for an education item
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = BulletPointForm(request.user, request.POST)

        # check whether it's valid:
        if form.is_valid():

            bp = BulletPoint()

            # get user
            user_info = request.user.user_info

            # get text of bullet point from form
            bpText = form.cleaned_data.get('bpText')
            bp.text = bpText

            # enable/disable the bullet point
            bpEnabled = form.cleaned_data.get('bpEnabled')
            bp.enabled = bpEnabled

            # get education from the drop down list in form
            education = request.POST.get('edu_id')

            # return all bullet points for that education, and find the next number for an ordering
            order_max = BulletPoint.objects.filter(object_id=education).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                bp.order = order_max + 1
            else:
                bp.order = 1

            # set bullet point's foreign keys to a given education choice
            education_type = ContentType.objects.get_for_model(Education)
            bp.content_type = education_type
            bp.object_id = education

            # add bullet point to db
            bp.save()

            return redirect('/profile/')

        else:

            form.set_education(request.user, request.POST.get('edu_id'))
            return render(request, 'add_education_bp.html', {'form': form, 'edu_id': request.POST.get('edu_id')})

    # if a GET (or any other method) we'll create a blank form
    else:

        # create the form
        form = BulletPointForm(request.user)
        form.set_education(request.user, item_id)
        return render(request, 'add_education_bp.html', {'form': form, 'edu_id': item_id})


@login_required
def add_education_comment(request, education_id):

    return add_item_comment(request, 'education', education_id)


@login_required
def enable_education(request, education_id):

    return enable_item(request, 'education', education_id)


@login_required
def disable_education(request, education_id):

    return disable_item(request, 'education', education_id)


@login_required
def get_comments_for_education(request, education_id):

    return get_comments_for_item(request, 'education', education_id)


# EXPERIENCE RELATED VIEWS
@login_required
def create_experience(request):
    """
    CREATE_EXPERIENCE: Presents and processes form data for making an experience
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ExperienceForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            # get user
            user_info = request.user.user_info

            # create experience
            exp = Experience(**form.cleaned_data)
            exp.owner = user_info

            # set order to last item
            order_max = Experience.objects.filter(owner=user_info).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                exp.order = order_max + 1
            else:
                exp.order = 1

            exp.save()

            return redirect('/profile/')

        else:

            return render(request, 'add_experience.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = ExperienceForm()
        return render(request, 'add_experience.html', {'form': form})


@login_required
def edit_experience(request, experience_id=None):
    """
    EDIT_EXPERIENCE: This view presents and processes the form data
    for editing an experience and its associated skills
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # get the user info
        user_info = request.user.user_info

        # create a form instance and populate it with data from the request:
        form = ExperienceForm(request.POST)
        form2 = ExperienceForm(request.POST, instance=Experience.objects.get(id=form.data.get('experience_id')))

        # check whether it's valid:
        if form2.is_valid():

            # process the data in form.cleaned_data as required
            form2.save()
            bp_dict = {}

            # pull out the BP stuff
            for thing in request.POST:

                if 'BP' in thing:
                    bp_dict[thing] = request.POST.get(thing)

            # get associated bullet point changes
            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

            return redirect('/profile/')

        else:

            # get associated bullet points
            bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
            experience_bps = []
            for bp in bps:
                if bp.get_parent() == Experience.objects.get(id=request.POST.get('experience_id')):
                    experience_bps.append(bp)

            form.add_bp_fields(experience_bps)
            return render(request, 'edit_experience.html', {'form': form, 'experience_id': request.POST.get('experience_id')})

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        experience_bps = []
        for bp in bps:
            if bp.get_parent() == Experience.objects.get(id=experience_id):
                experience_bps.append(bp)

        # display the form
        form = ExperienceBulletPointForm(experience_bps, instance=Experience.objects.get(id=experience_id))
        form.add_bp_fields(experience_bps)

        return render(request, 'edit_experience.html', {'form': form, 'experience_id': experience_id})


@login_required
def remove_experience(request, experience_id=None):
    """
    REMOVE_EXPERIENCE: Called from Edit Resume, removes an experience
    and redirects
    """

    # get content types
    experience_type = ContentType.objects.get_for_model(Experience)
    bp_type = ContentType.objects.get_for_model(BulletPoint)

    # get associated bullet points
    bps = BulletPoint.objects.filter(content_type=experience_type, object_id=experience_id)

    # for every bp under this education
    for bp in bps:

        # get and delete its associated comments
        comments_to_delete = Comment.objects.filter(content_type=bp_type, object_id=bp.id)
        for ctd in comments_to_delete:
            ctd.delete()

        # delete the bp
        bp.delete()

    # delete comments on this education item
    comments_to_delete = Comment.objects.filter(content_type=experience_type, id=experience_id)
    for ctd in comments_to_delete:
        ctd.delete()

    # finally, delete the education item itself
    Experience.objects.get(id=experience_id).delete()

    return redirect('/profile/')


@login_required
def add_experience_bp(request, item_id=None):
    """
    ADD_EXPERIENCE_BP: Presents and processes form data for adding BP to experience
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = BulletPointForm(request.user, request.POST)

        # check whether it's valid:
        if form.is_valid():

            bp = BulletPoint()

            # get user
            user_info = request.user.user_info

            # get text of bullet point from form
            bpText = form.cleaned_data.get('bpText')
            bp.text = bpText

            # enable/disable the bullet point
            bpEnabled = form.cleaned_data.get('bpEnabled')
            bp.enabled = bpEnabled

            # get education from the drop down list in form
            experience = request.POST.get('experience_id')

            # return all bullet points for that education, and find the next number for an ordering
            order_max = BulletPoint.objects.filter(object_id=experience).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                bp.order = order_max + 1
            else:
                bp.order = 1

            # set bullet point's foreign keys to a given education choice
            experience_type = ContentType.objects.get_for_model(Experience)
            bp.content_type = experience_type
            bp.object_id = experience

            # add bullet point to db
            bp.save()

            return redirect('/profile/')

        else:

            form.set_experience(request.user, request.POST.get('experience_id'))
            return render(request, 'add_experience_bp.html', {'form': form, 'experience_id': request.POST.get('experience_id')})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_experience(request.user, item_id)
        return render(request, 'add_experience_bp.html', {'form': form, 'experience_id': item_id})


@login_required
def move_up_experience(request, experience_id):

    return move_up_resume_item(request, 'experience', experience_id)


@login_required
def move_down_experience(request, experience_id):

    return move_down_resume_item(request, 'experience', experience_id)


@login_required
def enable_experience(request, experience_id):

    return enable_item(request, 'experience', experience_id)


@login_required
def add_experience_comment(request, experience_id):

    return add_item_comment(request, 'experience', experience_id)


@login_required
def get_comments_for_experience(request, experience_id):

    return get_comments_for_item(request, 'experience', experience_id)


@login_required
def disable_experience(request, experience_id):

    return disable_item(request, 'experience', experience_id)


# SKILL RELATED VIEWS
@login_required
def create_skill_category(request):
    """
    CREATE_SKILL_CATEGORY: Presents and processes form data for making a skill category
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = SkillCategoryForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            # get user
            user_info = request.user.user_info

            # create experience
            skill_cat = Skill(**form.cleaned_data)
            skill_cat.owner = user_info

            # set order to last item
            order_max = Skill.objects.filter(owner=user_info).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                skill_cat.order = order_max + 1
            else:
                skill_cat.order = 1

            skill_cat.save()

            return redirect('/profile/')

        else:

            return render(request, 'add-skill-category.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = SkillCategoryForm()
        return render(request, 'add-skill-category.html', {'form': form})


@login_required
def edit_skill(request, skill_id=None):
    """
    EDIT_SKILL: This view presents and processes the form data
    for editing a skill category and its associated skills
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # get user info
        user_info = request.user.user_info

        # create a form instance and populate it with data from the request:
        form = SkillCategoryForm(request.POST)
        form2 = SkillCategoryForm(request.POST, instance=Skill.objects.get(id=form.data.get('skill_id')))

        # check whether it's valid:
        if form2.is_valid():

            # process the data in form.cleaned_data as required
            form2.save()
            bp_dict = {}

            # pull out the BP stuff
            for thing in request.POST:

                if 'BP' in thing:
                    bp_dict[thing] = request.POST.get(thing)

            # get associated skills
            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

            return redirect('/profile/')

        else:

            # get associated bullet points
            bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
            skill_bps = []
            for bp in bps:
                if bp.get_parent() == Skill.objects.get(id=request.POST.get('skill_id')):
                    skill_bps.append(bp)

            form.add_bp_fields(skill_bps)
            return render(request, 'edit_skill.html', {'form': form, 'skill_id': request.POST.get('skill_id')})

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        skill_bps = []
        for bp in bps:
            if bp.get_parent() == Skill.objects.get(id=skill_id):
                skill_bps.append(bp)

        # display form
        form = SkillBulletPointForm(skill_bps, instance=Skill.objects.get(id=skill_id))
        form.add_bp_fields(skill_bps)

        return render(request, 'edit_skill.html', {'form': form, 'skill_id': skill_id})


@login_required
def remove_skill(request, skill_id=None):
    """
    REMOVE_SKILL: This view is called from Edit Resume and removes
    a skill category and then redirects back
    """

    # get content types
    skill_type = ContentType.objects.get_for_model(Skill)
    bp_type = ContentType.objects.get_for_model(BulletPoint)

    # get associated bullet points
    bps = BulletPoint.objects.filter(content_type=skill_type, object_id=skill_id)

    # for every bp under this education
    for bp in bps:

        # get and delete its associated comments
        comments_to_delete = Comment.objects.filter(content_type=bp_type, object_id=bp.id)
        for ctd in comments_to_delete:
            ctd.delete()

        # delete the bp
        bp.delete()

    # delete comments on this education item
    comments_to_delete = Comment.objects.filter(content_type=skill_type, id=skill_id)
    for ctd in comments_to_delete:
        ctd.delete()

    # finally, delete the education item itself
    Skill.objects.get(id=skill_id).delete()

    return redirect('/profile/')


@login_required
def add_skill_bp(request, item_id=None):
    """
    ADD_SKILL_BP: Presents and processes form data for adding a skill
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = BulletPointForm(request.user, request.POST)

        # check whether it's valid:
        if form.is_valid():

            bp = BulletPoint()

            # get user
            user_info = request.user.user_info

            # get text of bullet point from form
            bpText = form.cleaned_data.get('bpText')
            bp.text = bpText

            # enable/disable the bullet point
            bpEnabled = form.cleaned_data.get('bpEnabled')
            bp.enabled = bpEnabled

            # get education from the drop down list in form
            skill = request.POST.get('skill_id')

            # return all bullet points for that education, and find the next number for an ordering
            order_max = BulletPoint.objects.filter(object_id=skill).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                bp.order = order_max + 1
            else:
                bp.order = 1

            # set bullet point's foreign keys to a given education choice
            skill_type = ContentType.objects.get_for_model(Skill)
            bp.content_type = skill_type
            bp.object_id = skill

            # add bullet point to db
            bp.save()

            return redirect('/profile/')

        else:

            form.set_skills(request.user, request.POST.get('skill_id'))
            return render(request, 'add_skill_bp.html', {'form': form, 'skill_id': request.POST.get('skill_id')})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_skills(request.user, item_id)
        return render(request, 'add_skill_bp.html', {'form': form, 'skill_id': item_id})


@login_required
def move_up_skill(request, skill_id):

    return move_up_resume_item(request, 'skill', skill_id)


@login_required
def move_down_skill(request, skill_id):

    return move_down_resume_item(request, 'skill', skill_id)


@login_required
def enable_skill(request, skill_id):

    return enable_item(request, 'skill', skill_id)


@login_required
def disable_skill(request, skill_id):

    return disable_item(request, 'skill', skill_id)


@login_required
def get_comments_for_skill(request, skill_id):

    return get_comments_for_item(request, 'skill', skill_id)


@login_required
def add_skill_comment(request, skill_id):

    return add_item_comment(request, 'skill', skill_id)


# AWARD RELATED VIEWS
@login_required
def create_award(request):
    """
    CREATE_AWARD: Presents and processes form data for making an award
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = AwardForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # process the data in form.cleaned_data as required
            # get user
            user_info = request.user.user_info

            # create experience
            award = Award(**form.cleaned_data)
            award.owner = user_info

            # set order to last item
            order_max = Award.objects.filter(owner=user_info).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                award.order = order_max + 1
            else:
                award.order = 1

            award.save()

            return redirect('/profile/')

        else:

            return render(request, 'add_award.html', {'form': form})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = AwardForm()
        return render(request, 'add_award.html', {'form': form})


@login_required
def edit_award(request, award_id=None):
    """
    EDIT_AWARD: This view presents and processes the form data
    for editing an award and its associated bullet points
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        user_info = request.user.user_info

        form = AwardForm(request.POST)
        form2 = AwardForm(request.POST, instance=Award.objects.get(id=form.data.get('award_id')))

        # check whether it's valid:
        if form2.is_valid():

            # process the data in form.cleaned_data as required
            form2.save()
            bp_dict = {}

            # pull out the BP stuff
            for thing in request.POST:

                if 'BP' in thing:
                    bp_dict[thing] = request.POST.get(thing)

            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

            return redirect('/profile/')

        else:

            # get associated bullet points
            bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
            award_bps = []
            for bp in bps:
                if bp.get_parent() == Award.objects.get(id=request.POST.get('award_id')):
                    award_bps.append(bp)

            form.add_bp_fields(award_bps)
            return render(request, 'edit_award.html', {'form': form, 'award_id': request.POST.get('award_id')})

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        award_bps = []
        for bp in bps:
            if bp.get_parent() == Award.objects.get(id=award_id):
                award_bps.append(bp)

        # display the form
        form = AwardBulletPointForm(award_bps, instance=Award.objects.get(id=award_id))
        form.add_bp_fields(award_bps)

        return render(request, 'edit_award.html', {'form': form, 'award_id': award_id})


@login_required
def remove_award(request, award_id=None):
    """
    REMOVE_AWARD: Removes an award, its associated data, and redirects back to profile
    """

    # get content types
    award_type = ContentType.objects.get_for_model(Award)
    bp_type = ContentType.objects.get_for_model(BulletPoint)

    # get associated bullet points
    bps = BulletPoint.objects.filter(content_type=award_type, object_id=award_id)

    # for every bp under this education
    for bp in bps:

        # get and delete its associated comments
        comments_to_delete = Comment.objects.filter(content_type=bp_type, object_id=bp.id)
        for ctd in comments_to_delete:
            ctd.delete()

        # delete the bp
        bp.delete()

    # delete comments on this education item
    comments_to_delete = Comment.objects.filter(content_type=award_type, id=award_id)
    for ctd in comments_to_delete:
        ctd.delete()

    # finally, delete the education item itself
    Award.objects.get(id=award_id).delete()

    return redirect('/profile/')


@login_required
def add_award_bp(request, item_id=None):
    """
    ADD_AWARD_BP: Presents and processes form data for adding BP to award
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = BulletPointForm(request.user, request.POST)

        # check whether it's valid:
        if form.is_valid():

            bp = BulletPoint()

            # get user
            user_info = request.user.user_info

            # get text of bullet point from form
            bpText = form.cleaned_data.get('bpText')
            bp.text = bpText

            # enable/disable the bullet point
            bpEnabled = form.cleaned_data.get('bpEnabled')
            bp.enabled = bpEnabled

            # get education from the drop down list in form
            award = request.POST.get('award_id')

            # return all bullet points for that education, and find the next number for an ordering
            order_max = BulletPoint.objects.filter(object_id=award).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                bp.order = order_max + 1
            else:
                bp.order = 1

            # set bullet point's foreign keys to a given education choice
            award_type = ContentType.objects.get_for_model(Award)
            bp.content_type = award_type
            bp.object_id = award

            # add bullet point to db
            bp.save()

            return redirect('/profile/')

        else:

            form.set_awards(request.user, request.POST.get('award_id'))
            return render(request, 'add_award_bp.html', {'form': form, 'award_id': request.POST.get('award_id')})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_awards(request.user, item_id)

        return render(request, 'add_award_bp.html', {'form': form, 'award_id': item_id})


@login_required
def move_up_award(request, award_id):

    return move_up_resume_item(request, 'award', award_id)


@login_required
def move_down_award(request, award_id):

    return move_down_resume_item(request, 'award', award_id)


@login_required
def enable_award(request, award_id):

    return enable_item(request, 'award', award_id)


@login_required
def disable_award(request, award_id):

    return disable_item(request, 'award', award_id)


@login_required
def get_comments_for_award(request, award_id):

    return get_comments_for_item(request, 'award', award_id)


@login_required
def add_award_comment(request, award_id):

    return add_item_comment(request, 'award', award_id)


# BULLET POINT RELATED VIEWS
@login_required
def remove_bp(request, bp_id):
    """
    REMOVE_BP: Delete an BP and redirect to profile
    """

    BulletPoint.objects.get(id=bp_id).delete()

    return redirect('/profile/')


@login_required
def move_up_bp(request, bp_id):
    """
    MOVE_UP_BP: Swaps the relative position for the BP in its parent item
    up by one position
    """

    # which BP are we moving
    move_bp = BulletPoint.objects.get(id=bp_id)
    parent = move_bp.get_parent()

    # get our siblings
    siblings = []

    for bp in BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order'):

        if bp.get_parent() == parent and bp != move_bp:

            siblings.append(bp)

    # if top
    if move_bp.order < min(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # if not, get our order
    move_bp_order = move_bp.order
    sorted(siblings, key=lambda x: x.order)

    # find the next smaller number and swap us
    curr_order = -1
    prev_bp = None
    for sib in siblings:
        if sib.order < move_bp_order:
            prev_bp = sib
            curr_order = sib.order
        else:
            break

    # actually swap
    prev_bp.order = prev_bp.order + (move_bp_order - curr_order)
    prev_bp.save()
    move_bp.order = move_bp.order - (move_bp_order - curr_order)
    move_bp.save()

    return redirect('/profile/')


@login_required
def move_down_bp(request, bp_id):
    """
    MOVE_DOWN_BP: Swaps the relative position for the BP in its parent item
    down by one position
    """

    # who are we
    move_bp = BulletPoint.objects.get(id=bp_id)
    parent = move_bp.get_parent()

    # who are our siblings
    siblings = []
    for bp in BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('-order'):

        if bp.get_parent() == parent and bp != move_bp:

            siblings.append(bp)

    # if bottom
    if move_bp.order > max(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next largest number
    move_bp_order = move_bp.order
    curr_order = -1
    next_bp = None
    for sib in siblings:
        if sib.order > move_bp_order:
            next_bp = sib
            curr_order = sib.order
        else:
            break

    # actually swap
    next_bp.order = next_bp.order + (move_bp_order - curr_order)
    next_bp.save()
    move_bp.order = move_bp.order - (move_bp_order - curr_order)
    move_bp.save()

    return redirect('/profile/')


@login_required
def enable_bp(request, bp_id):

    return enable_item(request, 'bullet point', bp_id)


@login_required
def disable_bp(request, bp_id):

    return disable_item(request, 'bullet point', bp_id)


@login_required
def add_bp_comment(request, bp_id):

    return add_item_comment(request, 'bullet point', bp_id)


@login_required
def get_comments_for_bp(request, bp_id=None):

    return get_comments_for_item(request, 'bullet point', bp_id)


# SECTION RELATED VIEWS
@login_required
def move_up_section(request, section_name):
    """
    MOVE_UP_SECTION: Moves a section up one in relative ordering
    """

    user_info = request.user.user_info

    if section_name == 'education':

        if user_info.education_order == 1:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Experience", user_info.experience_order), ("Skill", user_info.skill_order), ("Award", user_info.award_order)]:
                if value == user_info.education_order - 1:
                    if name == "Experience":
                        user_info.experience_order = user_info.experience_order + 1
                    elif name == "Skill":
                        user_info.skill_order = user_info.skill_order + 1
                    elif name == "Award":
                        user_info.award_order = user_info.award_order + 1
                    user_info.education_order = user_info.education_order - 1
                    break

    elif section_name == 'experience':

        if user_info.experience_order == 1:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Education", user_info.education_order), ("Skill", user_info.skill_order), ("Award", user_info.award_order)]:
                if value == user_info.experience_order - 1:
                    if name == "Education":
                        user_info.education_order = user_info.education_order + 1
                    elif name == "Skill":
                        user_info.skill_order = user_info.skill_order + 1
                    elif name == "Award":
                        user_info.award_order = user_info.award_order + 1
                    user_info.experience_order = user_info.experience_order - 1
                    break

    elif section_name == 'skill':

        if user_info.skill_order == 1:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Education", user_info.education_order), ("Experience", user_info.experience_order), ("Award", user_info.award_order)]:
                if value == user_info.skill_order - 1:
                    if name == "Education":
                        user_info.education_order = user_info.education_order + 1
                    elif name == "Experience":
                        user_info.experience_order = user_info.experience_order + 1
                    elif name == "Award":
                        user_info.award_order = user_info.award_order + 1
                    user_info.skill_order = user_info.skill_order - 1
                    break

    elif section_name == 'award':

        if user_info.award_order == 1:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Education", user_info.education_order), ("Experience", user_info.experience_order), ("Skill", user_info.skill_order)]:
                if value == user_info.award_order - 1:
                    if name == "Education":
                        user_info.education_order = user_info.education_order + 1
                    elif name == "Experience":
                        user_info.experience_order = user_info.experience_order + 1
                    elif name == "Skill":
                        user_info.skill_order = user_info.skill_order + 1
                    user_info.award_order = user_info.award_order - 1
                    break

    user_info.save()
    return redirect('/profile/')


@login_required
def move_down_section(request, section_name):
    """
    MOVE_DOWN_SECTION: Moves a section down one in the relative ordering
    """

    user_info = request.user.user_info

    if section_name == 'education':

        if user_info.education_order == 4:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Experience", user_info.experience_order), ("Skill", user_info.skill_order), ("Award", user_info.award_order)]:
                if value == user_info.education_order + 1:
                    if name == "Experience":
                        user_info.experience_order = user_info.experience_order - 1
                    elif name == "Skill":
                        user_info.skill_order = user_info.skill_order - 1
                    elif name == "Award":
                        user_info.award_order = user_info.award_order - 1
                    user_info.education_order = user_info.education_order + 1
                    break

    elif section_name == 'experience':

        if user_info.experience_order == 4:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Education", user_info.education_order), ("Skill", user_info.skill_order), ("Award", user_info.award_order)]:
                if value == user_info.experience_order + 1:
                    if name == "Education":
                        user_info.education_order = user_info.education_order - 1
                    elif name == "Skill":
                        user_info.skill_order = user_info.skill_order - 1
                    elif name == "Award":
                        user_info.award_order = user_info.award_order - 1
                    user_info.experience_order = user_info.experience_order + 1
                    break

    elif section_name == 'skill':

        if user_info.skill_order == 4:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Education", user_info.education_order), ("Experience", user_info.experience_order), ("Award", user_info.award_order)]:
                if value == user_info.skill_order + 1:
                    if name == "Education":
                        user_info.education_order = user_info.education_order - 1
                    elif name == "Experience":
                        user_info.experience_order = user_info.experience_order - 1
                    elif name == "Award":
                        user_info.award_order = user_info.award_order - 1
                    user_info.skill_order = user_info.skill_order + 1
                    break

    elif section_name == 'award':

        if user_info.award_order == 4:
            return redirect('/profile/')
        else:
            # find next smallest
            next_smallest = None
            for (name, value) in [("Education", user_info.education_order), ("Experience", user_info.experience_order), ("Skill", user_info.skill_order)]:
                if value == user_info.award_order + 1:
                    if name == "Education":
                        user_info.education_order = user_info.education_order - 1
                    elif name == "Experience":
                        user_info.experience_order = user_info.experience_order - 1
                    elif name == "Skill":
                        user_info.skill_order = user_info.skill_order - 1
                    user_info.award_order = user_info.award_order + 1
                    break

    user_info.save()
    return redirect('/profile/')


@login_required
def get_comments_for_section(request, section_name, user_info_id):
    """
    GET_COMMENTS_FOR_SECTION: Returns all comments for a given section
    """

    # get all the comments
    if section_name == 'EDUCATION':
        comments = SectionComment.objects.filter(section_type=SectionType.EDUCATION, section_owner=UserInfo.objects.get(id=user_info_id)).order_by('-vote_total')

    elif section_name == 'SKILLS':
        comments = SectionComment.objects.filter(section_type=SectionType.SKILLS, section_owner=UserInfo.objects.get(id=user_info_id)).order_by('-vote_total')

    elif section_name == 'AWARDS':
        comments = SectionComment.objects.filter(section_type=SectionType.AWARDS, section_owner=UserInfo.objects.get(id=user_info_id)).order_by('-vote_total')

    elif section_name == 'EXPERIENCE':
        comments = SectionComment.objects.filter(section_type=SectionType.EXPERIENCE, section_owner=UserInfo.objects.get(id=user_info_id)).order_by('-vote_total')

    elif section_name == 'CONTACT':
        comments = SectionComment.objects.filter(section_type=SectionType.CONTACT, section_owner=UserInfo.objects.get(id=user_info_id)).order_by('-vote_total')

    # make into a list of lists
    comment_list = [[comment.pk, comment.text, comment.vote_total, comment.status] for comment in comments]

    votes = []
    for comment in comments:
        # check if user has voted
        has_voted = SectionVote.objects.filter(user=request.user.user_info, comment=comment)
        if has_voted and has_voted[0].vote_type == VoteType.UP:
            votes.append(0)
        elif has_voted and has_voted[0].vote_type == VoteType.DOWN:
            votes.append(1)
        else:
            votes.append(2)

    # now, thats a list of comments
    # let's make it a list of dictionaries
    output = {}

    # get bp info
    output['bp_info'] = None

    # get comment info
    output['comments'] = zip(comment_list, votes)

    output = json.dumps(output)
    return HttpResponse(output, content_type='application/json')


@login_required
def add_section_comment(request, section_name, user_info_id):
    """
    ADD_SECTION_COMMENT: Comment on a given section
    """

    if request.method == 'POST':

        new_comment = SectionComment()

        # author of comment is poster
        new_comment.author = request.user.user_info

        # get the comment text
        new_comment.text = request.POST.get('comment_text')

        if request.POST.get('comment_text') == "":
            return redirect('/view-my-resume/')

        # add rep points to the commenter
        MADE_COMMENT_RP = 10
        author = UserInfo.objects.get(id=new_comment.author.id)
        author.points = author.points + MADE_COMMENT_RP

        # get the type
        if section_name == 'EDUCATION':
            section_type = SectionType.EDUCATION
        elif section_name == 'SKILLS':
            section_type = SectionType.SKILLS
        elif section_name == 'AWARDS':
            section_type = SectionType.AWARDS
        elif section_name == 'EXPERIENCE':
            section_type = SectionType.EXPERIENCE
        elif section_name == 'CONTACT':
            section_type = SectionType.CONTACT

        # set the type
        new_comment.section_type = section_type

        # set the owner
        new_comment.section_owner = UserInfo.objects.get(id=user_info_id)

        # increment pending
        if section_name == 'EDUCATION':
            owner = UserInfo.objects.get(id=user_info_id)
            owner.education_section_pending += 1
            owner.save()
        elif section_name == 'SKILLS':
            owner = UserInfo.objects.get(id=user_info_id)
            owner.skills_section_pending += 1
            owner.save()
        elif section_name == 'AWARDS':
            owner = UserInfo.objects.get(id=user_info_id)
            owner.awards_section_pending += 1
            owner.save()
        elif section_name == 'EXPERIENCE':
            owner = UserInfo.objects.get(id=user_info_id)
            owner.experience_section_pending += 1
            owner.save()
        elif section_name == 'CONTACT':
            owner = UserInfo.objects.get(id=user_info_id)
            owner.contact_info_pending += 1
            owner.save()

        author.save()
        new_comment.save()

        return redirect('/view-my-resume/')


@login_required
def accept_section_comment(request, section_comment_id):
    """
    ACCEPT_SECTION_COMMENT: A resume owner accepts a section comment
    """

    # retrieve the relevant comment
    comment = SectionComment.objects.get(id=section_comment_id)

    # rep points for commenter
    ACCEPTED_COMMENT_RP = 20
    rp = ACCEPTED_COMMENT_RP

    if comment.section_type == SectionType.EDUCATION:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.education_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.SKILLS:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.skills_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.AWARDS:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.awards_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.EXPERIENCE:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.experience_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.CONTACT:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.contact_info_pending -= 1
        owner.save()

    # award rp to commenter
    commenter = UserInfo.objects.get(id=comment.author.id)
    commenter.points = commenter.points + rp
    commenter.save()

    # update comment's status
    comment.status = CommentStatus.ACCEPTED
    comment.save()

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))


@login_required
def reject_section_comment(request, section_comment_id):
    """
    REJECT_SECTION_COMMENT: A resume owner rejects a section comment
    """

    # retrieve the relevant comment
    comment = SectionComment.objects.get(id=section_comment_id)
    comment.status = CommentStatus.DECLINE
    comment.save()

    # decrement pending
    if comment.section_type == SectionType.EDUCATION:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.education_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.SKILLS:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.skills_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.AWARDS:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.awards_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.EXPERIENCE:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.experience_section_pending -= 1
        owner.save()
    elif comment.section_type == SectionType.CONTACT:
        owner = UserInfo.objects.get(id=request.user.user_info.pk)
        owner.contact_info_pending -= 1
        owner.save()

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))


@login_required
def upvote_section_comment(request, section_comment_id):
    """
    UPVOTE_SECTION_COMMENT: Upvotes a section comment
    """

    # assuming they haven't voted before
    vote = SectionVote()
    vote.user = request.user.user_info
    vote.comment = SectionComment.objects.get(id=section_comment_id)
    vote.vote_type = VoteType.UP
    vote.save()

    # update total on comment
    comment = SectionComment.objects.get(id=section_comment_id)
    comment.vote_total = comment.vote_total + 1
    comment.save()

    # rep points for comment author
    UPVOTED_COMMENT_RP = 3
    comment_author = UserInfo.objects.get(id=comment.author.id)
    comment_author.points = comment_author.points + UPVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


@login_required
def downvote_section_comment(request, section_comment_id):
    """
    DOWNVOTE_SECTION_COMMENT: Downvotes a section comment
    """

    # assuming they haven't voted before
    vote = SectionVote()
    vote.user = request.user.user_info
    vote.comment = SectionComment.objects.get(id=section_comment_id)
    vote.vote_type = VoteType.DOWN
    vote.save()

    # update total on comment
    comment = SectionComment.objects.get(id=section_comment_id)
    comment.vote_total = comment.vote_total - 1
    comment.save()

    # negative rep points for comment author
    DOWNVOTED_COMMENT_RP = -1
    comment_author = UserInfo.objects.get(id=comment.author.id)
    comment_author.points = comment_author.points + DOWNVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


@login_required
def disable_section(request, section_name):
    """
    DISABLE_SECTION: When editing resume, disable all items of either
    Education, Skill, Experience, or Award
    """

    # disable all header-level education items
    if section_name == "education":
        items = Education.objects.filter(owner_id=request.user.user_info.id, enabled=True)
        for i in items:
            i.enabled = False
            i.save()

    # disable all header-level skill categories
    elif section_name == "skill":
        items = Skill.objects.filter(owner_id=request.user.user_info.id, enabled=True)
        for i in items:
            i.enabled = False
            i.save()

    # disable all header-level experience items
    elif section_name == "experience":
        items = Experience.objects.filter(owner_id=request.user.user_info.id, enabled=True)
        for i in items:
            i.enabled = False
            i.save()

    # disable all header-level award items
    elif section_name == "award":
        items = Award.objects.filter(owner_id=request.user.user_info.id, enabled=True)
        for i in items:
            i.enabled = False
            i.save()

    return redirect('/profile/')


@login_required
def enable_section(request, section_name):
    """
    ENABLE_SECTION: When editing resume, enable all items of either
    Education, Skill, Experience, or Award
    """

    # disable all header-level education items
    if section_name == "education":
        items = Education.objects.filter(owner_id=request.user.user_info.id, enabled=False)
        for i in items:
            i.enabled = True
            i.save()

    # disable all header-level skill categories
    elif section_name == "skill":
        items = Skill.objects.filter(owner_id=request.user.user_info.id, enabled=False)
        for i in items:
            i.enabled = True
            i.save()


    # disable all header-level experience items
    elif section_name == "experience":
        items = Experience.objects.filter(owner_id=request.user.user_info.id, enabled=False)
        for i in items:
            i.enabled = True
            i.save()

    # disable all header-level award items
    elif section_name == "award":        
        items = Award.objects.filter(owner_id=request.user.user_info.id, enabled=False)
        for i in items:
            i.enabled = True
            i.save()

    return redirect('/profile/')


# ITEM RELATED VIEWS
@login_required
def move_up_resume_item(request, item_type, item_id):
    """
    MOVE_UP_RESUME_ITEM: Moves up a resume item by one position
    """

    # get the item we want to move
    if item_type == 'education':
        item_to_move = Education.objects.get(id=item_id)
    elif item_type == 'skill':
        item_to_move = Skill.objects.get(id=item_id)
    elif item_type == 'award':
        item_to_move = Award.objects.get(id=item_id)
    elif item_type == 'experience':
        item_to_move = Experience.objects.get(id=item_id)

    # get the item owner
    item_owner = item_to_move.owner

    # find the siblings
    if item_type == 'education':
        siblings = Education.objects.filter(owner=item_owner).order_by('order').exclude(id=item_id)
    elif item_type == 'skill':
        siblings = Skill.objects.filter(owner=item_owner).order_by('order').exclude(id=item_id)
    elif item_type == 'award':
        siblings = Award.objects.filter(owner=item_owner).order_by('order').exclude(id=item_id)
    elif item_type == 'experience':
        siblings = Experience.objects.filter(owner=item_owner).order_by('order').exclude(id=item_id)

    # if we have no siblings, do nothing
    if len(siblings) == 0:
        return redirect('/profile/')

    # if already the top, do nothing
    if item_to_move.order < min(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    curr_order = -1
    prev_item = None
    for sib in siblings:
        if sib.order < item_to_move.order:
            prev_item = sib
            curr_order = sib.order
        else:
            break

    # swap the order
    prev_item.order = prev_item.order + (item_to_move.order - curr_order)
    prev_item.save()
    item_to_move.order = item_to_move.order - (item_to_move.order - curr_order)
    item_to_move.save()

    return redirect('/profile/')


@login_required
def move_down_resume_item(request, item_type, item_id):
    """
    MOVE_DOWN_RESUME_ITEM: Moves down a resume item by one position
    """

    # get the item we want to move
    if item_type == 'education':
        item_to_move = Education.objects.get(id=item_id)
    elif item_type == 'skill':
        item_to_move = Skill.objects.get(id=item_id)
    elif item_type == 'award':
        item_to_move = Award.objects.get(id=item_id)
    elif item_type == 'experience':
        item_to_move = Experience.objects.get(id=item_id)

    # get the item owner
    item_owner = item_to_move.owner

    # find the siblings
    if item_type == 'education':
        siblings = Education.objects.filter(owner=item_owner).order_by('-order').exclude(id=item_id)
    elif item_type == 'skill':
        siblings = Skill.objects.filter(owner=item_owner).order_by('-order').exclude(id=item_id)
    elif item_type == 'award':
        siblings = Award.objects.filter(owner=item_owner).order_by('-order').exclude(id=item_id)
    elif item_type == 'experience':
        siblings = Experience.objects.filter(owner=item_owner).order_by('-order').exclude(id=item_id)

    # if we have no siblings, do nothing
    if len(siblings) == 0:
        return redirect('/profile/')

    # if already the bottom, do nothing
    if item_to_move.order > max(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next largest number
    curr_order = -1
    prev_item = None
    for sib in siblings:
        if sib.order > item_to_move.order:
            prev_item = sib
            curr_order = sib.order
        else:
            break

    # swap the order
    prev_item.order = prev_item.order + (item_to_move.order - curr_order)
    prev_item.save()
    item_to_move.order = item_to_move.order - (item_to_move.order - curr_order)
    item_to_move.save()

    return redirect('/profile/')


@login_required
def enable_item(request, item_type, item_id):
    """
    ENABLE_ITEM: Enables a resume item or bullet point
    """

    if item_type == 'education':
        item = Education.objects.get(id=item_id)
    elif item_type == 'skill':
        item = Skill.objects.get(id=item_id)
    elif item_type == 'award':
        item = Award.objects.get(id=item_id)
    elif item_type == 'experience':
        item = Experience.objects.get(id=item_id)
    elif item_type == 'bullet point':
        item = BulletPoint.objects.get(id=item_id)

    item.enabled = True
    item.save()
    return redirect('/profile/')


@login_required
def disable_item(request, item_type, item_id):
    """
    DISABLE_ITEM: Enables a resume item or bullet point
    """

    if item_type == 'education':
        item = Education.objects.get(id=item_id)
    elif item_type == 'skill':
        item = Skill.objects.get(id=item_id)
    elif item_type == 'award':
        item = Award.objects.get(id=item_id)
    elif item_type == 'experience':
        item = Experience.objects.get(id=item_id)
    elif item_type == 'bullet point':
        item = BulletPoint.objects.get(id=item_id)

    item.enabled = False
    item.save()
    return redirect('/profile/')


@login_required
def add_item_comment(request, item_type, item_id):
    """
    ADD_ITEM_COMMENT: Comment on a commentable resume item
    """

    new_comment = Comment()

    # author of comment is poster
    new_comment.author = request.user.user_info

    # get the comment text
    new_comment.text = request.POST.get('comment_text')

    if request.POST.get('comment_text') == "":
        return redirect('/view-my-resume/')

    # is there a suggestion
    new_comment.suggestion = request.POST.get('suggestion_text')

    if request.POST.get('suggestion_text') != "":

        new_comment.is_suggestion = True

        # add rep points for a suggestion to the author
        MADE_SUGGESTION_RP = 15
        author = UserInfo.objects.get(id=new_comment.author.id)
        author.points = author.points + MADE_SUGGESTION_RP

    else:

        new_comment.is_suggestion = False

        # add rep points to the commenter
        MADE_COMMENT_RP = 10
        author = UserInfo.objects.get(id=new_comment.author.id)
        author.points = author.points + MADE_COMMENT_RP

    # increment pending
    if item_type == 'education':
        item = Education.objects.get(id=item_id)
        item.num_pending_comments += 1
        item.save()
    elif item_type == 'skill':
        item = Skill.objects.get(id=item_id)
        item.num_pending_comments += 1
        item.save()
    elif item_type == 'award':
        item = Award.objects.get(id=item_id)
        item.num_pending_comments += 1
        item.save()
    elif item_type == 'experience':
        item = Experience.objects.get(id=item_id)
        item.num_pending_comments += 1
        item.save()
    elif item_type == 'bullet point':
        item = BulletPoint.objects.get(id=item_id)
        item.num_pending_comments += 1
        item.save()

    # get content type
    if item_type == 'education':
        new_comment.content_type = ContentType.objects.get_for_model(Education)
    elif item_type == 'skill':
        new_comment.content_type = ContentType.objects.get_for_model(Skill)
    elif item_type == 'award':
        new_comment.content_type = ContentType.objects.get_for_model(Award)
    elif item_type == 'experience':
        new_comment.content_type = ContentType.objects.get_for_model(Experience)
    elif item_type == 'bullet point':
        new_comment.content_type = ContentType.objects.get_for_model(BulletPoint)

    new_comment.object_id = item_id
    new_comment.parent_item = GenericForeignKey('content_type', 'object_id')
    new_comment.save()

    author.save()

    return redirect('/view-my-resume/')


@login_required
def get_comments_for_item(request, item_type, item_id):
    """
    GET_COMMENTS_FOR_ITEM: Returns comments for a given resume item or bullet point
    """

    # get all the comments
    if item_type == 'education':
        comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Education), object_id=item_id).order_by('-vote_total')
    elif item_type == 'skill':
        comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Skill), object_id=item_id).order_by('-vote_total')
    elif item_type == 'award':
        comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Award), object_id=item_id).order_by('-vote_total')
    elif item_type == 'experience':
        comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Experience), object_id=item_id).order_by('-vote_total')
    elif item_type == 'bullet point':
        comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(BulletPoint), object_id=item_id).order_by('-vote_total')

    # make into a list of lists
    comment_list = [[comment.pk, comment.text, comment.vote_total, comment.is_suggestion, comment.suggestion, comment.status] for comment in comments]

    votes = []
    for comment in comments:
        # check if user has voted
        has_voted = Vote.objects.filter(user=request.user.user_info, comment=comment)
        if has_voted and has_voted[0].vote_type == VoteType.UP:
            votes.append(0)
        elif has_voted and has_voted[0].vote_type == VoteType.DOWN:
            votes.append(1)
        else:
            votes.append(2)

    # now, thats a list of comments
    # let's make it a list of dictionaries
    output = {}

    # get other info
    if item_type == 'education':
        output['education_info'] = Education.objects.get(id=item_id).school + ", " + Education.objects.get(id=item_id).location
    elif item_type == 'skill':
        output['skill_info'] = Skill.objects.get(id=item_id).category
    elif item_type == 'award':
        output['award_info'] = Award.objects.get(id=item_id).name + " from " + Award.objects.get(id=item_id).issuer
    elif item_type == 'experience':
        output['experience_info'] = Experience.objects.get(id=item_id).title + " at " + Experience.objects.get(id=item_id).employer
    elif item_type == 'bullet point':
        output['bp_info'] = BulletPoint.objects.get(id=item_id).text

    # get comment info
    output['comments'] = zip(comment_list, votes)

    output = json.dumps(output)
    return HttpResponse(output, content_type='application/json')


# SEARCH/EXPLORE RESUME RELATED VIEWS
@login_required
def choose_resume_to_edit(request):
    """
    CHOOSE_RESUME_TO_EDIT: Allows the resume reviewer to search all resumes by keyword.
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # Find the num_resumes_to_return resumes most relevant to keywords

        # Search terms; default is empty string
        keywords = request.POST.get('keywords')
        keywords = ("" if None else keywords)

        # Search terms; default is 5
        num_resumes_to_return = request.POST.get('num_resumes_to_return')
        num_resumes_to_return = (5 if None else num_resumes_to_return)
        my_id = request.user.user_info.id

        # a multiset of UserInfo ID's, with 1 occurrence for every time that user is hit in this search
        id_results = []

        # Search in name, phone number, website, and email, excluding my own resume
        id_results += queryset_to_valueslist("id", UserInfo.objects.exclude(id=my_id).filter( \
            Q(display_name__icontains=keywords) | Q(phone_number__icontains=keywords) | \
            Q(website__icontains=keywords)).values('id'))
        id_results += queryset_to_valueslist("user_info", User.objects.exclude(id=my_id)\
            .filter(Q(email__icontains=keywords)).values('user_info'))

        # Search in Education, Skill categories, Experience, and Awards, excluding my own resume
        id_results += queryset_to_valueslist("owner_id", Education.objects.exclude(owner=my_id).filter(Q(enabled=True), \
            Q(school__icontains=keywords) | Q(location__icontains=keywords)).values('owner_id'))
        id_results += queryset_to_valueslist("owner", Skill.objects.exclude(owner=my_id).filter(Q(enabled=True), \
            Q(category__icontains=keywords)).values('owner'))
        id_results += queryset_to_valueslist("owner", Experience.objects.exclude(owner=my_id).filter(Q(enabled=True), \
            Q(title__icontains=keywords) | Q(employer__icontains=keywords) | Q(location__icontains=keywords)).values('owner'))
        id_results += queryset_to_valueslist("owner", Award.objects.exclude(owner=my_id).filter(Q(enabled=True), \
            Q(name__icontains=keywords) | Q(issuer__icontains=keywords)).values('owner'))

        # Search in Bullet Points, excluding my own resume
        id_results += queryset_to_valueslist("resume_owner", BulletPoint.objects.exclude(resume_owner=my_id).filter(enabled=True, \
            text__icontains=keywords).values('resume_owner'))

        # Count and order by how many times the keyword appeared per user,
        c = collections.Counter(id_results).most_common()

        # turn list of tuples (immutable) --> list of lists
        c_1 = map(list, c)
        none_item_to_remove = False

        # adjust score for rep points
        for x in c_1:

            # avoid calling a query on a "None" 
            if x[0] is None:
                none_item = x
                none_item_to_remove = True
            else:
                points = UserInfo.objects.get(id=x[0]).points
                # no one ever loses points for low rep score
                points_bonus = (4 if (points <= 4) else math.log(points, 1.5))
                x[1] += points_bonus

        # remove Nones (resulting from queries with no hits), if there are any
        if none_item_to_remove:
            c_1.remove(none_item)

        # return a flat list of num_resumes_to_return users in new ranking order
        sorted_c = sorted(c_1,key=lambda x: x[1], reverse=True)[:(int)(num_resumes_to_return)]
        top_hits = [item[0] for item in sorted_c]

        # make the choice list of tuples (user id, user's display name)
        results_list = []
        for x in top_hits:
            top_hit_user = UserInfo.objects.values_list('display_name', flat=True).get(pk=x)
            results_list.append((x, top_hit_user))

        # if we have search results, redirect to results page
        if len(results_list) > 0:
            form = SearchResumeResultsForm()
            form.set_resumes_to_display(results_list)
            return render(request, 'search_resume_results.html', {'form': form})

        # if no search results returned, redirect to search page
        else:
            form = ChooseResumeToEditForm()
            return render(request, 'choose_resume_to_edit.html', {'form': form, 'no_results': True})

    # if a get request, we'll create a blank form
    else:

        form = ChooseResumeToEditForm()
        return render(request, 'choose_resume_to_edit.html', {'form': form, 'no_results': False})


@login_required
def most_recently_commented_resumes(request):
    """
    MOST_RECENTLY_COMMENTED_RESUMES: This view returns the 5 most recently commented on resumes
    """

    if request.method == 'POST':

        form = MostRecentlyCommentedResumesForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            # get selected resume/user
            userinfo_id = request.POST.get("Resumes")
            user_info = UserInfo.objects.get(id=userinfo_id)
            user_dictionary = user_profile_dict(user_info.user, True)
            user_dictionary.update({'header_user': request.user})

            # comment chosen resume
            return render(request, 'comment_resume.html', user_dictionary)

    # get method
    else:

        mrc_resumes_list = []

        # Use a try clause in case there are not 5 uniquely commented resumes
        # In successive queries, we exclude comments on resumes already in our list
        # of most recently commented resumes
        try:
            # resume 1
            c = Comment.objects.latest('timestamp')
            ui1 = UserInfo.objects.get(id=c.resume_owner_id)
            mrc_resumes_list.append((ui1.id, ui1.display_name))

            # resume 2
            c = Comment.objects.exclude(resume_owner_id=ui1.id).latest('timestamp')
            ui2 = UserInfo.objects.get(id=c.resume_owner_id)
            mrc_resumes_list.append((ui2.id, ui2.display_name))

            # resume 3
            c = Comment.objects.exclude(resume_owner_id=ui1.id).exclude(resume_owner_id=ui2.id).latest('timestamp')
            ui3 = UserInfo.objects.get(id=c.resume_owner_id)
            mrc_resumes_list.append((ui3.id, ui3.display_name))

            # resume 4
            c = Comment.objects.exclude(resume_owner_id=ui1.id).exclude(resume_owner_id=ui2.id) \
                .exclude(resume_owner_id=ui3.id).latest('timestamp')
            ui4 = UserInfo.objects.get(id=c.resume_owner_id)
            mrc_resumes_list.append((ui4.id, ui4.display_name))

            # resume 5
            c = Comment.objects.exclude(resume_owner_id=ui1.id).exclude(resume_owner_id=ui2.id) \
                .exclude(resume_owner_id=ui3.id).exclude(resume_owner_id=ui4.id).latest('timestamp')
            ui5 = UserInfo.objects.get(id=c.resume_owner_id)
            mrc_resumes_list.append((ui5.id, ui5.display_name))
       
        # if we don't have 5 uniquely commented resumes, just return the ones we do have
        except Comment.DoesNotExist:
            pass

        # create and populate form with choices of mrc resumes
        form = MostRecentlyCommentedResumesForm()
        form.set_mrc_resumes(mrc_resumes_list)

        return render(request, 'mrc_resumes.html', {'form': form})


@login_required
def most_popular_resumes(request):
    """
    MOST_POPULAR_RESUMES: Returns the NUM_RESUMES_TO_RETURN resumes with 
    the most comment activity in the last N_DAYS days
    """

    if request.method == 'POST':

        form = MostRecentlyCommentedResumesForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            # get selected resume/user
            userinfo_id = request.POST.get("Resumes")
            user_info = UserInfo.objects.get(id=userinfo_id)
            user_dictionary = user_profile_dict(user_info.user, True)
            user_dictionary.update({'header_user': request.user})

            # comment chosen resume
            return render(request, 'comment_resume.html', user_dictionary)

    # get most popular resumes
    else:

        N_DAYS = 3
        NUM_RESUMES_TO_RETURN = 5

        # look at comments on others' resumes in the last 3 days
        d = datetime.date.today() - datetime.timedelta(days=N_DAYS)
        comments = Comment.objects.exclude(resume_owner=request.user.user_info.id).filter(timestamp__gt=d)

        # count comments per resumes using a dict of format {'c.resume_owner': count of comments}
        comments_per_resume = {}
        for c in comments:
            if c.resume_owner not in comments_per_resume:
                comments_per_resume[c.resume_owner] = 1
            else:
                comments_per_resume[c.resume_owner] = comments_per_resume[c.resume_owner] + 1

        # return the NUM_RESUMES_TO_RETURN most commented resumes
        sorted_top_resumes = sorted(comments_per_resume, key=comments_per_resume.get, reverse=True)[:NUM_RESUMES_TO_RETURN]
        mp_resumes_list = []
        for x in sorted_top_resumes:
            mp_resumes_list.append((x.id, x.display_name))

        # create and populate form with choices of mrc resumes
        form = MostPopularResume()
        form.set_mp_resumes(mp_resumes_list)

        return render(request, 'most_popular_resumes.html', {'form': form})


@login_required
def random_resume(request):
    """
    RANDOM_RESUME: Randomly choose a user/resume to view, giving priority
    to users with more rep points. Priority depends on rep points compared to
    other users, not absolute rep points. The general idea is that higher
    ranked users will be more likely to remain in the pool of resumes to
    be randomly chosen from.
    """

    # size of table
    num_users = UserInfo.objects.count()

    if num_users < 6:
        upper_limit = num_users-1

    else:
        # randomly determine how many users to exclude
        # the top safe_users_percent % of users, or the top 5 users,
        # whichever is greater, will never be excluded
        safe_users_percent = .05
        s = num_users*safe_users_percent

        # if the number of users in the top safe_users_percent is less than 5,
        # set the top 5 users to be safe
        if s < 5:
            s = 5

        # can't choose 0 as the upper limit, or the second call to random will fail
        if s < 1:
            s = 1

        upper_limit = random.randint(int(s), num_users-1)

    # from remaining users, randomly choose a resume
    # resumes are ordered from highest points [0] to lowest points [upper_limit]
    # subtract 1 from upper limit because we exclude our own resume from the search
    user_index = random.randint(0, upper_limit-1)
    user_info = UserInfo.objects.order_by('-points').exclude(id=request.user.user_info.id)[user_index]

    user_dictionary = user_profile_dict(user_info.user, True)
    user_dictionary.update({'header_user': request.user})

    # comment randomly chosen resume
    return render(request, 'comment_resume.html', user_dictionary)


@login_required
def search_resume_results(request):
    """
    SEARCH_RESUME_RESULTS: Shows the results from a keyword search
    """

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = SearchResumeResultsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            if request.POST.get("choose_resume"):

                # get owner of resume selected in drop down box
                selected_resume = request.POST.get('results_list')

                # get UserInfo object about resume owner
                user_info = UserInfo.objects.get(id=selected_resume)

                user_dictionary = user_profile_dict(user_info.user, True)
                user_dictionary.update({'header_user': request.user})

                # redirect to the page to comment the chosen resume
                return render(request, 'comment_resume.html', user_dictionary)

            # go back to choose/search resume screen
            elif request.POST.get("back_to_choose_resume"):
                return redirect('/choose-resume-to-edit')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseResumeToEditForm()
        return render(request, 'choose_resume_to_edit.html', {'form': form})


@login_required
def comment_resume(request):
    """
    COMMENT_RESUME: The view for leaving comments and suggestions on a user's resume
    """

    return render(request, 'comment_resume.html', user_profile_dict(request.user, only_enabled=True))


# PDF RELATED VIEWS
@login_required
def generate_pdf(request):
    """
    GENERATE_PDF: Takes the current resume version and PDFs it
    and saves as a new version in ResumePDF
    """

    # create the resumePDF
    pdf = ResumePDF()

    # get user id
    user_id = str(request.user.pk)
    pdf.user = request.user.user_info

    # generate file id
    random_int = str(random.randint(00000001, 99999999))
    pdf.path = random_int

    # run the command on command line
    command = 'cd cvhub_app; cd static; cd cvhub_app;  xvfb-run --server-args="-screen 0, 1024x768x24" wkhtmltopdf http://40.83.184.46/view-user-resume/' + user_id + ' ' + random_int + '.pdf'

    # get last version number
    last_max = ResumePDF.objects.filter(user=request.user.user_info).aggregate(Max('version_number')).get('version_number__max')
    if last_max is not None:
        pdf.version_number = last_max + 1
    else:
        pdf.version_number = 1

    pdf.save()

    os.system(command)
    return redirect('/profile/')


@login_required
def embed_pdf(request):
    """
    EMBED_PDF: The view for viewing your resume version history
    """

    # get past PDFs
    pdfs = ResumePDF.objects.filter(user=request.user.user_info)

    # if no PDFs, don't fail
    if len(pdfs) == 0:
        first_path = ""

    else:
        first_path = pdfs[0].path

    return render(request, 'embed_pdf.html', {'first_path': first_path, 'url_list': pdfs})


@login_required
def view_pdf(request):
    """
    VIEW_PDF: View the current resume as a PDF, but don't save as a verision
    """

    # get user id
    user_id = str(request.user.pk)

    # generate file id
    random_int = str(random.randint(00000001, 99999999))

    # run the command
    command = 'cd cvhub_app; cd static; cd cvhub_app;  xvfb-run --server-args="-screen 0, 1024x768x24" wkhtmltopdf http://40.83.184.46/view-user-resume/' + user_id + ' ' + random_int + '.pdf'

    os.system(command)

    return redirect('/static/cvhub_app/'+str(random_int)+'.pdf')


def public_resume_pdf(request, custom_string):
    """
    PUBLIC_RESUME_PDF: Given a custom URL, redirect to a PDF
    of the user's resume
    """

    # this user hasn't set their custom public url yet, ask them to
    if custom_string == "None":
        form = EditInformationForm(instance=request.user.user_info)
        return render(request, 'edit_information.html', {'form': form, 'name_taken': False, 'url_is_none': True})

    else:

        # find associated user
        user = UserInfo.objects.get(resume_url=str(custom_string))

        # get their resume pdf
        user_id = str(user.user.pk)

        # generate file id
        random_int = str(random.randint(00000001, 99999999))

        command = 'cd cvhub_app; cd static; cd cvhub_app;  xvfb-run --server-args="-screen 0, 1024x768x24" wkhtmltopdf http://40.83.184.46/view-user-resume/' + user_id + ' ' + random_int + '.pdf'

        os.system(command)

        return redirect('/static/cvhub_app/'+str(random_int)+'.pdf')


# GENERAL COMMENT MANAGEMENT RELATED VIEWS
@login_required
def upvote_comment(request, comment_id):
    """
    UPVOTE_COMMENT: Upvotes a comment
    """

    # assuming they haven't voted before
    vote = Vote()
    vote.user = request.user.user_info
    vote.comment = Comment.objects.get(id=comment_id)
    vote.vote_type = VoteType.UP
    vote.save()

    # update total on comment
    comment = Comment.objects.get(id=comment_id)
    comment.vote_total = comment.vote_total + 1
    comment.save()

    # rep points for comment author
    UPVOTED_COMMENT_RP = 3
    comment_author = UserInfo.objects.get(id=comment.author.id)
    comment_author.points = comment_author.points + UPVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


@login_required
def downvote_comment(request, comment_id):
    """
    DOWNVOTE_COMMENT: Downvotes a comment
    """

    # assuming they haven't voted before
    vote = Vote()
    vote.user = request.user.user_info
    vote.comment = Comment.objects.get(id=comment_id)
    vote.vote_type = VoteType.DOWN
    vote.save()

    # update total on comment
    comment = Comment.objects.get(id=comment_id)
    comment.vote_total = comment.vote_total - 1
    comment.save()

    # negative rep points for comment author
    DOWNVOTED_COMMENT_RP = -1
    comment_author = UserInfo.objects.get(id=comment.author.id)
    comment_author.points = comment_author.points + DOWNVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


@login_required
def review_comments(request):
    """
    REVIEW_COMMENTS: Resume owner reviews comments on their resume
    """

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))


@login_required
def accept_comment(request, comment_id):
    """
    ACCEPT_COMMENT: Resume owner accepts a comment
    """

    # retrieve the relevant comment
    comment = Comment.objects.get(id=comment_id)
    # rep points for commenter
    ACCEPTED_COMMENT_RP = 20
    ACCEPTED_SUGGESTION_RP = 30
    rp = ACCEPTED_COMMENT_RP

    # decrement pending
    # need to decrement pending
    obj = comment.get_parent()
    obj.num_pending_comments -= 1
    obj.save()

    # if accepted suggestion, need to replace bp text
    # suggestions can only be made to bullet points
    if comment.is_suggestion:

        # replace bp text
        bp = BulletPoint.objects.get(id=comment.object_id)
        bp.text = comment.suggestion
        bp.save()

        # award more rp for comment + suggestion than just a comment
        rp = ACCEPTED_SUGGESTION_RP

        # reject all other pending suggestions on this bp
        reject_suggestions = queryset_to_valueslist('id',Comment.objects.filter(object_id=bp.id, \
            is_suggestion=True, status=CommentStatus.PENDING).exclude(id=comment_id).values('id'))
        for rs_id in reject_suggestions:
            rs = Comment.objects.get(id=rs_id)
            obj = rs.get_parent()
            obj.num_pending_comments -= 1
            obj.save()
            rs.status = CommentStatus.DECLINE
            rs.save()

    # award rp to commenter
    commenter = UserInfo.objects.get(id=comment.author.id)
    commenter.points = commenter.points + rp
    commenter.save()

    # update comment's status
    comment.status = CommentStatus.ACCEPTED
    comment.save()

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))


@login_required
def reject_comment(request, comment_id):
    """
    REJECT_COMMENT: Resume owner rejects a comment
    """

    # retrieve the relevant comment
    comment = Comment.objects.get(id=comment_id)
    comment.status = CommentStatus.DECLINE
    comment.save()

    # decrement pending
    obj = comment.get_parent()
    obj.num_pending_comments -= 1
    obj.save()

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))


# HELPER FUNCTIONS
def queryset_to_valueslist(key, query_set):
    """
    QUERYSET_TO_VALUESLIST: Turns a Query Set into a flat list of values for easier use
    """

    # for every key-value pair in the dictionary, get the value
    id_results = []
    for x in query_set:
        id_results.append(x[key])

    return id_results
