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


def index(request):
    return render(request, 'current_time.html', {'question': 'his'})


def create_user(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UserInfoForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required

            # make the User object
            user = User.objects.create_user(form.cleaned_data.get('email'), \
            form.cleaned_data.get('email'), form.cleaned_data.get('password'))
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.save()

            # make the UserInfo object
            user_wrapper = UserInfo()
            user_wrapper.dob = form.cleaned_data.get('dob')
            user_wrapper.phone_number = form.cleaned_data.get('phone_number')
            user_wrapper.display_name = user.first_name + " " + user.last_name
            user_wrapper.website = form.cleaned_data.get('website')
            user_wrapper.user = user
            user_wrapper.save()

            # redirect to the profile page:
            user = authenticate(username=user.email, password=form.cleaned_data.get('password'))
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('/profile/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserInfoForm()

    return render(request, 'create_user.html', {'form': form})


def thanks(request):
    return render(request, 'thanks.html', {})


@login_required
def user_profile(request):

    return render(request, 'profile.html', user_profile_dict(request.user))


def logout_view(request):
    logout(request)
    # Redirect to a success page.
    return render(request, 'logout_success.html', {})


@login_required
def create_education(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = EducationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required

            # get user
            user_info = request.user.user_info

            # create education
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

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EducationForm()

    return render(request, 'add_education.html', {'form': form})


@login_required
def remove_education(request, education_id=None):

    bps = BulletPoint.objects.all()
    user_bps = {}
    for bp in bps:
        if bp.get_parent() == Education.objects.get(id=education_id):
            bp.delete()

    Education.objects.get(id=education_id).delete()

    return redirect('/profile/')


@login_required
def edit_education(request, education_id=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        user_info = request.user.user_info

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

            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

        return redirect('/profile/')

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        education_bps = []
        for bp in bps:
            if bp.get_parent() == Education.objects.get(id=education_id):
                education_bps.append(bp)

        form = EducationBulletPointForm(education_bps, instance=Education.objects.get(id=education_id))
        form.add_bp_fields(education_bps)

    return render(request, 'edit_education.html', {'form': form, 'edu_id': education_id})


@login_required
def edit_skill(request, skill_id=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        user_info = request.user.user_info

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

            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

        return redirect('/profile/')

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        skill_bps = []
        for bp in bps:
            if bp.get_parent() == Skill.objects.get(id=skill_id):
                skill_bps.append(bp)

        form = SkillBulletPointForm(skill_bps, instance=Skill.objects.get(id=skill_id))
        form.add_bp_fields(skill_bps)

    return render(request, 'edit_skill.html', {'form': form, 'skill_id': skill_id})


@login_required
def remove_skill(request, skill_id=None):

    bps = BulletPoint.objects.all()
    user_bps = {}
    for bp in bps:
        if bp.get_parent() == Skill.objects.get(id=skill_id):
            bp.delete()

    Skill.objects.get(id=skill_id).delete()

    return redirect('/profile/')



@login_required
def edit_experience(request, experience_id=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        user_info = request.user.user_info

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
                    print request.POST.get(thing)

            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

        return redirect('/profile/')

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        experience_bps = []
        for bp in bps:
            if bp.get_parent() == Experience.objects.get(id=experience_id):
                experience_bps.append(bp)

        form = ExperienceBulletPointForm(experience_bps, instance=Experience.objects.get(id=experience_id))
        form.add_bp_fields(experience_bps)

    return render(request, 'edit_experience.html', {'form': form, 'experience_id': experience_id})


@login_required
def remove_experience(request, experience_id=None):

    bps = BulletPoint.objects.all()
    user_bps = {}
    for bp in bps:
        if bp.get_parent() == Experience.objects.get(id=experience_id):
            bp.delete()

    Experience.objects.get(id=experience_id).delete()

    return redirect('/profile/')

@login_required
def add_education_bp(request, item_id=None):
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
            print request.POST

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

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_education(request.user, item_id)

        return render(request, 'add_education_bp.html', {'form': form, 'edu_id': item_id})

@login_required
def edit_award(request, award_id=None):
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
                    print request.POST.get(thing)

            for (id_str, text) in bp_dict.items():
                bp_id = id_str[2:]
                bp = BulletPoint.objects.get(id=int(bp_id))
                bp.text = text
                bp.save()

        return redirect('/profile/')

    # if a GET (or any other method) we'll create a blank form
    else:

        # get associated bullet points
        bps = BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order')
        award_bps = []
        for bp in bps:
            if bp.get_parent() == Award.objects.get(id=award_id):
                award_bps.append(bp)

        form = AwardBulletPointForm(award_bps, instance=Award.objects.get(id=award_id))
        form.add_bp_fields(award_bps)

    return render(request, 'edit_award.html', {'form': form, 'award_id': award_id})


@login_required
def remove_award(request, award_id=None):

    bps = BulletPoint.objects.all()
    user_bps = {}
    for bp in bps:
        if bp.get_parent() == Award.objects.get(id=award_id):
            bp.delete()

    Award.objects.get(id=award_id).delete()

    return redirect('/profile/')

@login_required
def add_skill_bp(request, item_id=None):
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
            print request.POST

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

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_skills(request.user, item_id)

        return render(request, 'add_skill_bp.html', {'form': form, 'skill_id': item_id})


@login_required
def add_experience_bp(request, item_id=None):
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
            print request.POST

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

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_experience(request.user, item_id)

        return render(request, 'add_experience_bp.html', {'form': form, 'experience_id': item_id})


@login_required
def add_award_bp(request, item_id=None):
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
            print request.POST

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

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_awards(request.user, item_id)

        return render(request, 'add_award_bp.html', {'form': form, 'award_id': item_id})


@login_required
def remove_bp(request, bp_id):

    BulletPoint.objects.get(id=bp_id).delete()

    return redirect('/profile/')


@login_required
def move_up_bp(request, bp_id):

    move_bp = BulletPoint.objects.get(id=bp_id)
    parent = move_bp.get_parent()

    siblings = []

    for bp in BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('order'):

        if bp.get_parent() == parent and bp != move_bp:

            siblings.append(bp)

    print siblings

    # if top
    if move_bp.order < min(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_bp_order = move_bp.order

    sorted(siblings, key=lambda x: x.order)
    for sib in siblings:
        print sib.order

    curr_order = -1
    prev_bp = None
    for sib in siblings:
        print "COMPARING", sib.order, move_bp_order
        if sib.order < move_bp_order:
            print sib.order, sib.text
            prev_bp = sib
            curr_order = sib.order
        else:
            break

    prev_bp.order = prev_bp.order + (move_bp_order - curr_order)
    prev_bp.save()
    move_bp.order = move_bp.order - (move_bp_order - curr_order)
    move_bp.save()

    return redirect('/profile/')


@login_required
def move_down_bp(request, bp_id):

    move_bp = BulletPoint.objects.get(id=bp_id)
    parent = move_bp.get_parent()

    siblings = []

    for bp in BulletPoint.objects.filter(resume_owner=request.user.user_info).order_by('-order'):

        if bp.get_parent() == parent and bp != move_bp:

            siblings.append(bp)

    print siblings

    # if bottom
    if move_bp.order > max(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next largest number
    move_bp_order = move_bp.order
    for sib in siblings:
        print sib.order

    curr_order = -1
    next_bp = None
    for sib in siblings:
        if sib.order > move_bp_order:
            print sib.order, sib.text
            next_bp = sib
            curr_order = sib.order
        else:
            break

    next_bp.order = next_bp.order + (move_bp_order - curr_order)
    next_bp.save()
    move_bp.order = move_bp.order - (move_bp_order - curr_order)
    move_bp.save()

    return redirect('/profile/')


@login_required
def move_up_education(request, education_id):

    move_education = Education.objects.get(id=education_id)
    our_owner = move_education.owner

    siblings = Education.objects.filter(owner=our_owner).order_by('order').exclude(id=education_id)

    # if top
    if move_education.order < min(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_education_order = move_education.order

    curr_order = -1
    prev_education = None
    for sib in siblings:
        if sib.order < move_education_order:
            prev_education = sib
            curr_order = sib.order
        else:
            break

    prev_education.order = prev_education.order + (move_education_order - curr_order)
    prev_education.save()
    move_education.order = move_education.order - (move_education_order - curr_order)
    move_education.save()

    return redirect('/profile/')


@login_required
def move_down_education(request, education_id):

    move_education = Education.objects.get(id=education_id)
    our_owner = move_education.owner

    siblings = Education.objects.filter(owner=our_owner).order_by('-order').exclude(id=education_id)

    # if top
    if move_education.order > max(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_education_order = move_education.order

    curr_order = -1
    prev_education = None
    for sib in siblings:
        if sib.order > move_education_order:
            prev_education = sib
            curr_order = sib.order
        else:
            break

    prev_education.order = prev_education.order + (move_education_order - curr_order)
    prev_education.save()
    move_education.order = move_education.order - (move_education_order - curr_order)
    move_education.save()

    return redirect('/profile/')


@login_required
def move_up_award(request, award_id):

    move_award = Award.objects.get(id=award_id)
    our_owner = move_award.owner

    siblings = Award.objects.filter(owner=our_owner).order_by('order').exclude(id=award_id)

    # if top
    if move_award.order < min(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_award_order = move_award.order

    curr_order = -1
    prev_award = None
    for sib in siblings:
        if sib.order < move_award_order:
            prev_award = sib
            curr_order = sib.order
        else:
            break

    prev_award.order = prev_award.order + (move_award_order - curr_order)
    prev_award.save()
    move_award.order = move_award.order - (move_award_order - curr_order)
    move_award.save()

    return redirect('/profile/')


@login_required
def move_down_award(request, award_id):

    move_award = Award.objects.get(id=award_id)
    our_owner = move_award.owner

    siblings = Award.objects.filter(owner=our_owner).order_by('-order').exclude(id=award_id)

    # if top
    if move_award.order > max(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_award_order = move_award.order

    curr_order = -1
    prev_award = None
    for sib in siblings:
        if sib.order > move_award_order:
            prev_award = sib
            curr_order = sib.order
        else:
            break

    prev_award.order = prev_award.order + (move_award_order - curr_order)
    prev_award.save()
    move_award.order = move_award.order - (move_award_order - curr_order)
    move_award.save()

    return redirect('/profile/')


@login_required
def move_up_skill(request, object_id):

    move_object = Skill.objects.get(id=object_id)
    our_owner = move_object.owner

    siblings = Skill.objects.filter(owner=our_owner).order_by('order').exclude(id=object_id)

    # if top
    if move_object.order < min(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_object_order = move_object.order

    curr_order = -1
    prev_object = None
    for sib in siblings:
        if sib.order < move_object_order:
            prev_object = sib
            curr_order = sib.order
        else:
            break

    prev_object.order = prev_object.order + (move_object_order - curr_order)
    prev_object.save()
    move_object.order = move_object.order - (move_object_order - curr_order)
    move_object.save()

    return redirect('/profile/')


@login_required
def move_down_skill(request, object_id):

    move_object = Skill.objects.get(id=object_id)
    our_owner = move_object.owner

    siblings = Skill.objects.filter(owner=our_owner).order_by('-order').exclude(id=object_id)

    # if top
    if move_object.order > max(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_object_order = move_object.order

    curr_order = -1
    prev_object = None
    for sib in siblings:
        if sib.order > move_object_order:
            prev_object = sib
            curr_order = sib.order
        else:
            break

    prev_object.order = prev_object.order + (move_object_order - curr_order)
    prev_object.save()
    move_object.order = move_object.order - (move_object_order - curr_order)
    move_object.save()

    return redirect('/profile/')


@login_required
def move_up_experience(request, object_id):

    move_object = Experience.objects.get(id=object_id)
    our_owner = move_object.owner

    siblings = Experience.objects.filter(owner=our_owner).order_by('order').exclude(id=object_id)

    # if top
    if move_object.order < min(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_object_order = move_object.order

    curr_order = -1
    prev_object = None
    for sib in siblings:
        if sib.order < move_object_order:
            prev_object = sib
            curr_order = sib.order
        else:
            break

    prev_object.order = prev_object.order + (move_object_order - curr_order)
    prev_object.save()
    move_object.order = move_object.order - (move_object_order - curr_order)
    move_object.save()

    return redirect('/profile/')


@login_required
def move_down_experience(request, object_id):

    move_object = Experience.objects.get(id=object_id)
    our_owner = move_object.owner

    siblings = Experience.objects.filter(owner=our_owner).order_by('-order').exclude(id=object_id)

    # if top
    if move_object.order > max(siblings, key=lambda x: x.order).order:
        return redirect('/profile/')

    # find next smallest number
    move_object_order = move_object.order

    curr_order = -1
    prev_object = None
    for sib in siblings:
        if sib.order > move_object_order:
            prev_object = sib
            curr_order = sib.order
        else:
            break

    prev_object.order = prev_object.order + (move_object_order - curr_order)
    prev_object.save()
    move_object.order = move_object.order - (move_object_order - curr_order)
    move_object.save()

    return redirect('/profile/')

# View my resume (displays all enabled items)
@login_required
def view_my_resume(request):

    # we pass in user and user info
    return render(request, 'view-my-resume.html', user_profile_dict(request.user, only_enabled=True))


def view_user_resume(request, user_id):

    # we pass in user and user info
    return render(request, 'resume_pdf_template.html', user_profile_dict(User.objects.get(id=user_id), only_enabled=True))



@login_required
def choose_resume_to_edit(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ChooseResumeToEditForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # Find the num_resumes_to_return resumes most relevant to keywords
            #if request.POST.get("search_resumes"):
            print "in search"

            # Search terms; default is empty string
            keywords = request.POST.get('keywords')
            keywords = ("" if None else keywords)

            # Search terms; default is 5
            num_resumes_to_return = request.POST.get('num_resumes_to_return')
            num_resumes_to_return = (5 if None else num_resumes_to_return)

            # a multiset of UserInfo ID's, with 1 occurrence for every time that user is hit in this search 
            id_results = []

            # See if user's contact information or name matches
            id_results += queryset_to_valueslist("id", UserInfo.objects.filter( \
                Q(display_name__icontains=keywords) | Q(phone_number__icontains=keywords) | \
                Q(website__icontains=keywords)).values('id'))

            # Attempts to search in email commented out here.
            # UserInfo and User id's are not the same. We are using the UserInfo id's,
            # so if a User matches, we have to fetch the UserInfo id
            # matching_users = User.objects.filter(email__icontains=keywords)
            # for x in matching_users:
            #     print x
            #     id_results.append(x.user_info.id)

            # Search in Education, Skill categories, Experience, and Awards
            id_results += queryset_to_valueslist("owner_id", Education.objects.filter(Q(enabled=True), \
                Q(school__icontains=keywords) | Q(location__icontains=keywords)).values('owner_id'))
            id_results += queryset_to_valueslist("owner", Skill.objects.filter(Q(enabled=True), \
                Q(category__icontains=keywords)).values('owner'))
            id_results += queryset_to_valueslist("owner", Experience.objects.filter(Q(enabled=True), \
                Q(title__icontains=keywords) | Q(employer__icontains=keywords) | Q(location__icontains=keywords)).values('owner'))
            id_results += queryset_to_valueslist("owner", Award.objects.filter(Q(enabled=True), \
                Q(name__icontains=keywords) | Q(issuer__icontains=keywords)).values('owner'))

            # Search in Bullet Points. BP's only know about their parent objects,
            # so we get the bp's parent's owner's id
            bp_results = BulletPoint.objects.filter(enabled=True, text__icontains=keywords)
            bp_owner_ids = []
            for bp in bp_results:
                bp_owner_ids.append(bp.resume_owner.pk)
            id_results += bp_owner_ids

            # Count and order by how many times the keyword appeared per user, 
            c = collections.Counter(id_results).most_common()
            
            # turn list of tuples (immutable) --> list of lists
            c_1 = map(list, c)

            own_resume = None

            # for every user
            for x in c_1:

                # if the user's own resume showed up in the search,
                # remember it so we can remove it from the results
                if x[0] == request.user.user_info.id:
                    own_resume = x

                # normal behavior: adjust each user's ranking based on rep score
                else:
                    points = UserInfo.objects.get(id=x[0]).points
                    # no one ever loses points for low rep score
                    points_bonus = (4 if (points <= 4) else math.log(points, 1.5))
                    x[1] += points_bonus

            # if user's own resume showed up in search
            if own_resume is not None:
                c_1.remove(own_resume)

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
                return render(request, 'search_resume_results.html', {'form':form})

            # if no search results returned, redirect to search page
            else:
                form = ChooseResumeToEditForm()
                return render(request, 'choose_resume_to_edit.html', {'form': form, 'no_results': True})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = ChooseResumeToEditForm()

    return render(request, 'choose_resume_to_edit.html', {'form': form, 'no_results': False})

# Get most recently commented resumes
@login_required
def most_recently_commented_resumes(request):

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
        NUM_RESUMES_TO_RETURN = 5
        
        # get all comments
        comments = Comment.objects.order_by('-timestamp')

        mrc_resumes_list = []

        # look at all comments until we have NUM_RESUMES_TO_RETURN most recently commented resumes
        for c in comments:

            # the owner of the resume item this comment is on (aka recipient of comment)
            recipient = c.get_header_level_parent().owner


            # append (user id, user's display name) to list of results
            if (recipient.id != request.user.user_info.id) and (recipient.id, recipient.display_name) not in mrc_resumes_list:
                mrc_resumes_list.append((recipient.id, recipient.display_name))

            # once we have NUM_RESUMES_TO_RETURN resumes, stop looking for new resumes
            if len(mrc_resumes_list) > NUM_RESUMES_TO_RETURN:
                break

        # create and populate form with choices of mrc resumes
        form = MostRecentlyCommentedResumesForm()
        form.set_mrc_resumes(mrc_resumes_list)

        return render(request, 'mrc_resumes.html', {'form': form})


def most_popular_resumes(request):

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

    # get request
    else:
        NUM_RESUMES_TO_RETURN = 5


        # list of all users
        all_userinfos = UserInfo.objects.exclude(id = request.user.user_info.id)

        # initialize count of comments for each resume to 0
        comment_count_per_ui = {}
        for ui in all_userinfos:
            comment_count_per_ui[ui.id] = 0

        # count the number of comments per resume/user
        comments = Comment.objects.all()
        for c in comments:

            # id of the owner of the resume item this comment is on (aka id of comment's recipient)
            recipient_id = c.get_header_level_parent().owner.id
            
            # increment number of comments attributed to that resume
            if recipient_id != request.user.user_info.id:
                comment_count_per_ui[recipient_id] = comment_count_per_ui[recipient_id] + 1

        # return the NUM_RESUMES_TO_RETURN most commented resumes
        sorted_top_resumes = sorted(comment_count_per_ui, key=comment_count_per_ui.get, reverse=True)[:NUM_RESUMES_TO_RETURN]
        
        mp_resumes_list = []
        for x in sorted_top_resumes:
            mp_resumes_list.append((x, UserInfo.objects.get(id=x).display_name))


        # create and populate form with choices of mrc resumes
        form = MostPopularResume()
        form.set_mp_resumes(mp_resumes_list)

        return render(request, 'most_popular_resumes.html', {'form': form})



# Randomly choose a user/resume to view, giving priority to users with more rep points
# Priority depends on rep points compared to other users, not absolute rep points
# The general idea is that higher ranked users will be more likely to remain
# in the pool of resumes to be randomly chosen from@login_required
def random_resume(request):

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
    user_index = random.randint(0,upper_limit-1)
    user_info = UserInfo.objects.order_by('-points').exclude(id=request.user.user_info.id)[user_index]

    user_dictionary = user_profile_dict(user_info.user, True)
    user_dictionary.update({'header_user': request.user})

    # comment randomly chosen resume
    return render(request, 'comment_resume.html', user_dictionary)


@login_required
def search_resume_results(request):

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
def move_up_section(request, section_name):

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
def enable_bp(request, bp_id):

    bp = BulletPoint.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_bp(request, bp_id):

    bp = BulletPoint.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_education(request, bp_id):

    bp = Education.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_education(request, bp_id):

    bp = Education.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_experience(request, bp_id):

    bp = Experience.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_experience(request, bp_id):

    bp = Experience.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_skill(request, bp_id):

    bp = Skill.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_skill(request, bp_id):

    bp = Skill.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_award(request, bp_id):

    bp = Award.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_award(request, bp_id):

    bp = Award.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')



@login_required
def move_up_section(request, section_name):

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
def enable_bp(request, bp_id):

    bp = BulletPoint.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_bp(request, bp_id):

    bp = BulletPoint.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_education(request, bp_id):

    bp = Education.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_education(request, bp_id):

    bp = Education.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_experience(request, bp_id):

    bp = Experience.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_experience(request, bp_id):

    bp = Experience.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_skill(request, bp_id):

    bp = Skill.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_skill(request, bp_id):

    bp = Skill.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')


@login_required
def enable_award(request, bp_id):

    bp = Award.objects.get(id=bp_id)
    bp.enabled = True
    bp.save()
    return redirect('/profile/')


@login_required
def disable_award(request, bp_id):

    bp = Award.objects.get(id=bp_id)
    bp.enabled = False
    bp.save()
    return redirect('/profile/')

@login_required
def comment_resume(request):

    # we pass in user and user info
    return render(request, 'comment_resume.html', user_profile_dict(request.user, only_enabled=True))

# Add your experience
@login_required
def create_experience(request):
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


    # if a GET (or any other method) we'll create a blank form
    else:
        form = ExperienceForm()

    return render(request, 'add_experience.html', {'form': form})

# Add an award
@login_required
def create_award(request):
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


    # if a GET (or any other method) we'll create a blank form
    else:
        form = AwardForm()

    return render(request, 'add_award.html', {'form': form})


# Add a skill category
# (User should list individual skills as bullet points under a category)
@login_required
def create_skill_category(request):
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


    # if a GET (or any other method) we'll create a blank form
    else:
        form = SkillCategoryForm()

    return render(request, 'add-skill-category.html', {'form': form})


@login_required
def generate_pdf(request):

    # create the resumePDF
    pdf = ResumePDF()

    # get user id
    user_id = str(request.user.pk)
    pdf.user = request.user.user_info

    # generate file id
    random_int = str(random.randint(00000001, 99999999))
    pdf.path = random_int

    command = 'cd cvhub_app; cd static; cd cvhub_app;  xvfb-run --server-args="-screen 0, 1024x768x24" wkhtmltopdf http://40.83.184.46:8002/view-user-resume/' + user_id + ' ' + random_int + '.pdf'

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
def coverflow(request):

    return render(request, 'coverflow.html', {})


@login_required
def embed_pdf(request):

    pdfs = ResumePDF.objects.filter(user=request.user.user_info)

    if len(pdfs) == 0:
        first_path = ""

    else:
        first_path = pdfs[0].path

    return render(request, 'embed_pdf.html', {'first_path': first_path, 'url_list': pdfs})


@login_required
def view_pdf(request):

    # get user id
    user_id = str(request.user.pk)

    # generate file id
    random_int = str(random.randint(00000001, 99999999))

    command = 'cd cvhub_app; cd static; cd cvhub_app;  xvfb-run --server-args="-screen 0, 1024x768x24" wkhtmltopdf http://40.83.184.46:8002/view-user-resume/' + user_id + ' ' + random_int + '.pdf'

    os.system(command)

    return redirect('/static/cvhub_app/'+str(random_int)+'.pdf')


# Add a skill category
# (User should list individual skills as bullet points under a category)
@login_required
def create_skill_category(request):
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


    # if a GET (or any other method) we'll create a blank form
    else:
        form = SkillCategoryForm()

    return render(request, 'add-skill-category.html', {'form': form})

# method called whenever we want to render profile.html
# gets user's info, education, skills, experience, and awards
def user_profile_dict(user, only_enabled=False):

    user_info = user.user_info

    # get bullet points for user
    if only_enabled:

        bps = BulletPoint.objects.filter(enabled=True, resume_owner=user_info).order_by('order')
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


@login_required
def add_bp_comment(request, bp_id=None):

    if request.method == 'POST':

        print request.POST

        new_comment = Comment()

        # author of comment is poster
        new_comment.author = request.user.user_info

        # get the comment text
        new_comment.text = request.POST.get('comment_text')

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


        # get bp parent
        bp = BulletPoint.objects.get(id=bp_id)
        parent = bp.get_parent()

        # increment pending
        bp.num_pending_comments += 1
        bp.save()

        # get content type
        new_comment.content_type = ContentType.objects.get_for_model(BulletPoint)
        new_comment.object_id = bp_id
        new_comment.parent_item = GenericForeignKey('content_type', 'object_id')
        new_comment.save()

        author.save()

        return redirect('/view-my-resume/')


@login_required
def add_education_comment(request, education_id=None):

    if request.method == 'POST':

        print request.POST

        new_comment = Comment()

        # author of comment is poster
        new_comment.author = request.user.user_info

        # get the comment text
        new_comment.text = request.POST.get('comment_text')

        # is there a suggestion
        new_comment.suggestion = request.POST.get('suggestion_text')

        if request.POST.get('suggestion_text') != "":

            new_comment.is_suggestion = True

            # add rep points for a suggestion to the author
            MADE_SUGGESTION_RP = 15
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_SUGGESTION_RP
            print "test"

        else:

            new_comment.is_suggestion = False

            # add rep points to the commenter
            MADE_COMMENT_RP = 10
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_COMMENT_RP

        print new_comment.is_suggestion

        # increment pending
        edu = Education.objects.get(id=education_id)
        edu.num_pending_comments += 1
        edu.save()

        # get content type
        new_comment.content_type = ContentType.objects.get_for_model(Education)
        new_comment.object_id = education_id
        new_comment.parent_item = GenericForeignKey('content_type', 'object_id')
        new_comment.save()

        author.save()

        return redirect('/view-my-resume/')


@login_required
def add_skill_comment(request, skill_id=None):

    if request.method == 'POST':

        print request.POST

        new_comment = Comment()

        # author of comment is poster
        new_comment.author = request.user.user_info

        # get the comment text
        new_comment.text = request.POST.get('comment_text')

        # is there a suggestion
        new_comment.suggestion = request.POST.get('suggestion_text')

        if request.POST.get('suggestion_text') != "":

            new_comment.is_suggestion = True

            # add rep points for a suggestion to the author
            MADE_SUGGESTION_RP = 15
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_SUGGESTION_RP
            print "test"

        else:

            new_comment.is_suggestion = False

            # add rep points to the commenter
            MADE_COMMENT_RP = 10
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_COMMENT_RP

        print new_comment.is_suggestion

        # increment pending
        edu = Skill.objects.get(id=skill_id)
        edu.num_pending_comments += 1
        edu.save()

        # get content type
        new_comment.content_type = ContentType.objects.get_for_model(Skill)
        new_comment.object_id = skill_id
        new_comment.parent_item = GenericForeignKey('content_type', 'object_id')
        new_comment.save()

        author.save()

        return redirect('/view-my-resume/')


@login_required
def add_experience_comment(request, experience_id=None):

    if request.method == 'POST':

        print request.POST

        new_comment = Comment()

        # author of comment is poster
        new_comment.author = request.user.user_info

        # get the comment text
        new_comment.text = request.POST.get('comment_text')

        # is there a suggestion
        new_comment.suggestion = request.POST.get('suggestion_text')

        if request.POST.get('suggestion_text') != "":

            new_comment.is_suggestion = True

            # add rep points for a suggestion to the author
            MADE_SUGGESTION_RP = 15
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_SUGGESTION_RP
            print "test"

        else:

            new_comment.is_suggestion = False

            # add rep points to the commenter
            MADE_COMMENT_RP = 10
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_COMMENT_RP

        print new_comment.is_suggestion

        # increment pending
        edu = Experience.objects.get(id=experience_id)
        edu.num_pending_comments += 1
        edu.save()

        # get content type
        new_comment.content_type = ContentType.objects.get_for_model(Experience)
        new_comment.object_id = experience_id
        new_comment.parent_item = GenericForeignKey('content_type', 'object_id')
        new_comment.save()

        author.save()

        return redirect('/view-my-resume/')


@login_required
def add_award_comment(request, award_id=None):

    print "THE"

    if request.method == 'POST':

        print request.POST

        new_comment = Comment()

        # author of comment is poster
        new_comment.author = request.user.user_info

        # get the comment text
        new_comment.text = request.POST.get('comment_text')

        # is there a suggestion
        new_comment.suggestion = request.POST.get('suggestion_text')

        if request.POST.get('suggestion_text') != "":

            new_comment.is_suggestion = True

            # add rep points for a suggestion to the author
            MADE_SUGGESTION_RP = 15
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_SUGGESTION_RP
            print "test"

        else:

            new_comment.is_suggestion = False

            # add rep points to the commenter
            MADE_COMMENT_RP = 10
            author = UserInfo.objects.get(id=new_comment.author.id)
            author.points = author.points + MADE_COMMENT_RP

        print new_comment.is_suggestion

        # increment pending
        edu = Award.objects.get(id=award_id)
        edu.num_pending_comments += 1
        edu.save()

        # get content type
        new_comment.content_type = ContentType.objects.get_for_model(Award)
        new_comment.object_id = award_id
        new_comment.parent_item = GenericForeignKey('content_type', 'object_id')

        new_comment.save()

        author.save()

        return redirect('/view-my-resume/')


@login_required
def get_comments_for_bp(request, bp_id):

    # get all the comments
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(BulletPoint), object_id=bp_id).order_by('-vote_total')

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

    # get bp info
    output['bp_info'] = BulletPoint.objects.get(id=bp_id).text

    # get comment info
    output['comments'] = zip(comment_list, votes)

    output = json.dumps(output)
    return HttpResponse(output, content_type='application/json')


@login_required
def get_comments_for_education(request, education_id):

    # get all the comments
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Education), object_id=education_id).order_by('-vote_total')

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

    # get bp info
    output['education_info'] = Education.objects.get(id=education_id).school + ", " + Education.objects.get(id=education_id).location

    # get comment info
    output['comments'] = zip(comment_list, votes)

    output = json.dumps(output)
    return HttpResponse(output, content_type='application/json')


@login_required
def get_comments_for_skill(request, skill_id):

    # get all the comments
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Skill), object_id=skill_id).order_by('-vote_total')

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

    # get bp info
    output['skill_info'] = Skill.objects.get(id=skill_id).category

    # get comment info
    output['comments'] = zip(comment_list, votes)

    output = json.dumps(output)
    return HttpResponse(output, content_type='application/json')


@login_required
def get_comments_for_experience(request, experience_id):

    # get all the comments
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Experience), object_id=experience_id).order_by('-vote_total')

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

    # get bp info
    output['experience_info'] = Experience.objects.get(id=experience_id).title + " at " + Experience.objects.get(id=experience_id).employer

    # get comment info
    output['comments'] = zip(comment_list, votes)

    output = json.dumps(output)
    return HttpResponse(output, content_type='application/json')


@login_required
def get_comments_for_award(request, award_id):

    # get all the comments
    comments = Comment.objects.filter(content_type=ContentType.objects.get_for_model(Award), object_id=award_id).order_by('-vote_total')

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

    # get bp info
    output['award_info'] = Award.objects.get(id=award_id).name + " from " + Award.objects.get(id=award_id).issuer

    # get comment info
    output['comments'] = zip(comment_list, votes)

    output = json.dumps(output)
    return HttpResponse(output, content_type='application/json')


@login_required
def get_comments_for_section(request, section_name, user_info_id):

    # if education
    if section_name == 'EDUCATION':
        comments = SectionComment.objects.filter(section_type=SectionType.EDUCATION, section_owner=UserInfo.objects.get(id=user_info_id)).order_by('-vote_total')

    # get all the comments
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

    if request.method == 'POST':

        new_comment = SectionComment()

        # author of comment is poster
        new_comment.author = request.user.user_info

        # get the comment text
        new_comment.text = request.POST.get('comment_text')

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
def upvote_comment(request, comment_id):

    # assuming they haven't voted before
    vote = Vote()
    vote.user = request.user.user_info
    vote.comment = Comment.objects.get(id=comment_id)
    vote.vote_type = VoteType.UP
    vote.save()
    print vote

    # update total on comment
    comment = Comment.objects.get(id=comment_id)
    comment.vote_total = comment.vote_total + 1
    comment.save()
    print comment

    # rep points for comment author
    UPVOTED_COMMENT_RP = 3
    comment_author = UserInfo.objects.get(id = comment.author.id)
    comment_author.points = comment_author.points + UPVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


@login_required
def downvote_comment(request, comment_id):

    # assuming they haven't voted before
    vote = Vote()
    vote.user = request.user.user_info
    vote.comment = Comment.objects.get(id=comment_id)
    vote.vote_type = VoteType.DOWN
    vote.save()
    print vote

    # update total on comment
    comment = Comment.objects.get(id=comment_id)
    comment.vote_total = comment.vote_total - 1
    comment.save()
    print comment

    # negative rep points for comment author
    DOWNVOTED_COMMENT_RP = -1
    comment_author = UserInfo.objects.get(id = comment.author.id)
    comment_author.points = comment_author.points + DOWNVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


@login_required
def upvote_section_comment(request, section_comment_id):

    # assuming they haven't voted before
    vote = SectionVote()
    vote.user = request.user.user_info
    vote.comment = SectionComment.objects.get(id=section_comment_id)
    vote.vote_type = VoteType.UP
    vote.save()
    print vote

    # update total on comment
    comment = SectionComment.objects.get(id=section_comment_id)
    comment.vote_total = comment.vote_total + 1
    comment.save()
    print comment

    # rep points for comment author
    UPVOTED_COMMENT_RP = 3
    comment_author = UserInfo.objects.get(id=comment.author.id)
    comment_author.points = comment_author.points + UPVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


@login_required
def downvote_section_comment(request, section_comment_id):

    # assuming they haven't voted before
    vote = SectionVote()
    vote.user = request.user.user_info
    vote.comment = SectionComment.objects.get(id=section_comment_id)
    vote.vote_type = VoteType.DOWN
    vote.save()
    print vote

    # update total on comment
    comment = SectionComment.objects.get(id=section_comment_id)
    comment.vote_total = comment.vote_total - 1
    comment.save()
    print comment

    # negative rep points for comment author
    DOWNVOTED_COMMENT_RP = -1
    comment_author = UserInfo.objects.get(id=comment.author.id)
    comment_author.points = comment_author.points + DOWNVOTED_COMMENT_RP
    comment_author.save()

    return redirect('/view-my-resume/')


# Resume owner reviews comments on their resume
@login_required
def review_comments(request):

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))

@login_required
def accept_comment(request, comment_id):
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
            print "successfully rejected", rs.text

    # award rp to commenter
    commenter = UserInfo.objects.get(id=comment.author.id)
    commenter.points = commenter.points + rp
    commenter.save()

    # update comment's status
    comment.status = CommentStatus.ACCEPTED
    comment.save()

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))

# note there is no rp penalty for rejected comment
@login_required
def reject_comment(request, comment_id):
    # retrieve the relevant comment
    comment = Comment.objects.get(id=comment_id)
    comment.status = CommentStatus.DECLINE
    comment.save()

    # decrement pending
    obj = comment.get_parent()
    obj.num_pending_comments -= 1
    obj.save()

    return render(request, 'review_comments.html', user_profile_dict(request.user, True))


@login_required
def accept_section_comment(request, section_comment_id):

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


# note there is no rp penalty for rejected comment
@login_required
def reject_section_comment(request, section_comment_id):
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


# turns a Query Set into a flat list of values for easier use
def queryset_to_valueslist(key, query_set):

    # for every key-value pair in the dictionary, get the value
    id_results = []
    for x in query_set:
        id_results.append(x[key])
        print x

    return id_results

@login_required
def edit_information(request):

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


# When editing resume, enable all items of either Education, Skill,
# Experience, or Award
# However, we don't disable the associated bullet points, because if the header
# level education is disabled, the bp's won't show anyway. And it's possible the
# user wants to remember which bp's are enabled/disabled.
@login_required
def disable_section(request, section_name):

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


# When editing resume, enable all items of either Education, Skill,
# Experience, or Award
# However, we don't disable the associated bullet points, because if the header
# level education is disabled, the bp's won't show anyway. And it's possible the
# user wants to remember which bp's are enabled/disabled.
@login_required
def enable_section(request, section_name):

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


def public_resume_pdf(request, custom_string):

    print "custom string is", custom_string

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

        command = 'cd cvhub_app; cd static; cd cvhub_app;  xvfb-run --server-args="-screen 0, 1024x768x24" wkhtmltopdf http://40.83.184.46:8002/view-user-resume/' + user_id + ' ' + random_int + '.pdf'

        os.system(command)

        return redirect('/static/cvhub_app/'+str(random_int)+'.pdf')
