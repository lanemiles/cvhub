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
    return render(request, 'profile.html', {'user': request.user, 'education_list': Education.objects.filter(owner=request.user.user_info).order_by('order')})


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

            # redirect to a new URL:
            return render(request, 'profile.html', {'user': request.user, 'education_list': Education.objects.filter(owner=user_info).order_by('order')})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = EducationForm()

    return render(request, 'add_education.html', {'form': form})

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
    return render(request, 'view-my-resume.html', {'user': request.user, 'education_list': Education.objects.filter(owner=request.user.user_info, enabled=True)})

# User chooses a resume (or requests a random resume) to comment
# TODO: change this to choose_resume_to_comment, not choose
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
            print "rendering comment_resume"
            return render(request, 'comment_resume.html', {'user': user_info.user.username, 'education_list': Education.objects.filter(owner=user_info).order_by('order'), 'form' : CommentResumeForm(user = user_info.user) })

    # if a GET (or any other method) we'll create a blank form
    else:
        form = ChooseResumeToEditForm()

    return render(request, 'choose_resume_to_edit.html', {'form': form})

# GET: send information about the relevant commentable resume item 
#   to the popup box
# POST: add comments to a resume from the popup box
@login_required
def comment_resume(request):

    # did we arrive at comment_resume legally, after choosing a user or getting a random resume?
    # try:
    #    user
    # except NameError:
        # no resume chosen - redirect to resume choosing page
        # print "NameError"
        # return redirect('choose_resume_to_edit')   
    #else:

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


    # valid resume chosen - can edit
    # return render(request, 'comment_resume.html', {'user': user.username, 'education_list': Education.objects.filter(owner=user_info).order_by('order'), 'form' : CommentResumeForm(user = user) })
