from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import *
from django.contrib.auth.forms import *
from .forms import CreateBidForm, CreateUserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    auctions = Auction.objects.all()[:6]
    context = {
        'auctions': auctions
    }
    return render(request, 'auctions/home.html', context)

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(request.POST.get('next'))
        else:
            messages.info(request, 'Username or Password is incorrect')

    context = {
    }
    return render(request, 'auctions/login.html', context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return redirect('home')

@unauthenticated_user
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

@login_required(login_url='login')
def dashboard(request):
    context = {}
    return render(request, 'auctions/dashboard.html', context)

@login_required(login_url='login')
def profile(request):
    context = {}
    return render(request, 'auctions/profile.html', context)

@login_required(login_url='login')
def placebid(request, auction_id):
    form = CreateBidForm()
    auction = Auction.objects.get(pk=auction_id)

    if request.method == 'POST':
        form = CreateBidForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('amount') > auction.current_bid_price():
                bid = form.save(commit=False)
                bid.user = request.user
                bid.auction = Auction.objects.get(pk=auction_id)
                bid.save()
                messages.success(request, 'Bid was placed successfully!')
                return redirect('/' + str(auction_id) + '/auctiondetail')
            else:
                messages.info(request, 'New bid price must be greater than the current bid price')

    context = {
        'form': form,
        'auction': auction
    }
    return render(request, 'auctions/placebid.html', context)

def bidhistory(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    context = {
        'auction': auction
    }
    return render(request, 'auctions/viewbidhistory.html', context)
