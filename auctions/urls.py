from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('<str:auction_id>/auctiondetail/', views.auctiondetail, name='auctiondetail'),
]