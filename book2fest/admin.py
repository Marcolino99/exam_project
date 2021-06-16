from django.contrib import admin
from book2fest.models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(EventProfile)
admin.site.register(Service)
admin.site.register(Artist)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Image)
admin.site.register(Picture)
admin.site.register(ServiceImage)
admin.site.register(Ticket)
admin.site.register(Seat)
admin.site.register(SeatType)
admin.site.register(Delivery)