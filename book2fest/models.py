from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import User
from django.db.models import IntegerField, When, Count, Case, Sum
from django.db.models.functions import datetime
from django.template.defaulttags import register
from django.utils.datetime_safe import date


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
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'


class Genre(models.Model):
    name = models.CharField(max_length=32)
    category = models.ForeignKey(Category, related_name='genre_category', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Artist(models.Model):
    full_name = models.CharField(max_length=32)
    image = models.ImageField(upload_to='images/')
    genre = models.ForeignKey(Genre, related_name='artist_genre', on_delete=models.CASCADE)

    def __str__(self):
        return self.full_name


class Delivery(models.Model):
    name = models.CharField(max_length=32)
    overprice = models.FloatField()
    delivery_time = models.DurationField()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name_plural = 'Deliveries'


class ServiceImage(models.Model):
    path = models.FileField(upload_to="services", validators=[FileExtensionValidator(['svg'])])

    def __str__(self):
        return f'{self.path.name.split("/")[-1]}'

class Service(models.Model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    icon = models.OneToOneField(ServiceImage, related_name='icon', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.name} - {self.description}'

class EventProfile(models.Model):
    user = models.ForeignKey(OrganizerProfile, related_name='event_user', on_delete=models.CASCADE)
    event_name = models.CharField(max_length=60)
    brief_description = models.TextField()
    description = models.TextField()
    artist_list = models.ManyToManyField(Artist)
    city = models.CharField(max_length=32)
    province = models.CharField(max_length=2)
    cap = models.CharField(max_length=5)
    country = models.CharField(max_length=32)
    address = models.CharField(max_length=32)
    how_to_reach = models.CharField(max_length=300)
    max_capacity = models.IntegerField()
    seats_available = models.IntegerField(default=None, blank=True, null=True)
    avg_rating = models.FloatField(default=None, blank=True, null=True)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    services = models.ManyToManyField(Service)
    cancelled = models.BooleanField(default=False)

    @property
    def is_past(self):
        return date.today() > self.event_end

    @register.filter(name='subtract')
    def subtract(value, arg):
        return value - arg

    def __str__(self):
        return f'{self.event_name} - {self.event_start.year}'



class Picture(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=200)
    img = models.ImageField(upload_to='pictures/')
    event = models.ForeignKey(EventProfile, related_name='pictures', on_delete=models.PROTECT)

    def __str__(self):
        return self.name


class SeatType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Seat(models.Model):
    event = models.ForeignKey(EventProfile, related_name='seat_event', on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    row = models.CharField(max_length=1, blank=True)
    number = models.CharField(max_length=4, blank=True)
    price = models.FloatField()
    available = models.BooleanField(default=True)
    seat_type = models.ForeignKey(SeatType, related_name='seat_type', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.event}: {self.seat_type.name} #{self.number} on row {self.row}'


class Ticket(models.Model):
    seat = models.OneToOneField(Seat, related_name='ticket_seat', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name="ticket_user", on_delete=models.CASCADE)
    delivery = models.ForeignKey(Delivery, related_name='ticket_delivery', on_delete=models.CASCADE)


class Review(models.Model):
    rating = models.FloatField(null=True)
    date = models.DateTimeField(default=datetime.Now())
    content = models.TextField(null=True)
    ticket = models.OneToOneField(Ticket, related_name='review_structure', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.ticket.seat.event.event_name}-{self.rating}'


