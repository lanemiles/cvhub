from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from cvhub_app.forms import *
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.db.models import Max
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist


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
            user = User.objects.create_user(form.cleaned_data.get('email'), form.cleaned_data.get('email'), form.cleaned_data.get('password'))
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
                    return render(request, 'profile.html', {'user': request.user, 'education_list': Education.objects.filter(owner=user.user_info)})


    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserInfoForm()

    return render(request, 'create_user.html', {'form': form})


def thanks(request):
    return render(request, 'thanks.html', {})


@login_required
def user_profile(request):

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

            education_info = form.cleaned_data

            gpa = education_info.pop('gpa', None)
            
            # create education
            education = Education(**education_info)
            education.owner = user_info
            
            # set order to last item
            order_max = Education.objects.filter(owner=user_info).aggregate(Max('order')).get('order__max')
            if order_max is not None:
                education.order = order_max + 1
            else:
                education.order = 1

            education.save()

            # create the GPA bullet point for it
            bp = BulletPoint()

            # get text of bullet point from form
            print gpa
            bp.text = "GPA: " + str(gpa)

            # enable/disable the bullet point
            bp.enabled = True

            # return all bullet points for that education, and find the next number for an ordering
            bp.order = 1

            # set bullet point's foreign keys to a given education choice
            education_type = ContentType.objects.get_for_model(Education)
            bp.content_type = education_type
            bp.object_id = education.pk
            
            # add bullet point to db
            bp.save()

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
        form = EducationForm()

    return render(request, 'add_education.html', {'form': form})

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
            education = form.cleaned_data.get('education_item_choices')

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

            # redirect to a new URL:
            return render(request, 'profile.html', {'user': request.user, 'education_list': Education.objects.filter(owner=user_info)})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = BulletPointForm(request.user)

    return render(request, 'add_bp.html', {'form': form})

# View my resume (displays all enabled items)
@login_required
def view_my_resume(request):

    # we pass in user and user info

    # get education objects
    try:

        education_list = Education.objects.filter(owner=request.user.user_info, enabled=True)

    except ObjectDoesNotExist:

        education_list = {}

    # then we need to get education items
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


    return render(request, 'view-my-resume.html', {'user': request.user, 'user_info': request.user.user_info, 'education_list': education_list, 'bps': user_bps})

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
            return render(request, 'comment_resume.html', {'user': user_info.user.username, 'education_list': Education.objects.filter(owner=user_info).order_by('order')})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseResumeToEditForm()

    return render(request, 'choose_resume_to_edit.html', {'form': form})

# add comments to a resume
@login_required
def comment_resume(request):

    # did we arrive at comment_resume legally, after choosing a user or getting a random resume?
    try:
        user_info
    except NameError:

        # no resume chosen - redirect to resume choosing page
        return redirect('choose_resume_to_edit')   
    else:

        # valid resume chosen - can edit
        return render(request, 'comment_resume.html', {'education_list': Education.objects.filter(owner=user_info).order_by('order')})
