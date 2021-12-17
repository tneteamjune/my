from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Point, Contact, Report
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# ID = username
# 이름(닉네임) = first_name
# 연락처 = last_name

class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")
    last_name = forms.IntegerField(label="phone")

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "email", "first_name", "last_name")

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("phone", 'email', 'greenpoint',)

class PointForm(forms.ModelForm):
    class Meta:
        model = Point
        fields = ('reason',)

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ("email", "content", 'imgs')
        # select = forms.CharField(widget=forms.Select(choices=TYPE_CHOICES))
        
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ("email", "content", 'imgs')
        # select = forms.CharField(widget=forms.Select(choices=TYPE_CHOICES))
        