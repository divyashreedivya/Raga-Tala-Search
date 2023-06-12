from django.urls import path, include
from . import views

app_name= 'home'
urlpatterns = [
    path('', views.HomeView.as_view() , name= 'home'),
    path('about/',views.AboutView.as_view(), name='about')
]