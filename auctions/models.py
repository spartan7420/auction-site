from datetime import datetime
from django.db import models
from django.db.models import CheckConstraint, Q, F
from currencies.models import Currency
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Max
from decimal import Decimal
import pytz

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=200, blank=True, null=True)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=200, blank=True, null=True)
    address = models.CharField(max_length=400, blank=True, null=True)
    city = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    country = models.CharField(max_length=2, choices=pytz.country_names.items(), null=True)
    date_of_birth = models.DateField(null=True)
    reputation = models.IntegerField(default=0)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, null=True, blank=True)

    def bid_count(self):
        auctions = self.user.bid_set.all().distinct('auction')
        bids = []
        for entry in auctions:
            b = self.user.bid_set.filter(auction=entry.auction).latest('created_at')
            bids.append(b)
        
        return len(bids)

    def auction_count(self):
        return Auction.objects.filter(user=self.user).count()
    
    def win_count(self):
        return Winner.objects.filter(user=self.user).count()

    def __str__(self):
        return str(self.user)

def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_profile, sender=User)

def update_profile(sender, instance, created, **kwargs):
    if created == False:
        instance.userprofile.save()

post_save.connect(update_profile, sender=User)


class Auction(models.Model):
    CATEGORY = (
        ('Mobiles & Electronics', 'Mobiles & Electronics'),
        ('Apparel', 'Apparel'),
        ('Furniture', 'Furniture'),
        ('Vehicles & Accessories', 'Vehicles & Accessories'),
        ('Sports', 'Sports'),
        ('Entertainment', 'Entertainment'),
        ('Home & Garden', 'Home & Garden'),
    )
    STATUS = (
        ('Unsold', 'Unsold'),
        ('Sold', 'Sold'),
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=1000, null=True)
    details = models.TextField(max_length=1000, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=200, choices=STATUS, default='Unsold')
    opening_price = models.DecimalField(        
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True)
    buy_price = models.DecimalField(        
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True)

    def time_left(self):
        now = timezone.now()
        if(self.end_date > now):
            time_left = self.end_date - now   
            #Extract days, hours, min from timedelta object
            time_left = str(time_left).split(',')
            if len(time_left) == 2:
                day = time_left[0].split(' ')[0].strip()
                clock = time_left[1].split(':')
                hour = clock[0].strip()
                min = clock[1].strip()
                sec = clock[2][:2].strip()
                
                if int(day) < 10 and int(day) >= 0:
                    day = '0' + day 
                if int(hour) < 10:
                    hour = '0' + hour 

                result = {
                    'day': day,
                    'hour': hour,
                    'min': min,
                    'sec': sec
                }
                return result
            elif len(time_left) == 1:
                clock = time_left[0].split(':')
                hour = clock[0].strip()
                min = clock[1].strip()
                sec = clock[2][:2].strip()
                day = '00'

                if int(hour) < 10:
                    hour = '0' + hour 

                result = {
                    'day': day,
                    'hour': hour,
                    'min': min,
                    'sec': sec
                }
                return result  
        else:
            result = {
                'day': '00',
                'hour': '00',
                'min': '00',
                'sec': '00'
            }
            return result   

    def time_until_start(self):
        now = timezone.now()
        if(self.end_date > now):
            time_left = self.start_date - now  
            #Extract days, hours, min from timedelta object
            time_left = str(time_left).split(',')
            if len(time_left) == 2:
                day = time_left[0].split(' ')[0].strip()
                clock = time_left[1].split(':')
                hour = clock[0].strip()
                min = clock[1].strip()
                sec = clock[2][:2].strip()
                
                if int(day) < 10 and int(day) >= 0:
                    day = '0' + str(day) 
                if int(hour) < 10:
                    hour = '0' + str(hour) 

                result = {
                    'day': day,
                    'hour': hour,
                    'min': min,
                    'sec': sec
                }
                return result
            elif len(time_left) == 1:
                clock = time_left[0].split(':')
                hour = clock[0].strip()
                min = clock[1].strip()
                sec = clock[2][:2].strip()
                day = '00'

                if int(hour) < 10:
                    hour = '0' + str(hour) 

                result = {
                    'day': day,
                    'hour': hour,
                    'min': min,
                    'sec': sec
                }
                return result  
        else:
            result = {
                'day': '00',
                'hour': '00',
                'min': '00',
                'sec': '00'
            }
            return result   

    def current_bid_price(self):
        return self.bid_set.all().aggregate(Max('amount'))['amount__max']

    def is_scheduled(self):
        """
        Returns True if the current date-time is less than the 
        start date-time of the auction
        """
        return timezone.now() < self.start_date
        
    def has_bids(self):
        """
        Returns true if an auction has atleast 1 bid
        """
        return self.bid_set.all().count() > 0

    def is_started(self):
        """
        Returns True if the auction is live
        """
        return self.start_date <= timezone.now() <= self.end_date

    def is_sold(self):
        """
        Returns True of the value of status field is equal to 'Sold'
        """
        return self.status == 'Sold'

    def is_ended(self):
        """
        Returns True of the value of current date-time is 
        greater than the end_date field
        """
        return (timezone.now() > self.end_date)

    def __str__(self):
        return str(self.title)

    class Meta:
        constraints = [
            CheckConstraint(
                check = Q(end_date__gt=F('start_date')), 
                name = 'check_start_date',
            ),
        ]

def generate_filename(instance, filename):
    import datetime

    time_now  = datetime.datetime.now().strftime('%m_%d_%Y_%H_%M_%S') 
    filebase, extension = filename.split('.')
    filebase = str(filebase) + str(time_now)
    return 'images/%s.%s' % (filebase, extension)

class AuctionImage(models.Model):
    auction = models.ForeignKey(Auction, on_delete=models.CASCADE)
    image = models.ImageField(blank=True, null=True, upload_to=generate_filename)

    def __str__(self):
        return str(self.auction.title)

class Winner(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    auction = models.OneToOneField(Auction, null=True, on_delete=models.SET_NULL)
    
class Bid(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    auction = models.ForeignKey(Auction, null=True, on_delete=models.SET_NULL)
    amount = models.DecimalField(        
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BuyRequest(models.Model):
    STATUS = (
        ('Waiting', 'Waiting'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    auction = models.ForeignKey(Auction, null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=200, choices=STATUS, default='Waiting')
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    auction = models.OneToOneField(Auction, null=True, on_delete=models.SET_NULL)
    PAYMENT_METHOD = (
        ('Cash On Delivery', 'Cash On Delivery'),
        ('UPI', 'UPi'),
        ('Net Banking', 'Net Banking')
    )
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid')
    )
    ORDER_STATUS = (
        ('Processing', 'Processing'),
        ('Transit', 'Transit'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered')
    )
    payment_amount = models.DecimalField(        
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))], null=True, blank=True)
    payment_method= models.CharField(max_length=200, null=True, choices=PAYMENT_METHOD)
    payment_status= models.CharField(max_length=200, null=True, choices=PAYMENT_STATUS, default='Pending')
    order_status= models.CharField(max_length=200, null=True, choices=ORDER_STATUS, default='Processing')
    created_at = models.DateTimeField()

    
    def __str__(self):
        return str(self.auction.title)
