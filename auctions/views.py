from django.shortcuts import render, redirect
from .models import *
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# Create your views here.
def home(request):
    auctions = Auction.objects.all()[:6]
    context = {
        'auctions': auctions
    }
    return render(request, 'auctions/home.html', context)

def loginPage(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {
    }
    return render(request, 'auctions/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account was created successfully!')
            return redirect('login')

    context = {
        'form': form
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