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

    return render(request, 'profile.html', user_profile_dict(request))


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
        bps = BulletPoint.objects.all()
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
        bps = BulletPoint.objects.all()
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
        bps = BulletPoint.objects.all()
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
        bps = BulletPoint.objects.all()
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

    for bp in BulletPoint.objects.all().order_by('order'):

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

    for bp in BulletPoint.objects.all().order_by('-order'):

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
    return render(request, 'view-my-resume.html', user_profile_dict(request, True))


@login_required
def choose_resume_to_edit(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ChooseResumeToEditForm(request.POST)
        # check whether it's valid:
        if form.is_valid():

            # randomly choose a user & resume to view
            if request.POST.get("random_resume"):

                user_info = UserInfo.objects.order_by('?').first()

            # Find the num_resumes_to_return resumes most relevant to keywords
            elif request.POST.get("search_resumes"):
                print "search resumes button pressed"

                keywords = form.cleaned_data.get('keywords')
                num_resumes_to_return = form.cleaned_data.get('num_resumes_to_return')

                # if the user pressed search without any values, just return all resumes
                if keywords is None:
                    keywords = ""

                # Search all enabled information for the keywords, and find relevant resume owners' ids
                id_results = []

                # See if user's contact information or name matches
                id_results += queryset_to_valueslist(UserInfo.objects.filter( \
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
                id_results += queryset_to_valueslist(Education.objects.filter(Q(enabled=True), \
                    Q(school__icontains=keywords) | Q(location__icontains=keywords)).values('owner'))
                id_results += queryset_to_valueslist(Skill.objects.filter(Q(enabled=True), \
                    Q(category__icontains=keywords)).values('owner'))
                id_results += queryset_to_valueslist(Experience.objects.filter(Q(enabled=True), \
                    Q(title__icontains=keywords) | Q(employer__icontains=keywords) | Q(location__icontains=keywords)).values('owner'))
                id_results += queryset_to_valueslist(Award.objects.filter(Q(enabled=True), \
                    Q(name__icontains=keywords) | Q(issuer__icontains=keywords)).values('owner'))

                # Search in Bullet Points. BP's only know about their parent objects,
                # so we get the bp's parent's owner's id
                bp_results = BulletPoint.objects.filter(enabled=True, text__icontains=keywords)
                bp_owner_ids = []
                for bp in bp_results:
                    bp_owner_ids.append(bp.get_parent().owner.pk)
                id_results += bp_owner_ids

                # To return the num_resumes_to_return most relevant resumes, 
                # we count how many times the keyword appeared per user
                num_resumes_to_return = 2
                c = collections.Counter(id_results).most_common(num_resumes_to_return)

                top_hits = []
                for x in c:
                    top_hits.append(x[0])

                # make the choice list of tuples (user id, user's display name)
                results_list = []
                for x in top_hits:
                    top_hit_user = UserInfo.objects.values_list('display_name', flat=True).get(pk=x)
                    results_list.append((top_hits, top_hit_user))

                # redirect to results page, with search results
                return render(request, 'search_resume_results.html', {'form':form, 'results_list': results_list})

            # redirect to results page
            return render(request, 'comment_resume.html', {'user': user_info.user.username, \
                'education_list': Education.objects.filter(owner=user_info).order_by('order')})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseResumeToEditForm()

    return render(request, 'choose_resume_to_edit.html', {'form': form})


@login_required
def search_resume_results(request):

    # if this is a POST request we need to process the form data
    if request.method == 'POST':

        # create a form instance and populate it with data from the request:
        form = SearchResumeResultsForm(request.POST)

        # check whether it's valid:
        if form.is_valid():

            if request.POST.get("choose_resume"):

                # get resume owner's id
                selected_resume = request.POST.get('user_choice')

                print selected_resume

                # get UserInfo object about resume owner
                user_info = UserInfo.objects.get(id=selected_resume)

            # go back to choose/search resume screen
            elif request.POST.get("back_to_choose_resume"):
                return render(request, 'choose_resume_to_edit.html', {'form': form})

            # redirect to the page for commenting resumes
            return render(request, 'comment_resume.html', {'user': user_info.user.username, \
                'education_list': Education.objects.filter(owner=user_info).order_by('order')})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = SearchResumeResultsForm(results_list='results_list')

    return render(request, 'search_resume_results.html', {'form': form})




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


# GET: send information about the relevant commentable resume item 
#   to the popup box
# POST: add comments to a resume from the popup box
# add comments to a resume
@login_required
def comment_resume(request):


    # TODO: change depending on what form looks like
    if request.method == 'POST':
        form = CommentResumeForm(request.POST, user=user)
        if form.is_valid():

            # if the user tried to submit a comment
            if request.POST.get("submit_comment"):

                # new comment with comment and suggestion text from form
                new_comment = Comment()
                new_comment.text = form.cleaned_data.get('comment_text')
                new_comment.suggestion = form.cleaned_data.get('suggestion_text')
                new_comment.author = request.user.user_info

                # set comment's foreign key to the selected item
                education_type = ContentType.objects.get_for_model(Education)
                new_comment.content_type = education_type
                education_item = form.cleaned_data.get('commentable_resume_item')
                new_comment.object_id = education_item
            
                # put new comment into the database
                new_comment.save()
                # return redirect('thanks.html') 
                # TODO: return success code here?  

    # GET method
    # given a div id, return information in JSON format 
    else:

        # get commentable resume item
        item_id = request.GET.get('id')

        # return all pending comments (status is 0) related to that resume item
        item_comments = Comments.objects.filter(object_id=item_id, status=CommentStatus.PENDING)

        # turn QuerySet into JSON
        json_comments = serializers.serialize("json", item_comments)

        # return JSON of existing comments for the given item
        return HttpResponse(json_comments)


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

# method called whenever we want to render profile.html
# gets user's info, education, skills, experience, and awards
def user_profile_dict(request, only_enabled=False):
    # get experience bullet points for user
    user_info = request.user.user_info

    if only_enabled:

        bps = BulletPoint.objects.filter(enabled=True).order_by('order')
        user_bps = {}
        for bp in bps:
            if bp.get_parent().owner == user_info:
                if bp.get_parent() in user_bps:
                    user_bps[bp.get_parent()].append(bp)
                else:
                    user_bps[bp.get_parent()] = [bp]

    else:

        bps = BulletPoint.objects.all().order_by('order')
        user_bps = {}
        for bp in bps:
            if bp.get_parent().owner == user_info:
                if bp.get_parent() in user_bps:
                    user_bps[bp.get_parent()].append(bp)
                else:
                    user_bps[bp.get_parent()] = [bp]

    if only_enabled:

        # create dictionary
        dictionary = {'user': request.user, \
                        'user_info': request.user.user_info, \
                        'education_list': Education.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'skill_category_list': Skill.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'experience_list': Experience.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'award_list': Award.objects.filter(owner=user_info, enabled=True).order_by('order'), \
                        'bps': user_bps}

    else:

        # create dictionary
        dictionary = {'user': request.user, \
                        'user_info': request.user.user_info, \
                        'education_list': Education.objects.filter(owner=user_info).order_by('order'), \
                        'skill_category_list': Skill.objects.filter(owner=user_info).order_by('order'), \
                        'experience_list': Experience.objects.filter(owner=user_info).order_by('order'), \
                        'award_list': Award.objects.filter(owner=user_info).order_by('order'), \
                        'bps': user_bps}

    return dictionary





def generate_pdf(request):
    return render(request, 'resume-pdf.html', user_profile_dict(request, True))

def queryset_to_valueslist(query_set):

    # first, QuerySet to dictionary
    id_results = {}
    for x in query_set:
        id_results.update(x)

    # next, only return values in dictionary
    return id_results.values()
