from django.contrib import admin
from book2fest.models import Artist, OrganizerProfile, UserProfile, Genre, Category, EventProfile, Service, SeatType, \
    ServiceImage, Seat, Delivery, Ticket, Review

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(OrganizerProfile)
admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(EventProfile)
admin.site.register(Service)
admin.site.register(SeatType)
admin.site.register(Seat)
admin.site.register(ServiceImage)
admin.site.register(Delivery)
admin.site.register(Ticket)
admin.site.register(Review)
