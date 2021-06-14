from django.urls import path
from . import views
from .views import UserProfileView, OrganizerProfileView, CompleteRegistrationView, ArtistCreate, UserCreate, \
    OrganizerCreate, ArtistDetail

app_name = "book2fest"

urlpatterns=[
    path('complete-reg/', CompleteRegistrationView.as_view(), name='complete-reg'),
    path('user/create', UserCreate.as_view(), name='user-create'),
    path('user/profile', UserProfileView.as_view(), name='user-profile'),
    path('organizer/profile', OrganizerProfileView.as_view(), name='organizer-profile'),
    path('organizer/create', OrganizerCreate.as_view(), name='organizer-create'),
    path('artist/create', ArtistCreate.as_view(), name='artist-create'),
    path('artist/<int:pk>/detail', ArtistDetail.as_view(), name='artist-detail'),
]
