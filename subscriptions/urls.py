from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.PlanListView.as_view(), name='plan_list'),
    path('my/', views.MySubscriptionListView.as_view(), name='my_subscriptions'),
]
