from django.urls import path
from . import views
from .views import UserProfileView, EventDetailView


app_name = "book2fest"

urlpatterns=[
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('event/<int:pk>', EventDetailView.as_view(), name='event-details')
]

