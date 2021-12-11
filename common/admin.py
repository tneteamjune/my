# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, Photo, Contact
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin

 
# Profile 모델을 따로 보기 원치 않으면 생략함.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'greenpoint',)

class ProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    can_delete = False
    verbose_name_plural = 'Profile'
 
class AUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ( 'username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone','get_department',)
    list_select_related = ('profile', )
 
    def get_phone(self, instance):
        return instance.profile.phone
    get_phone.short_description = 'Phone' # django admin의 표시 이름 재정의
    
    def get_department(self, instance):
        return instance.profile.department
    get_department.short_description = 'Deparement' # 표시 이름 재정의
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(AUserAdmin, self).get_inline_instances(request, obj)
 
admin.site.unregister(User)
admin.site.register(User, AUserAdmin)
admin.site.register(Profile, ProfileAdmin)




# Photo 클래스를 inline으로 나타낸다.
class PhotoInline(admin.TabularInline):
    model = Photo

# Post 클래스는 해당하는 Photo 객체를 리스트로 관리하는 한다. 
class PostAdmin(admin.ModelAdmin):
    inlines = [PhotoInline, ]

# Register your models here.
admin.site.register(Contact, PostAdmin)

