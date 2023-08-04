from django.http import Http404
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import UnauthenticatedPost, IsHimself, IsAdmin
from .models import User
from .serializers import UserSerializer


class UserList(APIView):
    """
    List all users, or create a new user.
    """

    permission_classes = [IsAdmin | UnauthenticatedPost]

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    """
    Retrieve, update or delete a user instance.
    """

    permission_classes = [IsAuthenticated & IsHimself]

    def get_object(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            self.check_object_permissions(request, user)
            return user
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(request, pk)
        self.check_object_permissions(request, user)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def patch(self, request, pk, format=None):
        user = self.get_object(request, pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(request, pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
