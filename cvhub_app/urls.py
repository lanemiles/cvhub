from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create-user', views.create_user, name='create_user'),
    url(r'^thanks', views.thanks, name='thanks'),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', 'django.contrib.auth.views.login', 
    	{'template_name': 'login.html'}),
    url(r'^profile', views.user_profile, name='user_profile'),
    url(r'^logout', views.logout_view, name='logout_view'),
    url(r'^add-education', views.create_education, name='create_education'),
    url(r'^edit-education/(?P<education_id>[0-9]+)', views.edit_education, name='edit_education'),
    url(r'^edit-education', views.edit_education, name='edit_education'),
    url(r'^add-bp', views.add_bp, name='add_bp'),
    url(r'^view-my-resume', views.view_my_resume, name='view_my_resume'),
    url(r'^choose-resume-to-edit', views.choose_resume_to_edit, name='choose_resume_to_edit'),
    url(r'^comment-resume', views.comment_resume, name='comment_resume')

]