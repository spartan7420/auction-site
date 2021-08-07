from decimal import Context
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from .models import *
from django.contrib.auth.forms import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user
from django.conf import settings
from django.contrib.auth.decorators import login_required
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
def set_currency(request):
    if not request.session.has_key('currency'):
        if request.user.is_authenticated:
            request.session['currency'] = request.user.userprofile.currency.code
        else:
            request.session['currency'] = settings.DEFAULT_CURRENCY
    return request


def home(request):
    request = set_currency(request)
    auctions = Auction.objects.all()[:6]
    context = {
        'auctions': auctions
    }
    return render(request, 'auctions/home.html', context)

def selectcurrency(request):
    if request.method == 'POST':
        lasturl = request.META.get('HTTP_REFERER')
        request.session['currency'] = request.POST['currency']
        if lasturl:
            return HttpResponseRedirect(lasturl)
        else:
            return redirect('home')


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
    if request.user.is_authenticated:
        if auction.buyrequest_set.filter(user=request.user).exists():
            buy_req = auction.buyrequest_set.get(user=request.user)
            context = {
                'auction': auction,
                'buy_req': buy_req
            }
            return render(request, 'auctions/auctiondetail.html', context)

    context = {
        'auction': auction,
    }
    return render(request, 'auctions/auctiondetail.html', context)

@login_required(login_url='login')
def dashboard(request):
    user = request.user
    if user.userprofile.stripe_account_id != None:
        stripe_account_link = stripe.AccountLink.create(
                    account=user.userprofile.stripe_account_id,
                    refresh_url='http://127.0.0.1:8000/dashboard',
                    return_url='http://127.0.0.1:8000/dashboard',
                    type='account_onboarding',
                )
        context = {
            'stripe_account_link': stripe_account_link
        }
        return render(request, 'auctions/dashboard.html', context)

    context = {

    }
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
            current_currency = Currency.objects.get(code=request.session['currency']).factor
            amount_default_curr = Decimal(form.cleaned_data.get('amount')) / current_currency
            if auction.has_bids():
                current_bid = auction.current_bid_price()
            else:
                current_bid = auction.opening_price

            if amount_default_curr > current_bid:
                bid = form.save(commit=False)
                bid.user = request.user
                bid.amount = amount_default_curr
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
def createbuyrequest(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    if request.method == 'POST' and request.POST['buy']:
        buy_request= BuyRequest()
        buy_request.user = request.user
        buy_request.auction = auction
        buy_request.save()
        messages.success(request, 'Buy request was placed successfully!')
        return redirect('/' + str(auction_id) + '/auctiondetail')

    context = {
        'auction': auction
    }
    return render(request, 'auctions/createbuyrequest.html', context)

@login_required(login_url='login')
def createnewauction(request):
    form = CreateAuctionForm()

    if request.method == 'POST':
        form = CreateAuctionForm(request.POST)
        current_currency = Currency.objects.get(code=request.session['currency']).factor
        if form.is_valid():
            auction = form.save(commit=False)
            opening_default_curr = Decimal(form.cleaned_data.get('opening_price')) / current_currency
            buy_default_curr = Decimal(form.cleaned_data.get('buy_price')) / current_currency
            auction.user = request.user
            auction.opening_price = opening_default_curr
            auction.buy_price = buy_default_curr
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
        if entry.auction.buyrequest_set.filter(user=user).exists():
            buy_req = entry.auction.buyrequest_set.get(user=request.user)
            b.buy_req = buy_req
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

@login_required(login_url='login')
def manageauction(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    bids = auction.bid_set.all().order_by('-created_at')

    context = {
        'auction': auction,
        'bids': bids
    }
    return render(request, 'auctions/manageauction.html', context)


@login_required(login_url='login')
def deletebid(request, bid_id):
    bid = Bid.objects.get(pk=bid_id)
    auction = bid.auction
    bid.delete()
    messages.success(request, 'Bid was deleted successfully')
    return redirect('/' + str(auction.id) + '/manageauction')

@login_required(login_url='login')
def rejectbuyrequest(request, buy_request_id):
    buy_req = BuyRequest.objects.get(pk=buy_request_id)
    buy_req.status = 'Rejected'
    buy_req.save()
    messages.success(request, 'Buy request was rejected successfully')
    return redirect('manageauction')

@login_required(login_url='login')
def endwithoutselling(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    auction.end_date = timezone.now()
    auction.save()
    messages.success(request, f"Auction ID {auction.id} has been ended successfully.")
    return redirect('yourauctions')

@login_required(login_url='login')
def endbyselling(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    auction.end_date = timezone.now()
    auction.status = 'Sold'
    auction.save()

    winner_user = auction.bid_set.latest('created_at').user
    Winner.objects.create(user=winner_user, auction=auction)

    messages.success(request, f"Auction ID {auction.id} has been sold to User ID {winner_user.id}.")
    return redirect('yourauctions')

@login_required(login_url='login')
def createstripeaccount(request):
    user = request.user
    if not user.userprofile.stripe_account_id:
        account = stripe.Account.create(
                    type='standard',
                )
        print(account)
        user.userprofile.stripe_account_id = account.id
        user.userprofile.save()

    return redirect('dashboard')

@login_required(login_url='login')
def checkout(request, auction_id):
    user = request.user
    auction = Auction.objects.get(pk=auction_id)
    if auction.winner.user == user:
        context = {
            'auction': auction
        }
        return render(request, 'auctions/checkout.html', context)
    else:
        return redirect('home')

@login_required(login_url='login')
def createcheckoutsession(request, auction_id):
    if request.method == 'POST':
        auction = Auction.objects.get(pk=auction_id)
        checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'name': auction.title,
            'amount': int(auction.current_bid_price() * 100),
            'currency': 'inr',
            'quantity': 1,
        }],
        payment_intent_data={
            'application_fee_amount': 123 * 100,
            'transfer_data': {
            'destination': auction.user.userprofile.stripe_account_id,
            },
        },
        mode='payment',
        success_url='http://127.0.0.1:8000/success',
        cancel_url='http://127.0.0.1:8000/failure',
        )
        url = checkout_session.url
        print(checkout_session)
        return redirect(url)
    return redirect('/' + str(auction_id) + '/checkout')

@login_required(login_url='login')
def success(request):
    context = {
    }
    return render(request, 'auctions/success.html', context)

@login_required(login_url='login')
def failure(request):
    context = {
    }
    return render(request, 'auctions/failure.html', context)

@login_required(login_url='login')
def orders(request):
    context = {
    }
    return render(request, 'auctions/orders.html', context)