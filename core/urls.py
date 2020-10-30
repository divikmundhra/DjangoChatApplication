from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('create/<str:room_name>/', views.room, name='room'),
    path('create/connect/login', views.forward, name='room'),
    path('logout', views.logoutPage, name="logout"),
    path('', views.homePage, name="home"), 
    path('login/', views.loginPage, name="login"),
    path('register', views.registerPage, name="register"), 
]
