from django.db import models
from django.contrib.auth.models import User
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





