import logging
from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import View, TemplateView, CreateView, DetailView, ListView, UpdateView
from django.views.generic.edit import FormMixin

from book2fest.forms import OrganizerProfileForm, UserProfileForm, ArtistForm, EventProfileForm, form_validation_error, \
    TicketForm, SeatForm, ReviewForm, SeatTypeForm, PictureForm
from book2fest.mixin import OrganizerRequiredMixin, UserRequiredMixin, EventOwnerMixin
from book2fest.models import Artist, UserProfile, OrganizerProfile, EventProfile, SeatType, Ticket, Seat, Category, \
    Genre, Review, Picture

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


class ProfileView(LoginRequiredMixin, View): #redirect view

    def dispatch(self, request, *args, **kwargs):

        if isinstance(request.user, AnonymousUser):
            return redirect('login')

        if UserProfile.objects.filter(user=request.user).exists():
            return redirect('book2fest:user-profile')

        if OrganizerProfile.objects.filter(user=request.user).exists():
            return redirect('book2fest:organizer-profile')


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
    success_url = reverse_lazy("book2fest:artist-list")

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return super(ArtistCreate, self).handle_no_permission()


class ArtistList(ListView):
    model = Artist
    template_name = "book2fest/artist/list.html"

    def get_queryset(self):
        result = super(ArtistList, self).get_queryset()
        query = self.request.GET.get('search', None)
        filter = self.request.GET.get('search-filter', None)
        key = None
        print(f'query {query}')

        if query:
            if filter == 'name':
                key = 'full_name__contains'

            if filter == 'genre':
                key = 'genre__name__contains'

            if filter == 'category':
                key = 'genre__category__name__contains'

            kwargs = {key: query}
            result = Artist.objects.all().filter(**kwargs)

        return result

    def get_context_data(self):
        context = super(ArtistList, self).get_context_data()
        try:
            if not isinstance(self.request.user, AnonymousUser):
                # if user is organizer -> show manage seat column in table
                context['organizer'] = OrganizerProfile.objects.get(user=self.request.user)

        except ObjectDoesNotExist:
            context['organizer'] = None

        return context


