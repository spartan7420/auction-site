from django.db import models
from django.db.models import CheckConstraint, Q, F
from django.contrib.auth.models import User
from django.utils import timezone
import pytz

# Create your models here.
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=400, blank=True)
    city = models.CharField(max_length=200, blank=True)
    state = models.CharField(max_length=200, blank=True)
    pincode = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=2, choices=pytz.country_names.items())
    date_of_birth = models.DateField()
    reputation = models.IntegerField(default=0)

    def __str__(self):
        return str(self.first_name)

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
        ('Scheduled', 'Scheduled'),
        ('Unsold', 'Unsold'),
        ('Sold', 'Sold'),
        ('Ended', 'Ended')
    )
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    category = models.CharField(max_length=200, null=True, choices=CATEGORY)
    title = models.CharField(max_length=200, null=True)
    description = models.TextField(max_length=1000, null=True)
    details = models.TextField(max_length=1000, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=200, choices=STATUS)
    opening_price = models.PositiveIntegerField(null=True)
    final_price = models.PositiveIntegerField(blank=True, null=True) 

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
                else:
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
    amount = models.PositiveIntegerField()
    created_at = models.DateTimeField()
 
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
    payment_amount = models.PositiveIntegerField()
    payment_method= models.CharField(max_length=200, null=True, choices=PAYMENT_METHOD)
    payment_status= models.CharField(max_length=200, null=True, choices=PAYMENT_STATUS, default='Pending')
    order_status= models.CharField(max_length=200, null=True, choices=ORDER_STATUS, default='Processing')
    created_at = models.DateTimeField()

    
    def __str__(self):
        return str(self.auction.title)
