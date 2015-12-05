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
                    return render(request, 'profile.html', {'user': request.user, \
                        'education_list': Education.objects.filter(owner=user.user_info), \
                        'experience_list': Experience.objects.filter(owner=request.user.user_info).order_by('order'),\
                        'award_list': Award.objects.filter(owner=request.user.user_info).order_by('order'), \
})


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

            return render(request, 'profile.html', user_profile_dict(request))

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

    return render(request, 'profile.html', user_profile_dict(request))


@login_required
def edit_education(request, education_id=None):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        user_info = request.user.user_info
        form = EducationForm(request.POST)
        print form.data
        form2 = EducationForm(request.POST, instance=Education.objects.get(id=form.data.get('edu_id')))
        # check whether it's valid:
        if form2.is_valid():
            # process the data in form.cleaned_data as required

            form2.save()

            # get education bullet points for user
            user = request.user.user_info
            bps = BulletPoint.objects.all()
            user_bps = {}
            for bp in bps:
                if bp.get_parent().owner == user:
                    if bp.get_parent() in user_bps:
                        user_bps[bp.get_parent()].append(bp)
                    else:
                        user_bps[bp.get_parent()] = [bp]

            return render(request, 'profile.html', {'user': request.user, 'education_list': Education.objects.filter(owner=request.user.user_info).order_by('order'), 'bps': user_bps})

    # if a GET (or any other method) we'll create a blank form
    else:

        form = EducationForm(instance=Education.objects.get(id=education_id))

    return render(request, 'edit_education.html', {'form': form, 'edu_id': education_id})

@login_required
def add_bp(request):
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

        return render(request, 'profile.html', user_profile_dict(request))

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

        return render(request, 'profile.html', user_profile_dict(request))

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

    return render(request, 'profile.html', user_profile_dict(request))



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

        return render(request, 'profile.html', user_profile_dict(request))

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

    return render(request, 'profile.html', user_profile_dict(request))

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

            return render(request, 'profile.html', user_profile_dict(request))

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_education(request.user, item_id)

        return render(request, 'add_education_bp.html', {'form': form, 'edu_id': item_id})


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

            return render(request, 'profile.html', user_profile_dict(request))

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

            return render(request, 'profile.html', user_profile_dict(request))

    # if a GET (or any other method) we'll create a blank form
    else:

        form = BulletPointForm(request.user)
        form.set_experience(request.user, item_id)

        return render(request, 'add_experience_bp.html', {'form': form, 'experience_id': item_id})


@login_required
def remove_bp(request, bp_id):

    BulletPoint.objects.get(id=bp_id).delete()
    return render(request, 'profile.html', user_profile_dict(request))


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
        return render(request, 'profile.html', user_profile_dict(request))

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

    return render(request, 'profile.html', user_profile_dict(request))


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
        return render(request, 'profile.html', user_profile_dict(request))

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

    return render(request, 'profile.html', user_profile_dict(request))

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

            if request.POST.get("choose_user"):

                # get selected user's id
                selected_user = form.cleaned_data.get('user_choice')

                # get UserInfo object from the id
                user_info = UserInfo.objects.get(id=selected_user)

            # randomly choose a user & resume to view
            elif request.POST.get("random_resume"):
                user_info = UserInfo.objects.order_by('?').first()

            # redirect to the page for commenting resumes
            return render(request, 'comment_resume.html', {'user': user_info.user.username, \
                'education_list': Education.objects.filter(owner=user_info).order_by('order')})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseResumeToEditForm()

    return render(request, 'choose_resume_to_edit.html', {'form': form})

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

            return render(request, 'profile.html', user_profile_dict(request))


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

            return render(request, 'profile.html', user_profile_dict(request))


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

            return render(request, 'profile.html', user_profile_dict(request))


    # if a GET (or any other method) we'll create a blank form
    else:
        form = SkillCategoryForm()

    return render(request, 'add-skill-category.html', {'form': form})

# method called whenever we want to render profile.html
# gets user's info, education, skills, experience, and awards
def user_profile_dict(request, only_enabled=False):
    # get experience bullet points for user
    user_info = request.user.user_info
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
