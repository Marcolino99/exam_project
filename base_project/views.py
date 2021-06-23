import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, resolve
from django.shortcuts import redirect
from django.views.generic import TemplateView, CreateView

_logger = logging.getLogger(__name__)

class UserCreationView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/user_create.html'
    success_url = reverse_lazy('book2fest:complete-reg')

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, "You are already authenticated. You can't sign another user.")
            return redirect("homepage")
        return super(UserCreationView, self).dispatch(request, *args, **kwargs)
