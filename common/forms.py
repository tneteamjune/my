from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Point, Contact
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
        


# class PointsForm(forms.ModelForm):
#     meetingKey = forms.CharField(
#         label="Meeting Key",
#         required=True,
#         widget=forms.TextInput(
#             attrs={
#                 'class' :'form-control',
#                 'type' : 'password',
#                 'id' : 'inputPassword4',
#                 'placeholder' : 'Password'
#                 }
#             )
#         )
#     user_ID = forms.CharField(
#         label="user ID",
#         required=True,
#         widget=forms.TextInput(
#             attrs={
#                 "type" : "text",
#                 "class" : "form-control",
#                 "id" : "InputID",
#                 "placeholder" : "0609067234"
#             }
#         )
#     )

#     class Meta :
#         model = PointsEntry
#         fields = ('user', 'date', 'points', 'reason')

#     def save(self):
#         data = self.cleaned_data
#         newID = hashUserNo(data['user_ID'])
#         print(newID)
#         tMeeting = MeetingKey.objects.filter(meetingKey=data['meetingKey']).first()
#         tUser=User.objects.filter(studentNo=newID).first()
#         print(tUser)
#         newEntry = PointsEntry(user=tUser, points=tMeeting.points, reason=tMeeting.name, meeting=tMeeting)
#         print(newEntry)
#         newEntry.save()
#         meetingEntry = MeetingEntry(student=tUser, meeting=tMeeting)
#         meetingEntry.save()


