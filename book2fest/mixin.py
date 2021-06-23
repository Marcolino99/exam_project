from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib import messages
from book2fest.models import OrganizerProfile, UserProfile, EventProfile

class OrganizerRequiredMixin:
    """ Mixin that requires a Organize User logged to dispatch, otherwise
        you get redirected"""
    def __init__(self):
        self.profile = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = OrganizerProfile.objects.get(user=request.user)
            return super().dispatch(request, *args, **kwargs)

        except ObjectDoesNotExist:
            messages.error(request, "You have no authorization to access this page." )
            return redirect('book2fest:user-profile')


class UserRequiredMixin:
    """ Mixin that requires a Organize User logged to dispatch, otherwise
        you get redirected"""
    def __init__(self):
        self.profile = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.profile = UserProfile.objects.get(user=request.user)
            return super().dispatch(request, *args, **kwargs)

        except ObjectDoesNotExist:
            messages.error(request, "You have no authorization to access this page.")
            return redirect('book2fest:organizer-profile')

class EventOwnerMixin:
    """ Mixin that redirects with error if event does not exist in the db or if user logged
        is not the owner of the event"""

    def __init__(self):
        self.event_profile = None

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event_profile = EventProfile.objects.get(pk=kwargs.get('pk')) # checks if event exists

            if self.profile: #check id user is logged in
                if self.event_profile.user == self.profile: #checks if user is owner
                    return super().dispatch(request, *args, **kwargs)

        except ObjectDoesNotExist:
            messages.error(request,
                           "Ops.. something went wrong with your request. We can't find the page you are looking for :(")
            return redirect('homepage')

        messages.error(request,
                       "Ops.. something went wrong with your request. It seems that you are not authorized :(")
        return redirect('homepage')



