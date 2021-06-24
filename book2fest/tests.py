from django.test import TestCase
from book2fest.models import EventProfile, OrganizerProfile, UserProfile, Ticket, Seat, SeatType, Delivery
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from book2fest.views import add_seats

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


    def book_ticket(self, event_id, seat, delivery):
        """ POST request to book a ticket"""

        # POST request to book a ticket
        response = self.client.post(
            reverse('book2fest:event-detail', kwargs={'pk': event_id}),
            data={'seat': seat.id,
                    'delivery': delivery.id,
                    'submit': ['Book']}
        )
        return response


    def test_book_ticket_when_event_cancelled(self):
        """ If user tries to book a seat when event is cancelled
        ->  Ticket not created and redirect to event-list page"""

        #create organizer to create an event with cancelled = True
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=0, cancelled=True)

        # create a seat for the event
        test_seat = create_seat(test_event, True)
        test_delivery = Delivery.objects.create(name="test-delivery", overprice=1.0, delivery_time=timedelta(days=2))

        response = self.book_ticket(event_id=test_event.id, seat=test_seat, delivery=test_delivery)

        self.assertEqual(response.status_code, 302) #should redirect to event-list page with message error
        self.assertEqual(response.url, reverse('book2fest:event-list'))  # check redirect url
        self.assertEqual(Ticket.objects.all().filter(seat=test_seat).exists(), False) #check if ticket has been created


    def test_book_ticket_when_event_past(self):
        """ If user tries to book an event that has already took place
        -> Ticket not created and redirect to event-list page"""

        # create organizer to create an event that has already took place (days=-10)
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=-10, cancelled=False)

        # create a seat for the event
        test_seat = create_seat(test_event, True)
        test_delivery = Delivery.objects.create(name="test-delivery", overprice=1.0, delivery_time=timedelta(days=2))

        response = self.book_ticket(event_id=test_event.id, seat=test_seat, delivery=test_delivery)

        self.assertEqual(response.status_code, 302)  # should redirect to event-list page with message error
        self.assertEqual(response.url, reverse('book2fest:event-list'))  # check redirect url
        self.assertEqual(Ticket.objects.all().filter(seat=test_seat).exists(), False)  # check if ticket has been created


    def test_book_ticket_when_seat_is_not_available(self):
        """ If user tries to book a seat that is not available
                -> Ticket not created and redirect to event-list with error message"""

        # create organizer to create an event in the future and not cancelled
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=10, cancelled=False)

        # create a seat NOT AVAILABLE for the event
        test_seat = create_seat(test_event,available=False)
        test_delivery = Delivery.objects.create(name="test-delivery", overprice=1.0, delivery_time=timedelta(days=2))

        response = self.book_ticket(event_id=test_event.id, seat=test_seat, delivery=test_delivery)

        self.assertEqual(response.status_code, 302)  # check redirect
        self.assertEqual(response.url,reverse('book2fest:event-list')) # check redirect url
        self.assertEqual(Ticket.objects.all().filter(seat=test_seat).exists(), False)  # check if ticket has been created


    def test_book_ticket_when_event_future_and_not_cancelled(self):
        """ If user tries to book an event in the future and not cancelled
                -> Ticket created and redirect to ticket page"""

        # create organizer to create an event in the future and not cancelled
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=10, cancelled=False)

        # create a seat for the event
        test_seat = create_seat(test_event, True)
        test_delivery = Delivery.objects.create(name="test-delivery", overprice=1.0, delivery_time=timedelta(days=2))

        response = self.book_ticket(event_id=test_event.id, seat=test_seat, delivery=test_delivery)

        self.assertEqual(response.status_code, 302)  # check redirect
        self.assertEqual(response.url,reverse('book2fest:ticket-manage',kwargs={'pk':1})) # check redirect url
        self.assertEqual(Ticket.objects.all().filter(seat=test_seat).exists(), True)  # check if ticket has been created


class AddSeatsTests(TestCase):

    def test_add_seats_with_negative_total_new(self):
        """ If try to add a negative number of seats
        -> Return False and do not add any seat"""

        # create organizer to create an event with cancelled = True
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=0, cancelled=True)

        # count number of seat before calling add_seats
        total_seat_before = Seat.objects.all().filter(event=test_event).count()

        val, __ = add_seats(total_new=-5, price=30.0, row="A", seat_type=SeatType.objects.create(name="test-seat-type"), event=test_event)

        # count number of seat after calling add_seats
        total_seat_after = Seat.objects.all().filter(event=test_event).count()

        self.assertEqual(val,False) # checks return value
        self.assertEqual(total_seat_before, total_seat_after) # checks that no seats have been added

    def test_add_seats_max_cap_exceed(self):
        """ If try to add number of seats that exceed the event max capacity
         -> Return False and do not add any seat"""

        # create organizer to create an event with cancelled = True
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=0, cancelled=True)

        # count number of seat before calling add_seats
        total_seat_before = Seat.objects.all().filter(event=test_event).count()

        val, __ = add_seats(total_new=12, price=30.0, row="A", seat_type=SeatType.objects.create(name="test-seat-type"), event=test_event)

        # count number of seat after calling add_seats
        total_seat_after = Seat.objects.all().filter(event=test_event).count()

        self.assertEqual(val,False) # checks return value
        self.assertEqual(total_seat_before, total_seat_after) # checks that no seats have been added

    def test_add_seats_positive_total_new_and_no_max_cap_exceed(self):
        """ If try to add positive number of seats that do not exceed the event max capacity
                 -> Return True and add correct amount of seats"""

        total_new = 8
        # create organizer to create an event with cancelled = True
        test_organizer = create_organizer(create_user("test-organizer", "test-pw"))
        test_event = create_event(user=test_organizer, max_capacity=10, seats_available=8, days=0, cancelled=True)

        # count number of seat before calling add_seats
        total_seat_before = Seat.objects.all().filter(event=test_event).count()

        val, __ = add_seats(total_new=total_new, price=30.0, row="A", seat_type=SeatType.objects.create(name="test-seat-type"), event=test_event)

        # count number of seat after calling add_seats
        total_seat_after = Seat.objects.all().filter(event=test_event).count()

        self.assertEqual(val,True) # checks return value
        self.assertEqual(total_seat_before+total_new, total_seat_after) # checks that the correct amount of seats have been added