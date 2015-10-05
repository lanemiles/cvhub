from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return render(request, 'templates/current_time.html', {'question': 'hi'})