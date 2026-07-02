from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.plan_list, name='plan_list'),
    path('my/', views.my_subscriptions, name='my_subscriptions'),
]
