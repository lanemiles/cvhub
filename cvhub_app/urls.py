from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create-user', views.create_user, name='create_user'),
    url(r'^thanks', views.thanks, name='thanks'),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', 'django.contrib.auth.views.login', 
    	{'template_name': 'login.html'}),
    url(r'^profile', views.user_profile, name='user_profile')
]