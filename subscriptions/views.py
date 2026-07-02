from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Subscription, SubscriptionPlan


def plan_list(request):
    plans = SubscriptionPlan.objects.filter(is_active=True)
    return render(request, 'subscriptions/plan_list.html', {'plans': plans})


@login_required
def my_subscriptions(request):
    subscriptions = (
        Subscription.objects.select_related('plan')
        .filter(user=request.user)
        .order_by('-start_date')
    )
    return render(
        request,
        'subscriptions/my_subscriptions.html',
        {'subscriptions': subscriptions},
    )

# Create your views here.