class SeatTypeCreate(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = SeatType
    form_class = SeatTypeForm
    template_name = "book2fest/seat/seat_type.html"
    success_url = reverse_lazy('book2fest:event-list')


class EventCreate(LoginRequiredMixin, OrganizerRequiredMixin, CreateView):
    model = EventProfile
    form_class = EventProfileForm
    template_name = "book2fest/event/create.html"
    permission_denied_message = "You must authenticate first!"
    success_url = reverse_lazy("book2fest:event-list")

    def form_valid(self, form):
        form.instance.user = self.profile
        return super(EventCreate, self).form_valid(form)

    def handle_no_permission(self):
        messages.error(self.request, self.permission_denied_message)
        return super(EventCreate, self).handle_no_permission()


class EventImagesUpload(LoginRequiredMixin, OrganizerRequiredMixin, EventOwnerMixin, View):
    event_profile = None

    def dispatch(self, request, *args, **kwargs):
        return super(EventImagesUpload, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        form = PictureForm()
        context = {'form':form, 'event':self.event_profile}
        return render(request, "book2fest/event/images-upload.html", context)

    def post(self, request, **kwargs):

        form = PictureForm(request.POST, request.FILES)
        if form.is_valid():
            for img in request.FILES.getlist('img'):
                Picture.objects.create(event=self.event_profile, img=img, name=form.cleaned_data.get('name'), description=form.cleaned_data.get('description'))
            messages.success(request, "Uploaded images successfully!")
            return redirect('book2fest:event-detail', self.event_profile.pk)
        else:
            messages.error(request, form_validation_error(form))
            return redirect(request.path_info)


class EventUpdate(LoginRequiredMixin, OrganizerRequiredMixin, EventOwnerMixin, UpdateView):
    model = EventProfile
    form_class = EventProfileForm
    success_url = reverse_lazy('homepage')
    template_name = "book2fest/event/update.html"


class EventDetail(FormMixin, DetailView):
    model = EventProfile
    form_class = TicketForm
    template_name = 'book2fest/event.html'
    success_url = '/home'
    profile = None
    ticket = None


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

        stars_number = int(self.object.avg_rating)
        reviews = Review.objects.filter(ticket__seat__event=self.object)

        context.update({'righe': l})
        context.update({'occupied_seats': occupied_seats})
        context.update({'stars_number': stars_number})
        context.update({'reviews': reviews})
        return context

    def form_valid(self, form):
        form.save()

    def get(self, request, **kwargs):
        # kwargs = self.get_form_kwargs()
        form = TicketForm(event_pk=kwargs.get('pk')) # filter form with event_pk

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)

        # Retrieve pictures
        try:
            context['pictures'] = Picture.objects.all().filter(event__pk=kwargs.get('pk'))

        except ObjectDoesNotExist:
            context['pictures'] = None

        context['form'] = form
        return self.render_to_response(context)


    def post(self, request, **kwargs):
        #check if user is anonymous
        if isinstance(request.user, AnonymousUser):
            return redirect('login')

        self.ticket = Ticket()
        form = TicketForm(request.POST, request.FILES, instance=self.ticket)


        try:
            if form.is_valid() and not self.get_object().cancelled and not self.get_object().is_past:
                #Get user profile and create ticket

                self.profile = UserProfile.objects.get(user=request.user)      # retrieve logged user
                self.ticket.user = self.profile
                self.ticket.delivery = form.cleaned_data.get('delivery')
                self.ticket.seat = form.cleaned_data.get('seat')

                if self.ticket.seat.available:
                    # save ticket
                    self.ticket.save()
                    self.ticket.seat.available = False
                    self.ticket.seat.save()
                    messages.success(request, 'Ticket booked successfully')
                else:
                    messages.error(request, "Something went wrong with your booking procedure. The seat is not available")
                    return redirect('book2fest:event-list')

            else:
                error = form_validation_error(form) if not form.is_valid() else "Something went wrong with your booking procedure. The event got cancelled or is past."
                messages.error(request, error)
                return redirect('book2fest:event-list')

        except ObjectDoesNotExist:  # if exception caught user is an organizer
            messages.error(request,"Sorry,but you are not allowed to book tickets.")
            return redirect("book2fest:organizer-profile")

        return redirect('book2fest:ticket-manage', self.ticket.pk)



def get_seat_available(event_id):
    """ Return the amount of seats available and unavailable for an event"""
    if event_id:
        return Seat.objects.all().filter(event=event_id, available=True).count()
    else:
        return None



class EventList(ListView):
    model = EventProfile
    template_name = "book2fest/event/list.html"

    def get_queryset(self):
        result = super(EventList, self).get_queryset()
        query = self.request.GET.get('search', None)
        filter = self.request.GET.get('search-filter', None)

        if query:
            if filter == "category":
                result = EventProfile.objects.all().filter(artist_list__genre__category__name__contains=query).distinct()

            if filter == "genre":
                result = EventProfile.objects.all().filter(artist_list__genre__name__contains=query).distinct()

            if filter == "artist":
                result = EventProfile.objects.all().filter(artist_list__full_name__contains=query).distinct()

            if filter == "event_name":
                result = EventProfile.objects.all().filter(event_name__contains=query)

        return result


    def get_ordering(self):
        ordering = self.request.GET.get('order-filter')
        # validate ordering here
        if ordering == "avg_rating":
            ordering = "-avg_rating"
        if ordering == "seats_available":
            ordering = "-seats_available"
        return ordering


    def get_context_data(self, *, object_list=None, **kwargs):

        context = super(EventList, self).get_context_data(**kwargs)
        context['order_filters'] = ['event_name', 'event_start', 'avg_rating', 'seats_available']
        try:
            # count seats available and average rating for events
            for event in self.object_list:

                event.seats_available = get_seat_available(event.pk)

                event_seats = Seat.objects.all().filter(event=event.pk)
                event_tickets = Ticket.objects.all().filter(seat__in=event_seats)
                qs = Review.objects.filter(ticket__in=event_tickets).aggregate(Avg('rating'))

                if not qs.get('rating__avg'):
                    event.avg_rating = 0.0
                else:
                    event.avg_rating = qs.get('rating__avg')

                event.save()


            if not isinstance(self.request.user, AnonymousUser):
                # if user is organizer -> show manage seat column in table
                context['organizer'] = OrganizerProfile.objects.get(user=self.request.user)

        except ObjectDoesNotExist:
            context['organizer'] = None

        return context

def add_seats(total_new, price, row, seat_type, event):
    """ Check the maximum capacity of event, then add seats"""
    total_event_seats = Seat.objects.all().filter(event=event).count()

    if total_new < 0:
        return False, "Can't add a negative number of seats"

    if total_event_seats + total_new <= event.max_capacity:
        # can add seats
        for number in range(total_new):
            seat = Seat(price=price, row=row, number=number, seat_type=seat_type, available=True,
                        event=event)
            seat.save()
        return True, f"Added {total_new} seats"
    else:
        return False, f"Max capacity exceeded"



class ManageSeat(LoginRequiredMixin, OrganizerRequiredMixin, EventOwnerMixin, View):
    event_profile = None
    event_id = None

    def get(self, request, **kwargs):
        seat_types = SeatType.objects.all()
        event_seats = Seat.objects.all().filter(event=self.event_profile)
        event_tickets = Ticket.objects.all().filter(seat__in=event_seats).order_by('seat__row','seat__number')

        context = {'event': self.event_profile, 'seat_types': seat_types, 'tickets':event_tickets}
        return render(request, 'book2fest/seat/create.html', context)

    def post(self, request, **kwargs):
        form = SeatForm(request.POST, request.FILES)

        if form.is_valid():
            total = form.cleaned_data.get('quantity')
            price = form.cleaned_data.get('price')
            row = form.cleaned_data.get('row')
            seat_type = form.cleaned_data.get('seat_type')

            flag, msg = add_seats(total, price, row, seat_type, self.event_profile)
            if flag:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
                return redirect(request.path_info)
        else:
            messages.error(request, form_validation_error(form))
            return redirect(request.path_info)

        return redirect('book2fest:event-detail', pk=kwargs.get('pk'))


from notifications.signals import notify
class EventCancel(ManageSeat):

    def get(self, request, **kwargs):

        if self.profile == self.event_profile.user:
            profiles = []
            tickets_users = Ticket.objects.filter(seat__event=self.event_profile).values_list('user')
            for id in tickets_users:
                profiles.append(UserProfile.objects.get(id=id[0]))

            if self.event_profile.cancelled:
                self.event_profile.cancelled = False
                self.event_profile.save()
                verb = 'Event AVAILABLE!'
                description = f'{self.event_profile.event_name} is now available!'

            else:
                self.event_profile.cancelled = True
                self.event_profile.save()
                verb = 'Event CANCELLED!'
                description = f'{self.event_profile.event_name} has been cancelled!'

            #retrieve all users that bought ticket for this event
            for profile in profiles:
                notify.send(profile.user, recipient=profile.user, verb=verb, description=description, target=self.event_profile)

        else:
            # show error you are not authorized
            messages.error(request, "You are not authorized!")

        return redirect("book2fest:manage-seat", pk=self.event_profile.pk)


class UserTicketList(LoginRequiredMixin, UserRequiredMixin, ListView):
    model = Ticket
    template_name = "book2fest/ticket/list.html"

    def get_context_data(self, *, object_list=None, **kwargs):

        context = super(UserTicketList, self).get_context_data(**kwargs)
        context['order_filters'] = ['event_name', 'event_start', 'price']
        return context

    def get_queryset(self):
        tickets = Ticket.objects.all().filter(user=self.profile)
        query = self.request.GET.get('search', None)
        filter = self.request.GET.get('search-filter', None)
        order = self.request.GET.get('order-filter', None)
        ordering = "seat__event__event_name"

        if order == "event_name":
            ordering = "seat__event__event_name"

        if order == "event_start":
            ordering = "seat__event__event_start"

        if order == "price":
            ordering = "seat__price"

        tickets = Ticket.objects.all().filter(user=self.profile).order_by(ordering)

        if query:

            if filter == "category":
                categories = Category.objects.all().filter(name__contains=query)
                genres = Genre.objects.all().filter(category__in=categories)
                artists = Artist.objects.all().filter(genre__in=genres)
                events = EventProfile.objects.all().filter(artist_list__in=artists)

            if filter == "genre":
                genres = Genre.objects.all().filter(name__contains=query)
                artists = Artist.objects.all().filter(genre__in=genres)
                events = EventProfile.objects.all().filter(artist_list__in=artists)

            if filter == "artist":
                artists = Artist.objects.all().filter(full_name__contains=query)
                events = EventProfile.objects.all().filter(artist_list__in=artists)

            if filter == "event_name":
                events = EventProfile.objects.all().filter(event_name__contains=query)

            seats = Seat.objects.all().filter(event__in=events)
            tickets = Ticket.objects.all().filter(seat__in=seats, user=self.profile).order_by(ordering).distinct()

        return tickets


class ManageTicket(LoginRequiredMixin, UserRequiredMixin, View):
    ticket = None
    review = None
    form = None

    def dispatch(self, request, *args, **kwargs):
        ticket_pk = kwargs.get('pk')
        try:
            self.ticket = Ticket.objects.get(pk=ticket_pk)
            self.review, __ = Review.objects.get_or_create(ticket=self.ticket)

        except ObjectDoesNotExist:
            # trying to access to a ticket that does not exist
            return redirect('homepage')  # TODO redirect to another page maybe

        return super(ManageTicket, self).dispatch(request, *args, **kwargs)

    def get(self, request, **kwargs):
        if self.ticket.user == self.profile:
            self.review = Review.objects.get(ticket=self.ticket)

            context = {'ticket': self.ticket, 'review': self.review}
            return render(request, "book2fest/ticket/manage.html", context)
        else:
            # user trying to manage not one of his tickets
            return redirect('homepage')  # TODO redirect to another page maybe

    def post(self, request, **kwargs):

        form = ReviewForm(request.POST, request.FILES, instance=self.review)

        if self.ticket.user == self.profile and form.is_valid():

            self.review.ticket = self.ticket
            self.review.rating = form.cleaned_data.get('rating')
            self.review.content = form.cleaned_data.get('content')
            self.review.date = date.today()
            self.review.save()

            messages.success(request, 'Ticket review successfully!')
        else:
            # user trying to review a ticket tha
            messages.error(request, form_validation_error(form))
        return redirect('book2fest:ticket-manage', self.ticket.pk)


class HomeView(ListView):
    model = EventProfile
    template_name = "book2fest/home.html"


    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        available = EventProfile.objects.filter(cancelled=False).filter(event_end__gt=date.today()).order_by('avg_rating')
        unavailable = EventProfile.objects.exclude(id__in=available).order_by('avg_rating')

        recommended = {}
        user_tickets = Ticket.objects.filter(user__user_id=self.request.user.id).values()  # ticket di eventi in cui è stato l'utente
        for i in range(len(user_tickets)):
            event_id = EventProfile.objects.filter(seat_event=user_tickets[i]['seat_id']).values()  # id evento al quale ha partecipato
            all_event_tickets = Ticket.objects.filter(seat__event_id=event_id[0]['id']).values()  # tutti i ticket relativi allo stesso evento
            for j in range(len(all_event_tickets)):
                users_tickets = Ticket.objects.filter(user=all_event_tickets[j]['user_id']).values()    # insieme di ticket per ogni possessore di ticket in all_event_tickets
                ticket_group = Ticket.objects.filter(user=users_tickets[0]['user_id']) # insieme di eventi per ogni possessore
                for ticket in ticket_group:
                    ev = EventProfile.objects.filter(seat_event__ticket_seat=ticket)
                    id = ev.values('id')[0]['id']
                    if id not in recommended.keys() and ev.filter(cancelled=False).filter(event_end__gt=date.today()):
                        recommended[id] = ev[0]

        context.update({"available":available[:5]})
        context.update({"unavailable":unavailable[:5]})
        context.update({"recommended":list(recommended.values())[:5]})
        return context