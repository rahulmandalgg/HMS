"""HMS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from login.views import login,admin,doctor,frontdesk,dataoperator
from login import views

urlpatterns = [
    path('', login),
    path('admin/', views.admin,name='admin'),
    path('doctor/', views.doctor,name='doctor'),
    path('frontdesk/', views.frontdesk,name='frontdesk'),
    path('dataoperator/', views.dataoperator,name='dataoperator'),
    path('error/', views.errorhtml,name='error'),

]