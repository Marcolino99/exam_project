
import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import View

from book2fest.forms import UserProfileForm, form_validation_error
from book2fest.models import UserProfile

_logger = logging.getLogger(__name__)



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





