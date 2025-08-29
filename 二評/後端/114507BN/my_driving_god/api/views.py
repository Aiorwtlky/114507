from rest_framework import generics
from .models import Personnel
from .serializers import PersonnelSerializer

class PersonnelListAPIView(generics.ListAPIView):
    """
    A read-only API endpoint that provides a list of all active personnel.
    
    - generics.ListAPIView has built-in logic to handle GET requests and return a list of objects.
    - We only need to tell it two things:
      1. queryset: The data to be retrieved.
      2. serializer_class: The serializer to be used for converting the data to JSON.
    """
    queryset = Personnel.objects.filter(is_active=True).order_by('personnel_number')
    serializer_class = PersonnelSerializer