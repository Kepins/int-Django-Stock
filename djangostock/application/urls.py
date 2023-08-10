from django.urls import path

from .views import UserList, UserDetail, StockPrices

urlpatterns = [
    path("users/", UserList.as_view()),
    path("users/<int:pk>/", UserDetail.as_view()),
    path("stock/prices/", StockPrices.as_view()),
]
