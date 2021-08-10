from decimal import Context
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse, response
from .models import *
from django.contrib.auth.forms import *
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .decorators import unauthenticated_user
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage
import stripe
import requests 

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
    try:
        request = set_currency(request)
        auctions = Auction.objects.all()[:6]
        context = {
            'auctions': auctions
        }
        return render(request, 'auctions/home.html', context)
    except:
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
    p = Paginator(auctions, 20)

    page_num = request.GET.get('page', 1)

    try: 
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)

    context = {
        'auctions': page
    }
    return render(request, 'auctions/shop.html', context)

def category_list(request):
    categories = Category.objects.all().order_by('category')
    context = {
        'categories': categories
    }
    return context

def auctionsbycategory(request, category_slug):
    category = Category.objects.get(slug=category_slug)
    auctions = category.auction_set.all()

    p = Paginator(auctions, 20)

    page_num = request.GET.get('page', 1)

    try: 
        page = p.page(page_num)
    except EmptyPage:
        page = p.page(1)

    context = {
        'auctions': page,
        'category': category
    }
    return render(request, 'auctions/auctionsbycategory.html', context)


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
        url = f'https://api.stripe.com/v1/accounts/{user.userprofile.stripe_account_id}'
        header = {
            'Authorization': f'Bearer {settings.STRIPE_SECRET_KEY}'
        }
        r = requests.get(url=url, headers=header)
        response = r.json() 
        
        #Send onboarding link if it's not completed
        if not response['charges_enabled']:
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
        else:
            context = {
                'onboarded': True
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

    for buy_req in BuyRequest.objects.all():
        if buy_req.user == user:
            buy_req.buy_req = buy_req
            bids.append(buy_req)

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
    try:
        if auction.order:
            form = EditOrderStatus(instance=auction.order)

            if request.method == 'POST':
                form = EditOrderStatus(request.POST, instance=auction.order)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Order status was updated successfully.')
                    return redirect('/' + str(auction_id) + '/manageauction')

            context = {
                'auction': auction,
                'bids': bids,
                'form': form
            }
            return render(request, 'auctions/manageauction.html', context)
    except:
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
def endbysellrequest(request, auction_id, buyer_id):
    user = User.objects.get(pk=buyer_id)
    auction = Auction.objects.get(pk=auction_id)
    auction.end_date = timezone.now()
    auction.status = 'Sold'
    auction.buyrequest_set.get(user=user).status = 'Accepted'
    auction.buyrequest_set.get(user=user).save()
    auction.save()

    Winner.objects.create(user=user, auction=auction)

    messages.success(request, f"Auction ID {auction.id} has been sold to User ID {user.id}.")
    return redirect('/' + str(auction.id) + '/manageauction')

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
def selectpaymentmethod(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)

    if request.method == 'POST':
        paymethod = request.POST.get('paymethod')
        return redirect(f'/{auction.id}/checkout/{paymethod}')
        
    context = {
        'auction': auction
    }
    return render(request, 'auctions/selectpaymentmethod.html', context)

@login_required(login_url='login')
def checkout(request, auction_id, payment_method):
    user = request.user
    auction = Auction.objects.get(pk=auction_id)
    if auction.winner.user == user:
        if auction.buyrequest_set.get(user=user).status == 'Accepted':
            price = auction.buy_price
            shipping = Decimal()

            if not auction.shipping_price:
                shipping = 0
            else:
                shipping = auction.shipping_price 
            total = str(price + shipping)

            context = {
                'auction': auction,
                'payment_method': payment_method,
                'total': total,
                'buyreq': True
            }
            return render(request, 'auctions/checkout.html', context)
        else:
            price = auction.current_bid_price()
            shipping = Decimal()

            if not auction.shipping_price:
                shipping = 0
            else:
                shipping = auction.shipping_price 
            total = str(price + shipping)

            context = {
                'auction': auction,
                'payment_method': payment_method,
                'total': total
            }
            return render(request, 'auctions/checkout.html', context)
    else:
        return redirect('home')

@login_required(login_url='login')
def createcheckoutsession(request, auction_id):
    user = request.user
    auction = Auction.objects.get(pk=auction_id)
    payment_method = 'Debit Card/Credit Card'
    buy_req = False
    total = 0
    current_currency = Currency.objects.get(code=request.session['currency']).factor
    if auction.buyrequest_set.get(user=user).status == 'Accepted':
        price = auction.buy_price * current_currency
        shipping = Decimal()
        if not auction.shipping_price:
            shipping = 0
        else:
            shipping = auction.shipping_price * current_currency 
        total = price + shipping
        Order.objects.create(user=user, auction=auction, payment_amount=total, payment_method=payment_method)
        buy_req = True
    else:
        price = auction.current_bid_price() * current_currency
        shipping = Decimal()

        if not auction.shipping_price:
            shipping = 0
        else:
            shipping = auction.shipping_price * current_currency
        total = price + shipping
        Order.objects.create(user=user, auction=auction, payment_amount=total, payment_method=payment_method)

    if request.method == 'POST':
        if buy_req:
            auction = Auction.objects.get(pk=auction_id)
            checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'name': auction.title,
                'amount': int(total * 100),
                'currency': request.session['currency'].lower(),
                'quantity': 1,
            }],
            payment_intent_data={
                'application_fee_amount': 123 * 100,
                'transfer_data': {
                'destination': auction.user.userprofile.stripe_account_id,
                },
            },
            mode='payment',
            success_url=f'http://127.0.0.1:8000/{auction.id}/success',
            cancel_url=f'http://127.0.0.1:8000/{auction.id}/failure',
            )
            url = checkout_session.url
            print(checkout_session)
            return redirect(url)
        else:
            auction = Auction.objects.get(pk=auction_id)
            checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'name': auction.title,
                'amount': int(total * 100),
                'currency': request.session['currency'].lower(),
                'quantity': 1,
            }],
            payment_intent_data={
                'application_fee_amount': 123 * 100,
                'transfer_data': {
                'destination': auction.user.userprofile.stripe_account_id,
                },
            },
            mode='payment',
            success_url=f'http://127.0.0.1:8000/{auction.id}/success',
            cancel_url=f'http://127.0.0.1:8000/{auction.id}/failure',
            )
            url = checkout_session.url
            print(checkout_session)
            return redirect(url) 
    return redirect('/' + str(auction_id) + '/checkout')

