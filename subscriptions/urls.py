from django.urls import path

from . import views

app_name = 'subscriptions'

urlpatterns = [
    path('', views.PlanListView.as_view(), name='plan_list'),
    path('my/', views.MySubscriptionListView.as_view(), name='my_subscriptions'),
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
    path(
        'newsletter/unsubscribe/<str:token>/',
        views.NewsletterUnsubscribeView.as_view(),
        name='newsletter_unsubscribe',
    ),
]
