from django.urls import path

from .views import UserList, UserDetail, StockPrices, StockFollow, Home, StockRequest

urlpatterns = [
    path("users/", UserList.as_view()),
    path("users/<int:pk>/", UserDetail.as_view()),
    path("stock/prices/", StockPrices.as_view()),
    path("stock/follow/", StockFollow.as_view()),
    path("stock/request/", StockRequest.as_view()),
    path("home/", Home.as_view()),
]
