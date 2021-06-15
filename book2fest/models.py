from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db.models.functions import datetime


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'

class OrganizerProfile(models.Model):
    user = models.OneToOneField(User, related_name='organizer_user_profile', on_delete=models.CASCADE)
    company = models.CharField(max_length=32)
    short_bio = models.CharField(max_length=300)

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'




class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.name}'

class Genre(models.Model):
    name = models.CharField(max_length=32)
    category = models.ForeignKey(Category, related_name='genre_category', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name}'


class Artist(models.Model):
    full_name = models.CharField(max_length=32)
    genre = models.ForeignKey(Genre, related_name='artist_genre', on_delete=models.CASCADE)
    path = models.FilePathField(path='static/images/artist', default='static/images/default.png')

    def __str__(self):
        return f'{self.full_name}'


class Delivery(models.Model):
    name = models.CharField(max_length=32)
    overprice = models.FloatField()
    delivery_time = models.DurationField()   #TODO forse meglio mettere un datetime field boh

    def __str__(self):
        return f'{self.name}'

class Service(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    path = models.FilePathField(path='static/images/icon', default='static/images/default.png')

    def __str__(self):
        return f'{self.name} - {self.description}'


class EventProfile(models.Model):
    user = models.OneToOneField(OrganizerProfile, related_name='event_user', on_delete=models.CASCADE)
    event_name = models.CharField(max_length=60)
    artist_list = models.ManyToManyField(Artist)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=32)
    address = models.CharField(max_length=32)
    max_capacity = models.IntegerField(max_length=4)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    services = models.ManyToManyField(Service)      # An event has many services, a service can be offered by many events (m to n)

    def __str__(self):
        return f'{self.event_name} - {self.event_start.year}'


class SeatType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.name}'


class Seat(models.Model):
    event = models.ForeignKey(EventProfile, related_name='seat_event', on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    row = models.CharField(max_length=1, blank=True)
    number = models.CharField(max_length=4, blank=True)
    price = models.FloatField()
    available = models.BooleanField(default=True)
    seat_type = models.ForeignKey(SeatType, related_name='seat_type', on_delete=models.CASCADE)


class Ticket(models.Model):
    seat = models.ForeignKey(Seat, related_name='ticket_seat', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name="ticket_user", on_delete=models.CASCADE)
    delivery = models.ForeignKey(Delivery, related_name='ticket_delivery', on_delete=models.CASCADE)

# class InterestedUser(models.Model):
#     # room = models.ForeignKey(Seat, related_name='interested_room', on_delete=models.CASCADE)
#     user = models.ForeignKey(UserProfile, related_name='interested_user', on_delete=models.CASCADE)

# class Review(models.Model):
#     writer = models.ForeignKey(UserProfile, related_name='writer', on_delete=models.CASCADE)
#     rating = models.IntegerField(max_length=1)
#     date = models.DateTimeField(default=datetime.Now())
#     content = models.TextField()
#     structure = models.OneToOneField(EventProfile, related_name='review_structure', on_delete=models.CASCADE)
#
#     def __str__(self):
#         return f'{self.structure_name}'


