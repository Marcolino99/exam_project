from django.urls import path
from . import views
from .views import UserProfileView, OrganizerProfileView, CompleteRegistrationView, ArtistCreate, UserCreate, \
    OrganizerCreate, EventCreate, EventUpdate, EventDetail, EventList, ManageSeat, UserTicketList, ManageTicket, \
    EventCancel, ArtistList, SeatTypeCreate

app_name = "book2fest"

urlpatterns=[
    path('complete-reg/', CompleteRegistrationView.as_view(), name='complete-reg'),
    path('user/create', UserCreate.as_view(), name='user-create'),
    path('user/profile', UserProfileView.as_view(), name='user-profile'),
    path('organizer/profile', OrganizerProfileView.as_view(), name='organizer-profile'),
    path('organizer/create', OrganizerCreate.as_view(), name='organizer-create'),
    path('event/create', EventCreate.as_view(), name='event-create' ),
    path('event/<int:pk>/detail', EventDetail.as_view(), name='event-detail'),
    path('event/list', EventList.as_view(), name='event-list'),
    path('artist/create', ArtistCreate.as_view(), name='artist-create'),
    path('artist/list', ArtistList.as_view(), name='artist-list'),
    # path('artist/<int:pk>/detail', ArtistDetail.as_view(), name='artist-detail'),
    path('event/<int:pk>/manage-seat', ManageSeat.as_view(), name='manage-seat' ),
    path('event/<int:pk>/cancel', EventCancel.as_view(), name='event-cancel'),
    path('event/<int:pk>/update', EventUpdate.as_view(), name='event-update'),
    path('ticket/list', UserTicketList.as_view(), name='ticket-list' ),
    path('ticket/<int:pk>/manage', ManageTicket.as_view(), name='ticket-manage'),
    path('seat-type/create', SeatTypeCreate.as_view(), name='seat-type-create')
]
