from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'common'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('change/', views.change, name='change'),
    path('mypage/', views.mypage, name='mypage'),

    path('point/', views.point, name='point'),
    path('greenpoint/', views.greenpoint, name='greenpoint'),
    path('points_list/', views.points_list, name='points_list'),
    path('quiz/', views.quiz, name='quiz'),

    path('contact/', views.contact, name='contact'),

]