@login_required(login_url='login')
def success(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    try:
        if auction.order.user == 'user':
            auction.order.payment_status = 'Paid'
            auction.order.save()
            context = {
            }
            return render(request, 'auctions/success.html', context)
        else:
            return redirect('home')
    except: 
        return redirect('home')


@login_required(login_url='login')
def failure(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    try:
        if auction.order.user == 'user':
            context = {
            }
            return render(request, 'auctions/failure.html', context)
        else: 
            return redirect('home')
    except:
        return redirect('home')


@login_required(login_url='login')
def orders(request):
    user = request.user
    orders = user.order_set.all()
    context = {
        'orders': orders
    }
    return render(request, 'auctions/orders.html', context)

@login_required(login_url='login')
def orderinfo(request, order_id):
    order = Order.objects.get(pk=order_id)
    context = {
        'order': order
    }
    return render(request, 'auctions/orderinfo.html', context)

def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        auctions = list(Auction.objects.filter(title__icontains=query).values())

        return JsonResponse(auctions, safe=False)

def searchresults(request):
    if 'query' in request.GET:
        query = request.GET['query']
        auctions = Auction.objects.filter(title__icontains=query)
        context = {
            'auctions': auctions,
            'query': query
        }
        return render(request, 'auctions/searchresults.html', context)
    else: 
        context = {
        }
        return render(request, 'auctions/searchresults.html', context)



