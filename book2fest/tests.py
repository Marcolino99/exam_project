from django.test import TestCase
from book2fest.models import EventProfile, OrganizerProfile, UserProfile, Ticket, Seat, SeatType, Delivery
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse

def create_user(username, password):
    user = User.objects.create(username=username)
    user.set_password(password)
    user.save()
    return user


def create_organizer(user):
    return OrganizerProfile.objects.create(user=user, company="test-company", short_bio="test-short-bio")


def create_user_profile(user):
    return UserProfile.objects.create(user=user)


def create_event(user, max_capacity, seats_available, days, cancelled):
    date = timezone.now() + timedelta(days=days)
    return EventProfile.objects.create(user=user, max_capacity=max_capacity, seats_available=seats_available, event_start=date,
                                       event_end=date, cancelled=cancelled, avg_rating=2.5)

def create_seat(event, available):
    return Seat.objects.create(event=event, available=available, name="test-seat", row="A", number="1", price=12.0, seat_type=SeatType.objects.create(name="test-seat-type"))


class EventDetailTestCase(TestCase):

    def setUp(self):
        #create user profile
        test_user = create_user_profile(create_user("test-user-profile", "test-pw"))

        # disable csrf token
        self.client.enforce_csrf_checks = True

        # login user
        self.client.login(username=test_user.user.username, password="test-pw")

    def book_ticket(self, event, seat, delivery):

        # POST request to book a ticket
        response = self.client.post(
            reverse('book2fest:event-detail', kwargs={'pk': event.id}),
            data={'seat': seat.id,
                    'delivery': delivery.id,
                    'submit': ['Book']}
        )
        return response


    def test_book_ticket_when_event_cancelled(self):
        """ If user try to book a seat when event is cancelled
        ->  Ticket not created and redirect to event-list page"""

        #create organizer to create an event with cancelled = True
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=0, cancelled=True)

        # create a seat for the event
        test_seat = create_seat(test_event, True)
        test_delivery = Delivery.objects.create(name="test-delivery", overprice=1.0, delivery_time=timedelta(days=2))

        response = self.book_ticket(event=test_event, seat=test_seat, delivery=test_delivery)

        self.assertEqual(response.status_code, 302) #should redirect to event-list page with message error
        self.assertEqual(response.url, reverse('book2fest:event-list'))  # check redirect url
        self.assertEqual(Ticket.objects.all().filter(seat=test_seat).exists(), False) #check if ticket has been created


    def test_book_ticket_when_event_past(self):
        """ If user try to book an event that has already took place
        -> Ticket not created and redirect to event-list page"""

        # create organizer to create an event that has already took place (days=-10)
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=-10, cancelled=False)

        # create a seat for the event
        test_seat = create_seat(test_event, True)
        test_delivery = Delivery.objects.create(name="test-delivery", overprice=1.0, delivery_time=timedelta(days=2))

        response = self.book_ticket(event=test_event, seat=test_seat, delivery=test_delivery)

        self.assertEqual(response.status_code, 302)  # should redirect to event-list page with message error
        self.assertEqual(response.url, reverse('book2fest:event-list'))  # check redirect url
        self.assertEqual(Ticket.objects.all().filter(seat=test_seat).exists(), False)  # check if ticket has been created

    def test_book_ticket_when_event_future_and_not_cancelled(self):
        """ If user try to book an event in the future and not cancelled
                -> Ticket created and redirect to ticket page"""

        # create organizer to create an event in the future and not cancelled
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=10, cancelled=False)

        # create a seat for the event
        test_seat = create_seat(test_event, True)
        test_delivery = Delivery.objects.create(name="test-delivery", overprice=1.0, delivery_time=timedelta(days=2))

        response = self.book_ticket(event=test_event, seat=test_seat, delivery=test_delivery)

        print(response)
        print(response.context)

        self.assertEqual(response.status_code, 302)  # check redirect
        self.assertEqual(response.url,reverse('book2fest:ticket-manage',kwargs={'pk':1})) # check redirect url
        self.assertEqual(Ticket.objects.all().filter(seat=test_seat).exists(), True)  # check if ticket has been created
