from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop, name='shop'),
    path('<int:auction_id>/auctiondetail/', views.auctiondetail, name='auctiondetail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
]

