from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'common'

urlpatterns = [
    #회원정보관리
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('change/', views.change, name='change'),
    path('mypage/', views.mypage, name='mypage'),

    #초록점수
    path('point/', views.point, name='point'),
    path('greenpoint/', views.greenpoint, name='greenpoint'),
    path('points_list/', views.points_list, name='points_list'),
    path('quiz/', views.quiz, name='quiz'),
    path('event/', views.event, name='event'),

    #제안하기
    path('contact/', views.contact, name='contact'),

    #관리자페이지
    path('admin/', views.admin, name='admin'),

]