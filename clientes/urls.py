from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('cadastro/', views.cadastro_api, name='cadastro'),
    path('service/', views.service, name='service'),
    #path("google_login/", views.google_login, name="google_login"),
    #path("oauth2callback/", views.oauth2callback, name="oauth2callback"),
    #path("calendar/", views.calendar_events, name="calendar_events"),
    #path('login/', views.login, name='login'),
    #path('singup/', views.signup, name='signup'),

]