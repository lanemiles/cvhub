from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from cvhub_app.forms import *
from django.contrib.auth.decorators import login_required


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

            # redirect to a new URL:
            return render(request, 'thanks.html', {'user_wrapper': user_wrapper})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserInfoForm()

    return render(request, 'create_user.html', {'form': form})


def thanks(request):
    return render(request, 'thanks.html', {})

@login_required
def user_profile(request):
    return render(request, 'profile.html', {'user': request.user })