from django.urls import path
from . import views
from .views import UserProfileView

app_name = "book2fest"

urlpatterns=[
path('profile/', UserProfileView.as_view(), name='user-profile'),
]

