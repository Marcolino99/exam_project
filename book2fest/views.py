
import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView
from django.core.exceptions import ObjectDoesNotExist

from book2fest.forms import OrganizerProfileForm, UserProfileForm, form_validation_error
from book2fest.models import UserProfile,OrganizerProfile

_logger = logging.getLogger(__name__)

class ChooseProfileView(LoginRequiredMixin, TemplateView):
    template_name = "book2fest/choose_profile.html"

    # def get(self, request):
    #     # Control if user logged is already a normal user'
    #     temp = UserProfile.objects.get(user=request.user)
    #     print("\n\n\n"+temp.__str__())
    #
    #     if temp is not None:
    #         #User has already choosed to be a normal user
    #         context = {'profile': temp}
    #         return render(request, 'book2fest/user/user_profile.html', context)
    #
    #     temp = OrganizerProfile.objects.get(user=request.user)
    #
    #     if temp is not None:
    #         # User has already choosed to be an organizer
    #         context = {'profile': temp}
    #         return render(request, 'book2fest/organizer/profile.html', context)
    #
    #     return super.get(self, request)



class OrganizerProfileView(LoginRequiredMixin, View):
    profile = None

    def dispatch(self, request, *args, **kwargs):

        try:
            temp = UserProfile.objects.get(user=request.user)
            #User has already choosed to be a normal user
            context = {'profile': temp}
            return render(request, 'book2fest/user/user_profile.html', context)

        except ObjectDoesNotExist:

            self.profile, __ = OrganizerProfile.objects.get_or_create(user=request.user)
            return super(OrganizerProfileView, self).dispatch(request, *args, **kwargs)




    def get(self, request):
        context = {'profile': self.profile}
        return render(request, 'book2fest/organizer/profile.html', context)

    def post(self, request):
        form = OrganizerProfileForm(request.POST, request.FILES, instance=self.profile)

        if form.is_valid():
            profile = form.save()
            profile.user.first_name = form.cleaned_data.get('first_name')
            profile.user.last_name = form.cleaned_data.get('last_name')
            profile.user.email = form.cleaned_data.get('email')
            profile.user.company = form.cleaned_data.get('company')
            profile.user.short_bio = form.cleaned_data.get('short_bio')
            profile.user.save()

            messages.success(request, 'Profile saved successfully')
        else:
            messages.error(request, form_validation_error(form))
        return redirect('book2fest:organizer-profile')


class UserProfileView(LoginRequiredMixin, View):
    profile = None

    def dispatch(self, request, *args, **kwargs):
        try:
            temp = OrganizerProfile.objects.get(user=request.user)
            # User has already choosed to be a normal user
            context = {'profile': temp}
            return render(request, 'book2fest/organizer/profile.html', context)

        except ObjectDoesNotExist :
            self.profile, __ = UserProfile.objects.get_or_create(user=request.user)
            return super(UserProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {'profile': self.profile}
        return render(request, 'book2fest/user/user_profile.html', context)

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





