from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile-setup/', views.profile_setup, name='profile_setup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings, name='settings'),
    path('history/', views.history, name='history'),
    path('log-water/', views.log_water, name='log_water'),
    
    # Challenge URLs
    path('challenges/', views.challenges_list, name='challenges_list'),
    path('challenges/create/', views.create_challenge, name='create_challenge'),
    path('challenges/<int:challenge_id>/', views.challenge_detail, name='challenge_detail'),
    path('challenges/<int:challenge_id>/join/', views.join_challenge, name='join_challenge'),
    path('challenges/<int:challenge_id>/leaderboard/', views.leaderboard, name='leaderboard'),
    
    # API URLs
    path('api/water-tips/', views.get_water_tips, name='water_tips_api'),
    path('api/coachbot-message/', views.get_coachbot_message_api, name='coachbot_message_api'),
]
