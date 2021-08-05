from auctions.models import UserProfile
from django.contrib import admin
from .models import *

# Register your models here.
class AuctionImageInline(admin.StackedInline):
    model = AuctionImage
    extra = 3

class AuctionAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'status', 'opening_price', 'buy_price')
    inlines = [AuctionImageInline]

admin.site.register([UserProfile, Bid, Order, Winner, BuyRequest])
admin.site.register(Auction, AuctionAdmin)
