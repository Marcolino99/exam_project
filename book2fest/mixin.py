from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.shortcuts import redirect
from django.contrib import messages
from book2fest.models import OrganizerProfile, UserProfile

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