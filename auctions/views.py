from django.shortcuts import render
from .models import *

# Create your views here.
def home(request):
    auctions = Auction.objects.all()[:6]
    context = {
        'auctions': auctions
    }
    return render(request, 'auctions/home.html', context)

def loginPage(request):
    context = {
    }
    return render(request, 'auctions/login.html', context)

def registerPage(request):
    context = {
    }
    return render(request, 'auctions/register.html', context)

def shop(request):
    auctions = Auction.objects.all() 
    context = {
        'auctions': auctions
    }
    return render(request, 'auctions/shop.html', context)

def auctiondetail(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)

    context = {
        'auction': auction,
    }

    return render(request, 'auctions/auctiondetail.html', context)

def dashboard(request):
    context = {}
    return render(request, 'auctions/dashboard.html', context)

def profile(request):
    context = {}
    return render(request, 'auctions/profile.html', context)