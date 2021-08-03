from django.forms import ModelForm, widgets
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class CreateBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

class CreateAuctionForm(ModelForm):
    
    class Meta:
        model = Auction
        fields = ['category', 'title', 'description', 'details'
                  ,'start_date', 'end_date', 'status']

class EditProfile(ModelForm):
    
    class Meta:
        model = UserProfile
        fields = ['first_name', 'last_name', 'phone', 'address'
                  ,'city', 'state', 'pincode', 'country']