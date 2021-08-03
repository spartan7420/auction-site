from django.db import reset_queries
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, request
from .models import *
from django.contrib.auth.forms import *
from .forms import *
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
            return redirect('home')
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
    profile = UserProfile.objects.get(user=request.user)
    context = {
        'profile': profile
    }
    return render(request, 'auctions/profile.html', context)

@login_required(login_url='login')
def editprofile(request):
    profile = UserProfile.objects.get(user=request.user)
    form = EditProfile(instance=profile)

    if request.method == 'POST':
        form = EditProfile(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            print(profile)
            messages.success(request, 'Your profile has been updated')
            return redirect('dashboard')
    context = {
        'form': form
    }
    return render(request, 'auctions/editprofile.html', context)

@login_required(login_url='login')
def placebid(request, auction_id):
    form = CreateBidForm()
    auction = Auction.objects.get(pk=auction_id)
    if auction.is_scheduled():
        messages.info(request, "Auction hasn't started yet!")
        return redirect('/' + str(auction_id) + '/auctiondetail')
    if auction.is_sold():
        messages.info(request, "Item has been sold!")
        return redirect('/' + str(auction_id) + '/auctiondetail')
    if auction.is_ended():
        messages.info(request, "Auction has ended")
        return redirect('/' + str(auction_id) + '/auctiondetail')

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
    bids = auction.bid_set.all().order_by('-created_at')
    context = {
        'auction': auction,
        'bids': bids
    }
    return render(request, 'auctions/viewbidhistory.html', context)

@login_required(login_url='login')
def createnewauction(request):
    form = CreateAuctionForm()

    if request.method == 'POST':
        form = CreateAuctionForm(request.POST)

        if form.is_valid():
            auction = form.save(commit=False)
            auction.user = request.user
            auction.save()
            images = request.FILES.getlist('image')
            print(images)
            for image in images:
                AuctionImage.objects.create(auction=auction, image=image)
            messages.success(request, 'Auction was created successfully!')
            return redirect('yourauctions')

    context = {
        'form': form
    }
    return render(request, 'auctions/createnewauction.html', context)


@login_required(login_url='login')
def yourauctions(request):
    auctions = Auction.objects.filter(user=request.user)
    context = {
        'auctions': auctions
    }
    return render(request, 'auctions/yourauctions.html', context)

@login_required(login_url='login')
def yourbids(request):
    user = request.user
    auctions = user.bid_set.all().distinct('auction')
    bids = []
    for entry in auctions:
        b = user.bid_set.filter(auction=entry.auction).latest('created_at')
        bids.append(b)

    context = {
        'bids': bids,
    }
    return render(request, 'auctions/yourbids.html', context)


@login_required(login_url='login')
def editauction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    if auction.is_scheduled:
        form = CreateAuctionForm(instance=auction)
        if request.method =='POST':
            form = CreateAuctionForm(request.POST, instance=auction)
            if form.is_valid():
                form.save()
                messages.success(request, 'Auction has been updated successfully')
                return redirect('yourauctions')
    else:
        messages.info(request, "An auction can't be edited if it has started")
    context = {
        'form': form
    }
    return render(request, 'auctions/editauction.html', context)


@login_required(login_url='login')
def deleteauction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    auction.delete()
    messages.success(request, 'Auction was deleted successfully')
    return redirect('yourauctions')

