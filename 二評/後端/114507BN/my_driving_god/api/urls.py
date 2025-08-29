from django.urls import path
from .views import PersonnelListAPIView

urlpatterns = [
    path('personnel/', PersonnelListAPIView.as_view(), name='personnel-list'),
]