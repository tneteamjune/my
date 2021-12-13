from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
import hashlib
from django.utils.translation import gettext_lazy as _

def hashKey():
    ck = CurrentKey.objects.first()
    print(ck)
    ck.currentKey = ck.currentKey + 1
    ck.save()
    return hashlib.sha256(str(ck.currentKey).encode('utf-8')).hexdigest()

def hashUserNo(string):
    return hashlib.sha256(str(hashlib.sha256(str(string+"iwannabetheboshy").encode('utf-8')).hexdigest()+"donotdisturb").encode('utf-8')).hexdigest()


now = timezone.now()

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=30, null=True)
    email = models.CharField(max_length=100, null=True)
    greenpoint = models.IntegerField('초록점수', blank=True, null=True)
    coupon = models.IntegerField('쿠폰', default = 0)

    def __str__(self):
        return self.user.username

# 유저 생성시 profile.greenpoint 생성
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.greenpoint = 10

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class Point(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    point = models.IntegerField(default=0)
    reason = models.TextField(default="")
    event = models.TextField(default="")
    def __str__(self):
        return self.owner.username

@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        point = Point.objects.create(owner=instance)
        point.date = timezone.now()
        point.point = 10
        point.reason = "가입축하포인트"
        point.event = "0.가입"
        point.save()
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# 포인트 발생시 proflie.greenpoint에 반영    
@receiver(post_save, sender=Point)
def add_points(sender, instance, created, **kwargs):
    if created:
        user_id = instance.owner_id
        user = User.objects.get(id=user_id)
        pointArr = Point.objects.filter(owner_id=user_id).order_by('date')
        point_sum = 0
        for point in pointArr :
            point_sum += point.point
        user.profile.greenpoint = point_sum
        user.profile.save()
        

class Contact(models.Model):
   
    ADD, IDEA, ERROR, ETC = 'add', 'idea', 'error', 'etc'
    TYPE_CHOICES = (
        (ADD, '휴지통 추가 설치가 필요해요'),
        (IDEA, '이런 기능이 있었으면 해요'),
        (ERROR, '사이트에 오류가 있어요'),
        (ETC, '그 외 문의가 있어요')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=200)
    content = models.TextField()
    create_date = models.DateTimeField()
    modify_date = models.DateTimeField(null=True, blank=True)
    imgs = models.ImageField(upload_to='images/', blank=True, null=True)
    # type = models.CharField(
    #     verbose_name=_("어떤 제안이 있으신가요?"),
    #     max_length=20,
    #     choices=CONTACT_TYPE_CHOICES,
    #     default=ADD
    # )
    type = models.CharField(
        choices=TYPE_CHOICES,
        max_length=100, null=True, blank=True)

    class Meta:
        ordering = ('-create_date',)

    def __str__(self):
        return self.subject


class Photo(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True)
    image = models.ImageField(upload_to='images/', blank=True, null=True)

