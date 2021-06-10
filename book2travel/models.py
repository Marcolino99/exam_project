from cups import modelSort
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db.models.functions import datetime


class UserProfile(models.model):
    user = models.OneToOneField(User, related_name='user_profile', on_delete=models.CASCADE)
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Image(models.model):
    path = models.FilePathField()

class Service(models.model):
    name = models.CharField(max_length=32)
    description = models.TextField()
    icon = models.ForeignKey(Image, related_name='icon', on_delete=models.CASCADE)

class RoomType(models.model):
    name = models.CharField(max_length=32)

class StructureProfile(models.model):
    user = models.OneToOneField(User, related_name='structure_profile', on_delete=models.CASCADE)
    structure_name = models.CharField(max_length=60)
    city = models.CharField(max_length=32)
    country = models.CharField(max_length=32)
    address = models.CharField(max_length=32)
    rooms = models.IntegerField(max_length=4)
    services = models.ManyToManyField(Service)


class Rooms(models.model):
    structure = models.ForeignKey(StructureProfile, related_name='room_structure', on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    description = models.TextField()
    floor = models.IntegerField(max_length=3)
    number = models.CharField(max_length=4, blank=True)
    start_available = models.DateTimeField()
    end_available = models.DateTimeField()
    price_per_night = models.FloatField()
    room_type = models.ForeignKey(RoomType, related_name='room_type', on_delete=models.CASCADE)

class InterestedUser(models.model):
    room = models.ForeignKey(Rooms, related_name='interested_room', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name='interested_user', on_delete=models.CASCADE)

class Reservation(models.model):
    structure = models.ForeignKey(StructureProfile, related_name='reservation_structure', on_delete=models.CASCADE)
    user = models.ForeignKey(UserProfile, related_name="reservation_user", on_delete=models.CASCADE)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    guests_number = models.IntegerField()


class Review(models.model):
    writer = models.ForeignKey(UserProfile, related_name='writer', on_delete=models.CASCADE)
    rating = models.IntegerField(max_length=1)
    date = models.DateTimeField(default=datetime.now)
    content = models.TextField()
    structure = models.OneToOneField(StructureProfile, related_name='review_structure', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.structure_name}'


