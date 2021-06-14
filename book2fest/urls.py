from django.urls import path
from . import views
from .views import UserProfileView, OrganizerProfileView, ChooseProfileView, ArtistCreate

app_name = "book2fest"

urlpatterns=[
    path('choose-profile', ChooseProfileView.as_view(), name='choose-profile'),
    path('user/profile', UserProfileView.as_view(), name='user-profile'),
    path('organizer/profile', OrganizerProfileView.as_view(), name='organizer-profile'),
    path('artist/create', ArtistCreate.as_view(), name='artist-create')
]

