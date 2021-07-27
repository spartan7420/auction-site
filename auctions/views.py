from django.shortcuts import render

# Create your views here.
def home(request):
    title = "Home"
    context = {'title':title}
    return render(request, 'auctions/home.html', context)

def shop(request):
    title = "All Auctions"
    context = {'title':title}
    return render(request, 'auctions/shop.html', context)

def auctiondetail(request, auction_id):
    title = "Details"
    context = {'title':title}
    return render(request, 'auctions/auctiondetail.html', context)

def dashboard(request):
    title = "Dashboard"
    context = {'title':title}
    return render(request, 'auctions/dashboard.html', context)

def profile(request):
    title = "Profile"
    context = {'title':title}
    return render(request, 'auctions/profile.html', context)