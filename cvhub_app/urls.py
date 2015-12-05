from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create-user', views.create_user, name='create_user'),
    url(r'^thanks', views.thanks, name='thanks'),
    url(r'^$', views.index, name='index'),
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    url(r'^profile', views.user_profile, name='user_profile'),
    url(r'^logout', views.logout_view, name='logout_view'),
    url(r'^add-education/', views.create_education, name='create_education'),
    url(r'^edit-education/(?P<education_id>[0-9]+)', views.edit_education, name='edit_education'),
    url(r'^edit-education/', views.edit_education, name='edit_education'),
    url(r'^edit-skill/(?P<skill_id>[0-9]+)', views.edit_skill, name='edit_skill'),
    url(r'^edit-skill', views.edit_skill, name='edit_skill'),
    url(r'^remove-skill/(?P<skill_id>[0-9]+)', views.remove_skill, name='remove_skill'),
    url(r'^remove-experience/(?P<experience_id>[0-9]+)', views.remove_experience, name='remove_experience'),
    url(r'^remove-education/(?P<education_id>[0-9]+)', views.remove_education, name='remove_education'),
    url(r'^add-education-bp/(?P<item_id>[0-9]+)', views.add_education_bp, name='add_education_bp'),
    url(r'^add-education-bp', views.add_education_bp, name='add_education_bp'),
    url(r'^add-skill-bp/(?P<item_id>[0-9]+)', views.add_skill_bp, name='add_skill_bp'),
    url(r'^add-skill-bp', views.add_skill_bp, name='add_skill_bp'),
    url(r'^add-experience-bp/(?P<item_id>[0-9]+)', views.add_experience_bp, name='add_experience_bp'),
    url(r'^add-experience-bp', views.add_experience_bp, name='add_experience_bp'),
    url(r'^view-my-resume', views.view_my_resume, name='view_my_resume'),
    url(r'^generate-pdf', views.generate_pdf, name='generate_pdf'),
    url(r'^choose-resume-to-edit', views.choose_resume_to_edit, name='choose_resume_to_edit'),
    url(r'^search-resume-results', views.search_resume_results, name='search_resume_results'),
    url(r'^comment-resume', views.comment_resume, name='comment_resume'),
    url(r'^add-experience/', views.create_experience, name='create_experience'),
    url(r'^edit-experience/(?P<experience_id>[0-9]+)', views.edit_experience, name='edit_experience'),
    url(r'^edit-experience/', views.edit_experience, name='edit_experience'),
    url(r'^add-award', views.create_award, name='create_award'),
    url(r'^add-skill-category', views.create_skill_category, name='create_skill_category'),
    url(r'^remove-bp/(?P<bp_id>[0-9]+)', views.remove_bp, name='remove_bp'),
    url(r'^move-up-bp/(?P<bp_id>[0-9]+)', views.move_up_bp, name='move_up_bp'),
    url(r'^move-down-bp/(?P<bp_id>[0-9]+)', views.move_down_bp, name='move_down_bp')
]