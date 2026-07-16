from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Subscription, SubscriptionPlan


class PlanListView(ListView):
    model = SubscriptionPlan
    template_name = 'subscriptions/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True)


class MySubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscriptions/my_subscriptions.html'
    context_object_name = 'subscriptions'

    def get_queryset(self):
        return (
            Subscription.objects.select_related('plan')
            .filter(user=self.request.user)
            .order_by('-start_date')
        )
