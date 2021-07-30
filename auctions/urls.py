from django.urls import path
from . import views 

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.loginPage, name='login'),
    path('register/', views.registerPage, name='register'),
    path('logout/', views.logoutUser, name='logout'),
    path('shop/', views.shop, name='shop'),
    path('<int:auction_id>/auctiondetail/', views.auctiondetail, name='auctiondetail'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('<int:auction_id>/placebid/', views.placebid, name='placebid'),
    path('<int:auction_id>/bidhistory/', views.bidhistory, name='bidhistory'),
]

