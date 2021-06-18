
import logging
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView, CreateView, DetailView, ListView
from django.views.generic.edit import FormMixin

from book2fest.forms import OrganizerProfileForm, UserProfileForm, ArtistForm, EventProfileForm, form_validation_error, \
    SeatForm, TicketForm
from book2fest.mixin import OrganizerRequiredMixin, UserRequiredMixin
from book2fest.models import Artist, UserProfile, OrganizerProfile, EventProfile, Seat, SeatType, Ticket

_logger = logging.getLogger(__name__)

class CompleteRegistrationView(LoginRequiredMixin, TemplateView):
    template_name = 'book2fest/choose_profile.html'


class UserCreate(LoginRequiredMixin, View):
    user_profile = None
    model = UserProfile
    template_name = 'book2fest/choose_profile.html'
    permission_denied_message = "You must authenticate first!"


    def post(self, request):

        form = UserProfileForm(request.POST, request.FILES, instance=self.user_profile)

        if form.is_valid():

            self.user_profile = UserProfile(user=request.user)
            self.user_profile.save()

            self.user_profile.user.first_name = form.cleaned_data.get('first_name')
            self.user_profile.user.last_name = form.cleaned_data.get('last_name')
            self.user_profile.user.email = form.cleaned_data.get('email')
            self.user_profile.user.save()

            messages.success(request, 'Profile saved successfully')

        else:
            messages.error(request, form_validation_error(form))
        return redirect('book2fest:user-profile')

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return super(UserCreate, self).handle_no_permission()


class OrganizerCreate(LoginRequiredMixin, View):
    organizer = None
    model = OrganizerProfile
    template_name = 'book2fest/choose_profile.html'
    permission_denied_message = "You must authenticate first!"


    def post(self, request):

        form = OrganizerProfileForm(request.POST, request.FILES, instance=self.organizer)

        if form.is_valid():

            self.organizer = OrganizerProfile(user=request.user, short_bio=form.cleaned_data.get('short_bio'), company=form.cleaned_data.get('company'))
            self.organizer.save()
            self.organizer.user.first_name = form.cleaned_data.get('first_name')
            self.organizer.user.last_name = form.cleaned_data.get('last_name')
            self.organizer.user.email = form.cleaned_data.get('email')
            self.organizer.user.save()

            messages.success(request, 'Profile saved successfully')
        else:
            messages.error(request, form_validation_error(form))
        return redirect('book2fest:organizer-profile')

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return super(UserCreate, self).handle_no_permission()


class OrganizerProfileView(LoginRequiredMixin, OrganizerRequiredMixin, View):
    profile = None

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


class UserProfileView(LoginRequiredMixin, UserRequiredMixin, View):
    profile = None

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
            profile.user.save()

            messages.success(request, 'Profile saved successfully')
        else:
            messages.error(request, form_validation_error(form))
        return redirect('book2fest:user-profile')


class ArtistCreate(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = Artist
    form_class = ArtistForm
    template_name = "book2fest/artist/create.html"
    permission_denied_message = "You must authenticate first!"
    success_url = reverse_lazy("homepage")

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return super(ArtistCreate, self).handle_no_permission()


class ArtistDetail(DetailView):
    model = Artist
    template_name = "book2fest/artist/detail.html"


class EventCreate(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = EventProfile
    form_class = EventProfileForm
    template_name = "book2fest/event/create.html"
    permission_denied_message = "You must authenticate first!"
    success_url = reverse_lazy("book2fest:organizer-profile")

    def form_valid(self, form):
        form.instance.user = self.profile
        return super(EventCreate, self).form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return super(EventCreate, self).handle_no_permission()


class EventDetail(FormMixin, DetailView):
    model = EventProfile
    form_class = TicketForm
    template_name = 'book2fest/event.html'
    success_url = '/home'
    profile = None
    ticket = None

    def get(self, request, **kwargs):
        form = TicketForm(event_pk=kwargs.pop('pk')) # filter form with event_pk

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        context['form'] = form
        return self.render_to_response(context)


    def post(self, request, **kwargs):
            #check if user is anonymous
            if isinstance(request.user, AnonymousUser):
                return redirect('login')

            self.ticket = Ticket()
            form = TicketForm(request.POST, request.FILES, instance=self.ticket)


            try:
                if form.is_valid():
                    #Get user profile and create ticket

                    self.profile = UserProfile.objects.get(user=request.user)      # retrieve logged user
                    self.ticket.user = self.profile
                    self.ticket.delivery = form.cleaned_data.get('delivery')
                    self.ticket.seat = form.cleaned_data.get('seat')

                    # save ticket
                    self.ticket.save()

                    self.ticket.seat.available = False
                    print(self.ticket.seat)
                    self.ticket.seat.save()
                    messages.success(request, 'Ticket booked successfully')

            except ObjectDoesNotExist:  # if exception catched user is an organizer
                return redirect("book2fest:organizer-profile")

            return redirect('homepage') #TODO Redirect to ticket detail page or something




class EventList(ListView):
    model = EventProfile
    template_name = "book2fest/event/list.html"


class ManageSeat(LoginRequiredMixin, OrganizerRequiredMixin, View):
    # form_class = SeatForm
    # template_name = "book2fest/seat/create.html"
    # permission_denied_message = "You must authenticate first!"
    # success_url = reverse_lazy("book2fest:organizer-profile")
    event_profile = None

    def get(self, request, **kwargs):
        event_id = kwargs.get('pk')
        self.event_profile = EventProfile.objects.get(pk=event_id)
        seat_types = SeatType.objects.all()


        context = {'event': self.event_profile, 'seat_types': seat_types}
        return render(request, 'book2fest/seat/create.html', context)
