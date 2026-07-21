from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView, ListView, TemplateView

from .forms import NewsletterSubscriptionForm
from .models import NewsletterSubscription, Subscription, SubscriptionPlan


class PlanListView(ListView):
    model = SubscriptionPlan
    template_name = 'subscriptions/plan_list.html'
    context_object_name = 'plans'

    def get_queryset(self):
        return SubscriptionPlan.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        initial = {}
        if self.request.user.is_authenticated and self.request.user.email:
            initial['email'] = self.request.user.email
        context['newsletter_form'] = NewsletterSubscriptionForm(initial=initial)
        return context


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


class NewsletterSubscribeView(FormView):
    form_class = NewsletterSubscriptionForm
    success_url = reverse_lazy('subscriptions:plan_list')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        subscription, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={
                'user': self.request.user if self.request.user.is_authenticated else None,
                'is_active': True,
            },
        )
        if not created:
            subscription.is_active = True
            if self.request.user.is_authenticated and not subscription.user:
                subscription.user = self.request.user
            subscription.save()

        messages.success(self.request, 'Підписку активовано. Нові статті прийдуть на email.')
        return super().form_valid(form)


class NewsletterUnsubscribeView(TemplateView):
    template_name = 'subscriptions/newsletter_unsubscribe.html'

    def dispatch(self, request, *args, **kwargs):
        self.subscription = NewsletterSubscription.objects.filter(
            token=self.kwargs['token'],
        ).first()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.subscription:
            self.subscription.is_active = False
            self.subscription.save(update_fields=('is_active', 'updated_at'))
            messages.success(request, 'Ви відписалися від email-повідомлень.')
        return redirect('subscriptions:plan_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['subscription'] = self.subscription
        return context
