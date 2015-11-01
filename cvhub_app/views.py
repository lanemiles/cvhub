from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from cvhub_app.forms import *


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
            # ...
            # redirect to a new URL:
            return HttpResponseRedirect('/thanks/')

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UserInfoForm()

    return render(request, 'create_user.html', {'form': form})


def thanks(request):
    return render(request, 'thanks.html', {})