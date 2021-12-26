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
from common.models import Profile, Point, Contact, Photo, Report
from common.forms import PointForm, ContactForm, ReportForm

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
            return redirect('common:mypage')
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
    if totalPoints >= 100:
        totalPoints = couponPoints

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


# 환경사랑 참여 점수받기
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
                point.point = 20
                point.reason = "환경사랑 참여 약속"
                point.event = "1.환경사랑참여"
                point.save()
                messages.info(request, '초록점수 20점을 받았습니다.')
                return redirect('common:point')
    else:
        form = PointForm()
    context = {'form': form}
    return render(request, 'common/point/points.html', context)

#제안하기
def contact(request):
    if request.user.is_authenticated:
        if(request.method == 'POST'):
            contact_form = ContactForm(request.POST)
            if contact_form.is_valid():
                post = Contact()
                post.user = request.user
                post.email = request.POST['email']
                post.subject = request.POST['subject']
                post.content = request.POST['content']
                post.create_date = timezone.datetime.now()
                try :
                    post.imgs = request.FILES['imgs']
                except :
                    pass
                post.save()
                messages.info(request, '제안이 제출되었습니다.')
                return redirect('common:my_contact')
            else :
                messages.warning(request, ('상세 내용은 필수 항목입니다.'))
        else:
            contact_form = ContactForm()
        return render(request, 'common/contact.html', {'contact_form': contact_form})
    else :
        return render(request, 'common/contact_none.html')


# 오류신고 (신고 즉시 5점 적립)
def report(request):
    if request.user.is_authenticated:
        if(request.method == 'POST'):
            report_form = ReportForm(request.POST)
            if report_form.is_valid():
                post = Report()
                post.user = request.user
                post.email = request.POST['email']
                post.content = request.POST['content']
                post.create_date = timezone.datetime.now()
                post.type = request.POST['type']
                try :
                    post.imgs = request.FILES['imgs']
                except :
                    pass
                post.save()
                point = Point()
                point.owner = request.user
                point.date = timezone.now()
                point.point = 5
                point.reason = "오류신고 참여"
                point.event = "2.오류신고 참여"
                point.save()
                messages.info(request, '참여 감사합니다. 초록점수 5점을 받으셨습니다')
                return redirect('common:report')
            else :
                messages.warning(request, ('상세 내용은 필수 항목입니다.'))
        else:
            report_form = ReportForm()
        return render(request, 'common/report.html', {'report_form': report_form})
    else :
        return render(request, 'common/report_none.html')


# 관리자페이지
def admin(request):
    if request.user.is_superuser:
        contacts = Contact.objects.all().order_by("-create_date")
        if request.method == "POST":
            contact_id = request.POST['id']
            contact = Contact.objects.get(id=contact_id)
            contact.select = 1
            contact.save()
        context = {
            'contacts' : contacts,
            }
        return render(request, 'common/admin.html', context)
    else:
        return render(request, 'pybo/index.html')

# 제안채택(사용자)
def contact_point(request):
    if request.method == "POST":
        form = PointForm(request.POST)
        point = form.save(commit=False)
        point.owner = request.user
        point.date = timezone.now()
        point.point = 20
        point.reason = "제안 채택"
        point.event = request.POST['event']
        point.save()
        contact = Contact.objects.get(id=point.event)
        contact.select = 2
        contact.save()
        messages.info(request, '초록점수 20점을 받았습니다.')
        return redirect('common:my_contact')
    else:
        form = PointForm()
    context = {'form': form }
    return render(request, 'common/my_contact.html', context)


#나의 제안하기
def my_contact(request):
    userid = request.user.id
    contacts = Contact.objects.filter(user_id=userid).order_by('-create_date')

    context = {
        'contacts' : contacts,
        }
    return render(request, 'common/my_contact.html', context)


# 쿠폰발행
def coupon(request):
    user = request.user
    if(request.method == 'POST'):
        point_form = PointForm(request.POST)
        if point_form.is_valid():
            if user.profile.greenpoint < 100 :
                messages.warning(request, '초록점수가 부족합니다.')
                return redirect('common:coupon')
            else:
                point = Point()
                point.owner = request.user
                point.date = timezone.now()
                point.point = -100
                point.reason = "에코쿠폰 교환"
                point.event = "3.쿠폰교환"
                point.save()
                profile = Profile.objects.get(id=user.id)
                profile.coupon += 1
                profile.save()
                messages.info(request, '축하합니다. 에코쿠폰이 발행되었습니다!')
                return redirect('common:coupon')
    else:
        point_form = PointForm()
    context = {'form': point_form}
    return render(request, 'common/point/coupon.html', context)
