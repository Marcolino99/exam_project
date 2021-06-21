
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
    TicketForm, SeatForm
from book2fest.mixin import OrganizerRequiredMixin, UserRequiredMixin
from book2fest.models import Artist, UserProfile, OrganizerProfile, EventProfile, SeatType, Ticket, Seat, Category, \
    Genre

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

    # def get_form_kwargs(self):
    #     s = str(self.request)
    #     req = s[s[:s.rfind('/')].rfind('/')+1:s.rfind('/')]
    #     kwargs = super(EventDetail, self).get_form_kwargs()
    #     print(req)
    #     kwargs['request'] =req
    #     print(kwargs)
    #     return kwargs

    def get_context_data(self, **kwargs):
        context = super(EventDetail, self).get_context_data(**kwargs)
        occupied_seats = Seat.objects.filter(event=self.object).filter(available=False)
        righe = (Seat.objects.filter(event=self.object).values('name','number','price','row','available','seat_type').order_by('row','number'))

        d = {}
        for x in righe:
            if x['row'] in d.keys():
                d[x['row']].append(x)
            else:
                d[x['row']] = [x]
        l = []
        for x in d:
            l.append(d[x])

        context.update({'righe': l})
        context.update({'occupied_seats': occupied_seats})
        return context

    def form_valid(self, form):
        form.save()

    def get(self, request, **kwargs):
        # kwargs = self.get_form_kwargs()
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

    def get_queryset(self):
        result = super(EventList, self).get_queryset()
        query = self.request.GET.get('search', None)
        filter = self.request.GET.get('search-filter', None)

        if query:
            if filter == "category":
                categories = Category.objects.all().filter(name__contains=query)
                genres = Genre.objects.all().filter(category__in=categories)
                artists = Artist.objects.all().filter(genre__in=genres)
                result = EventProfile.objects.all().filter(artist_list__in=artists).distinct()

            if filter == "genre":
                genres = Genre.objects.all().filter(name__contains=query)
                artists = Artist.objects.all().filter(genre__in=genres)
                result = EventProfile.objects.all().filter(artist_list__in=artists).distinct()

            if filter == "artist":
                artists = Artist.objects.all().filter(full_name__contains=query)
                result = EventProfile.objects.all().filter(artist_list__in=artists).distinct()

            if filter == "event_name":
                result = EventProfile.objects.all().filter(event_name__contains=query)

        return result


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(EventList, self).get_context_data(**kwargs)
        try:
            # count seats available for events
            for event in self.object_list:
                seat_not_available = Seat.objects.all().filter(event=event.pk, available=False).count()
                event.available  = Seat.objects.all().filter(event=event.pk).count() - seat_not_available

            # if user is organizer -> show manage seat column in table
            if not isinstance(self.request.user, AnonymousUser):
                context['organizer'] = OrganizerProfile.objects.get(user=self.request.user)

        except ObjectDoesNotExist:
            context['organizer'] = None

        return context


class ManageSeat(LoginRequiredMixin, OrganizerRequiredMixin, View):
    event_profile = None
    event_id = None

    def dispatch(self, request, *args, **kwargs):
        self.event_id = kwargs.get('pk')

        try:
            self.event_profile = EventProfile.objects.get(pk=self.event_id)

        except ObjectDoesNotExist:
            # trying to manage seat of an event that does not exist
            return redirect('homepage')  # TODO redirect to another page maybe

        return super(ManageSeat, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):

        if self.profile == self.event_profile.user:
            seat_types = SeatType.objects.all()
            context = {'event': self.event_profile, 'seat_types': seat_types}
            return render(request, 'book2fest/seat/create.html', context)
        else:
            #User trying to manage seats not of one of his events
            return redirect('homepage') #TODO redirect to another page maybe

    def post(self, request, **kwargs):

        form = SeatForm(request.POST, request.FILES)
        if form.is_valid():
            total = form.cleaned_data.get('quantity')
            price = form.cleaned_data.get('price')
            row = form.cleaned_data.get('row')
            seat_type = form.cleaned_data.get('seat_type')

            for number in range(total):
                seat = Seat(price=price, row=row, number=number, seat_type=seat_type, available=True, event=self.event_profile)
                seat.save()

            messages.success(request, f"Added {total} seats successfully")



        else:
            messages.error(request, form_validation_error(form))

        return redirect('book2fest:event-detail', pk=kwargs.get('pk'))

from notifications.signals import notify

class EventCancel(ManageSeat):

    def get(self, request, **kwargs):

        if self.profile == self.event_profile.user:
            # self.event_profile.cancelled = True
            # self.event_profile.save()


            #retrieve all users that bought ticket for this event
            seats = Seat.objects.all().filter(event=self.event_profile)

            corr = Ticket.objects.filter(seat__in=seats).values_list('user')
            profiles = []

            for d in corr:
                profiles.append(UserProfile.objects.get(id=d[0]))

            for profile in profiles:
                 notify.send(profile.user, recipient=profile.user, verb='Event cancelled', description=f"{self.event_profile.event_name} has been cancelled!", target=self.event_profile)

        else:
            #show error you are not authorized
            pass

        return redirect("book2fest:manage-seat", pk=self.event_id)


class UserTicketList(LoginRequiredMixin, UserRequiredMixin, ListView):
    model = Ticket
    template_name = "book2fest/ticket/list.html"

    def get_queryset(self):
        return Ticket.objects.all().filter(user=self.profile)


class ManageTicket(LoginRequiredMixin, UserRequiredMixin, View):
    ticket = None
    form = None

    def dispatch(self, request, *args, **kwargs):
        ticket_pk = kwargs.get('pk')
        try:
            self.ticket = Ticket.objects.get(pk=ticket_pk)

        except ObjectDoesNotExist:
            # trying to access to a ticket that does not exist
            return redirect('homepage') #TODO redirect to another page maybe

        return super(ManageTicket, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        if self.ticket.user == self.profile:

            context = {'ticket': self.ticket}
            return render(request, "book2fest/ticket/manage.html", context)
        else:
            # user trying to manage not one of his tickets
            return redirect('homepage')  # TODO redirect to another page maybe


    #TODO post method
