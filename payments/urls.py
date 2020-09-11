"""gameshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import path, re_path, include
from . import views
from django.contrib.auth import views as auth_views


""" these paths are just random ones that I used to get a basic  """
urlpatterns = [

    path('<game_id>', views.payment, name='payment'),
    path('',views.payment,name='payment_frame'),
    re_path(r'^success', views.success, name='payment_success'),
    re_path(r'^error', views.error, name='payment_error'),
    re_path(r'^request', views.payment, name='payment_request'),
    re_path(r'^cancel', views.payment_cancel, name = 'payment_cancel'),
    re_path(r'^', views.back_home),


]
