from django.db.models import OuterRef, Subquery, Max
from django.http import Http404
from django.shortcuts import render
from django.views import View
from rest_framework import status
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .auth import UnauthenticatedPost, IsHimself, IsAdmin
from .models import User, Stock, StockTimeSeries, Follow
from .serializers import UserSerializer, StockSerializer, FollowSerializer


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


class StockPricePagination(PageNumberPagination):
    page_size = 20


class StockPrices(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Stock.objects.filter(last_update_date__isnull=False)
    serializer_class = StockSerializer
    pagination_class = StockPricePagination

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        latest_volume_subquery = (
            StockTimeSeries.objects.filter(stock=OuterRef("pk")).order_by("-recorded_date").values("volume")[:1]
        )

        # TODO THIS SHOULD ALSO WORK
        # latest_volume_subquery = (
        #     StockTimeSeries.objects.filter(stock=OuterRef("pk"))
        #     .get(recorded_date="stock__last_update_date")
        #     .values("volume")[:1]
        # )

        # Query to retrieve stocks along with the latest volume and order by volume
        stocks_ordered_by_latest_volume = queryset.annotate(latest_volume=Subquery(latest_volume_subquery)).order_by(
            "-latest_volume"
        )

        page = self.paginate_queryset(stocks_ordered_by_latest_volume)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(stocks_ordered_by_latest_volume, many=True)
        return Response(serializer.data)


class StockFollow(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        data = request.data
        data["user"] = request.user.pk
        serializer = FollowSerializer(data=data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, format=None):
        try:
            follow = Follow.objects.get(user=request.user, stock_id=request.data["stock"])
        except Follow.DoesNotExist as e:
            return Response({"error": "Not following."}, status=status.HTTP_404_NOT_FOUND)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Home(APIView):
    """This view would need some proper js that adds header with Bearer token"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        context = {"stocks": request.user.follows.all()}

        return render(request, "home.html", context)
