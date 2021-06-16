
import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.views.generic import View, DetailView
from django.views.generic.edit import FormMixin

from .forms import UserProfileForm, form_validation_error, TicketForm
from .models import UserProfile, EventProfile

_logger = logging.getLogger(__name__)

class EventDetailView(FormMixin, DetailView):
    model = EventProfile
    form_class = TicketForm
    template_name = 'book2fest/event.html'
    success_url = '/home'

    """
    def __init__(self, user, *args, **kwargs):
        super(EventDetailView, self).__init__(*args, **kwargs)
        self.form_class.fields['user'].queryset = User.objects.filter(pk=user.id)
    """

    def form_valid(self, form):
        form.save()


class UserProfileView(LoginRequiredMixin, View):
    profile = None

    def dispatch(self, request, *args, **kwargs):
        self.profile, __ = UserProfile.objects.get_or_create(user=request.user)
        return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {'profile': self.profile}
        return render(request, 'book2fest/user_profile.html', context)

    def post(self, request):
        form = UserProfileForm(request.POST, request.FILES, instance=self.profile)

        if form.is_valid():
            profile = form.save()
            profile.user.first_name = form.cleaned_data.get('first_name')
            profile.user.last_name = form.cleaned_data.get('last_name')
            profile.user.email = form.cleaned_data.get('email')
            profile.user.organizer = form.cleaned_data.get('organizer')
            profile.user.save()

            messages.success(request, 'Profile saved successfully')
        else:
            messages.error(request, form_validation_error(form))
        return redirect('book2fest:user-profile')





