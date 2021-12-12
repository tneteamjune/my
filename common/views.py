from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from common.forms import UserForm, ProfileForm, PointForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from django.contrib.auth.models import User
from common.models import Profile, Point, Contact, Photo
from common.forms import PointForm, ContactForm

def signup(request):
    """
    계정생성
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)  # 사용자 인증
            login(request, user)  # 로그인
            return redirect('index')
    else:
        form = UserForm()
    return render(request, 'common/signup.html', {'form': form})


# def update_profile(request, user_id):
#     user = User.objects.get(pk=user_id)
#     user.profile.greenpoint = 0
#     user.save()


@login_required(login_url='common:login')
def change(request):
    """
    정보변경
    """
    if request.method == "POST":
        user_form = UserForm(request.POST, instance=request.user)
        if user_form.is_valid():
            user = user_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, ('회원정보가 변경되었습니다!'))
            return redirect('common:mypage')
        else:
            messages.warning(request, ('입력 정보를 다시 한번 확인해 주세요.'))
            update_session_auth_hash(request, user_form)            
    else:
        user_form = UserForm(instance=request.user)
    return render(request, 'common/change.html', {'user_form': user_form})


#제안하기
def contact(request):
    if(request.method == 'POST'):
        contact_form = ContactForm(request.POST, instance=request.user)
        if contact_form.is_valid():
            post = Contact()
            post.user = request.user
            post.subject = request.POST['subject']
            post.content = request.POST['content']
            post.create_date = timezone.datetime.now()
            try :
                post.imgs = request.FILES['imgs']
            except :
                pass
            post.save()
            # # name 속성이 imgs인 input 태그로부터 받은 파일들을 반복문을 통해 하나씩 가져온다 
            # for img in request.FILES.getlist('imgs'):
            #     # Photo 객체를 하나 생성한다.
            #     photo = Photo()
            #     # 외래키로 현재 생성한 Post의 기본키를 참조한다.
            #     photo.contact = post
            #     # imgs로부터 가져온 이미지 파일 하나를 저장한다.
            #     photo.image = img
            #     # 데이터베이스에 저장
            #     photo.save()
            messages.info(request, '제안이 제출되었습니다.')
            return redirect('common:contact')
        else :
            messages.warning(request, ('입력 정보를 다시 한번 확인해 주세요.'))
            # return redirect('common:contact')
        # return redirect('/detail/' + str(post.id))
    else:
        return render(request, 'common/contact.html')

def greenpoint(request):
    return render(request, 'common/point/greenpoint.html')

def quiz(request):
    return render(request, 'common/point/quiz.html')

def event(request):
    return render(request, 'common/event.html')

monthRef = {
    8 : 'August',
    9 : 'September',
    10 : "October",
    11 : "November",
    12 : 'December',
    1 : 'January',
    2 : 'February',
    3 : 'March',
    4 : 'April',
    5 : 'May',
    6 : 'June'
}

def getStatus(v):
    if v < 10:
        return ['inactive', 'text-danger']
    elif v < 20:
        return ['average', 'text-warning']
    elif v < 30:
        return ['good', 'text-info']
    else:
        return ['spectacular', 'text-success']


# 마이페이지 (초록점수현황 포함)
@login_required(login_url='common:login')
def mypage(request):
    userid = request.user.id
    user = User.objects.get(id=userid)

    totalPoints = user.profile.greenpoint
    couponPoints = 100

    pointArr = Point.objects.filter(owner_id=userid).order_by('date')

    point_sum = 0
    for point in pointArr:
        point_sum += point.point

    startMonth = pointArr.first().date.month
    endMonth = pointArr.last().date.month
    if endMonth <= 6:
        endMonth += 12
    lenn = endMonth - startMonth + 1
    points = [0]*lenn
    months = [""]*lenn
    colors = [""]*lenn
    for i in range(lenn):
        for x in pointArr:
            month = x.date.month
            if (month <= 6):
                month += 12
            if (month == startMonth + i):
                points[i] += x.point
        month = startMonth + i
        if (month > 12):
            month -= 12
        months[i] = monthRef[month]
        if points[i] < 10:
            colors[i] = "rgba(255, 99, 132,"
        elif points[i] < 20:
            colors[i] = "rgba(255, 206, 86,"
        elif points[i] < 30:
            colors[i] = "rgba(54, 162, 235,"
        else:
            colors[i] = "rgba(129, 247, 173,"

    avgPoints = (sum(points)/len(points))
    recentPoints = points[-1]
    avgStatus, avgColor = getStatus(avgPoints)[0], getStatus(avgPoints)[1]
    recentStatus, recentColor = getStatus(recentPoints)[0], getStatus(recentPoints)[1]
    avgPoints /= 40
    recentPoints /= 40
    avgPoints *= 100
    recentPoints *= 100

    context = {
        'couponPoints' : couponPoints,
        'totalPoints' : totalPoints,
        'user' : user,
        'pointArr' : pointArr,
        'months' : months,
        'points' : points,
        'colors' : colors,
        'avgPoints' : avgPoints,
        'recentPoints' : recentPoints,
        'avgStatus' : avgStatus,
        'recentStatus' : recentStatus,
        'avgColor' : avgColor,
        'recentColor' : recentColor
    }
    print(context)
    return render(request, 'common/mypage.html', context)


# 포인트 랭킹
def points_list(request):
    toplist = []
    users = User.objects.all()
    points = Profile.objects.all().order_by("-greenpoint")
    for i in range(len(points)):
        for j in range(len(users)):
            if points[i].id == users[j].id:
                toplist.append(users[j])
    context = {
        'users' : users,
        'topusers' : toplist[:10]
    }
    return render(request, 'common/point/points_list.html', context)


# 10점받기
@login_required(login_url='common:login')
def point(request):
    user = get_object_or_404(User, pk=request.user.id)

    userid = request.user.id
    pointArr = Point.objects.filter(owner_id=userid).order_by('date')
    isvalid = 0
    for point in pointArr:
        if point.event == "1.환경사랑참여" :
            isvalid = -1
            break

    if request.method == "POST":
        form = PointForm(request.POST)
        if form.is_valid():
            if isvalid == -1 :
                messages.warning(request, '이미 참여하셨습니다.')
                return redirect('common:point')
            else:
                point = form.save(commit=False)
                point.owner = request.user
                point.date = timezone.now()
                point.point = 30
                point.reason = "환경사랑 참여 약속"
                point.event = "1.환경사랑참여"
                point.save()
                messages.info(request, '초록점수 10점을 받았습니다.')
                return redirect('common:point')
    else:
        form = PointForm()
    context = {'form': form}
    return render(request, 'common/point/points.html', context)



# # 작업중
# @login_required(login_url='common:login')
# def points_get(request, instance):
#     if request.method == "POST":
#         obj = PointsEntry.objects.create(user = instance)
#         obj.user = request.user.id
#         obj.points = 10
#         obj.reason = "get 10 points!"
#         obj.save()
#     return render(request, 'common/point/points_get.html')



# def points_entrys(request):
#     form = PointsForm(request.POST or None)
#     query = request.GET.get('meetingKey')
#     if query is not None:
#         form.initial['meetingKey'] = query

#     # Only do something if the request is post
#     if request.method == "POST":
#         form = PointsForm(request.POST)
#         # Make sure noone is trying to hack us. Can use cleaned_data after calling is_valid
#         if form.is_valid():
#             # If the meetingkey is not valid then stop the program

#             # Get the meetingKey object associated with the meeting key
#             data = MeetingKey.objects.filter(meetingKey=form.cleaned_data['meetingKey'])
#             if data.exists() == False:
#                 raise ValidationError(_('Key does not exist.'))
#             # Startblock
#             # We are going to check if a user exists. If it doesn't then we are going to create one
#             formInput = form.cleaned_data
#             newID = hashUserNo(formInput['user_ID'])
#             if User.objects.filter(userNo=newID).exists() == False:
#                 newID = hashUserNo(formInput['user_ID'])
#                 newUser = User(userNo=formInput['user_ID'], firstName=(formInput['firstName']).lower(), lastName=(formInput['lastName']).lower(), points=0)
#                 newUser.save()
#             # EndBlock
#             # After creating the user, we will fetch it based on the inputted ID
#             currentUser = User.objects.filter(userNo=hashUserNo(form.cleaned_data['user_ID'])).first()

#             for object in PointsEntry.objects.filter(user=currentUser):
#                 if object.meeting == data.first():
#                     # raise ValidationError(_('Points already added.'))
#                     return HttpResponse('Points already added.')

#             messages.success(request, 'Request submitted succesfully!')
#             form.save()
#             form = PointsForm()
#             # Save the form. Also adds a point entry
#     context = {
#         'form' : form,
#     }
#     return render(request, 'points/entry.html', context)






