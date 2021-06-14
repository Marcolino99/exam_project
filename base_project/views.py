import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy, resolve
from django.views.generic import TemplateView, CreateView

_logger = logging.getLogger(__name__)



class Homepage(TemplateView):
    template_name = 'home.html'


class UserCreationView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/user_create.html'
    success_url = reverse_lazy('homepage') #TODO trovare modo di fare redirect alla choose-profile
