"""
Views for the user API
"""

# Create your views here.
from rest_framework import generics
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    # Create a new user in the systems
    serializer_class = UserSerializer
