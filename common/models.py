from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.utils import timezone
import hashlib

def hashKey():
    ck = CurrentKey.objects.first()
    print(ck)
    ck.currentKey = ck.currentKey + 1
    ck.save()
    return hashlib.sha256(str(ck.currentKey).encode('utf-8')).hexdigest()

def hashUserNo(string):
    return hashlib.sha256(str(hashlib.sha256(str(string+"iwannabetheboshy").encode('utf-8')).hexdigest()+"donotdisturb").encode('utf-8')).hexdigest()


now = timezone.now()

class Point(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    point = models.IntegerField(default=0)
    reason = models.TextField()
    event = models.TextField()

@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        point = Point.objects.create(owner = instance)
        point.date = timezone.now()
        point.point = 10
        point.reason = "welcome point"
        point.event = "0. signup"
        point.save()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=30, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField('연락처', max_length=30, blank=True, null=True)
    greenpoint = models.IntegerField('초록점수', blank=True, null=True)
    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        instance.profile.greenpoint = 10

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

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
        

#작업중

class PointsEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    points = models.IntegerField(null=True)
    reason = models.TextField(null=True)

    def __str__(self):
        return str(self.date) + "-" + str(self.user)

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     relatedEntries = PointsEntry.objects.filter(user=self.user)
    #     self.user.profile.greenpoint = sum([entry.points for entry in relatedEntries])
    #     self.user.save()

@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        obj = PointsEntry.objects.create(user = instance)
        obj.points = 10
        obj.reason = "welcome point"
        obj.save()

class MeetingKey(models.Model):
    meetingKey = models.CharField(max_length=64, default=hashKey)
    name = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    points = models.IntegerField(default=0)
    desc = models.TextField()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('meetingList', kwargs={'pk' : self.id})

class MeetingEntry(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    meeting = models.ForeignKey(MeetingKey, on_delete=models.CASCADE, null=True)




