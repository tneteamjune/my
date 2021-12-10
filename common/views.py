from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from common.forms import UserForm, ProfileForm, PointsForm, PointForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from common.models import Profile, PointsEntry, Point
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.utils import timezone
from django.contrib.auth.models import User
from common.models import Profile, PointsEntry, hashUserNo, Point
from common.forms import PointsForm, PointForm

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

def update_profile(request, user_id):
    user = User.objects.get(pk=user_id)
    user.profile.greenpoint = 0
    user.save()

# @login_required
# @transaction.atomic
# def update_profile(request):
#     if request.method == 'POST':
#         user_form = UserForm(request.POST, instance=request.user)
#         profile = Profile.objects.get(user = request.user)
#         profile_form = ProfileForm(request.POST, instance=request.user.profile)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#             messages.success(request, _('Your profile was successfully updated!'))
#             return redirect('settings:profile')
#         else:
#             messages.error(request, _('Please correct the error below.'))
#     else:
#         user_form = UserForm(instance=request.user)
#         profile_form = ProfileForm(instance=request.user.profile)
#     return render(request, 'common/mypage.html', {
#         'user_form': user_form,
#         'profile_form': profile_form
#     })

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
            messages.success(request, ('Your profile was successfully updated!'))
            return redirect('common:mypage')
        else:
            update_session_auth_hash(request, user_form)
            messages.error(request, ('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
    return render(request, 'common/change.html', {'user_form': user_form})


# 마이페이지
@login_required(login_url='common:login')
def mypage(request):
    myuser = request.user
    pic_url = ''

    context = {
        'id': myuser.username,
        'email': myuser.email,
        'picture': pic_url,
        }
    return render(request, 'common/mypage.html', context=context)




# 포인트 관련
def greenpoint(request):
    return render(request, 'common/point/greenpoint.html')


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


@login_required(login_url='common:login')
def point(request):
    user = get_object_or_404(User, pk=request.user.id)
    if request.method == "POST":
        form = PointForm(request.POST)
        if form.is_valid():
            point = form.save(commit=False)
            point.owner = request.user
            point.date = timezone.now()
            point.point = 10
            point.reason = "get 10 points!"
            point.save()
            return redirect('common:points_detail', id=request.user.id)
    else:
        form = PointForm()
    context = {'form': form}
    return render(request, 'common/point/points.html', context)



# 작업중
@login_required(login_url='common:login')
def points_get(request, instance):
    if request.method == "POST":
        obj = PointsEntry.objects.create(user = instance)
        obj.user = request.user.id
        obj.points = 10
        obj.reason = "get 10 points!"
        obj.save()
    return render(request, 'common/point/points_get.html')


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

@login_required(login_url='common:login')
def points_detail(request, id):
    user = User.objects.get(id=id)
    totalPoints = 0
    for users in User.objects.all():
        totalPoints += users.profile.greenpoint
    pointArr = Point.objects.filter(owner_id=id).order_by('date')

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
    return render(request, 'common/point/points_detail.html', context)



def points_entrys(request):
    form = PointsForm(request.POST or None)
    query = request.GET.get('meetingKey')
    if query is not None:
        form.initial['meetingKey'] = query

    # Only do something if the request is post
    if request.method == "POST":
        form = PointsForm(request.POST)
        # Make sure noone is trying to hack us. Can use cleaned_data after calling is_valid
        if form.is_valid():
            # If the meetingkey is not valid then stop the program

            # Get the meetingKey object associated with the meeting key
            data = MeetingKey.objects.filter(meetingKey=form.cleaned_data['meetingKey'])
            if data.exists() == False:
                raise ValidationError(_('Key does not exist.'))
            # Startblock
            # We are going to check if a user exists. If it doesn't then we are going to create one
            formInput = form.cleaned_data
            newID = hashUserNo(formInput['user_ID'])
            if User.objects.filter(userNo=newID).exists() == False:
                newID = hashUserNo(formInput['user_ID'])
                newUser = User(userNo=formInput['user_ID'], firstName=(formInput['firstName']).lower(), lastName=(formInput['lastName']).lower(), points=0)
                newUser.save()
            # EndBlock
            # After creating the user, we will fetch it based on the inputted ID
            currentUser = User.objects.filter(userNo=hashUserNo(form.cleaned_data['user_ID'])).first()

            for object in PointsEntry.objects.filter(user=currentUser):
                if object.meeting == data.first():
                    # raise ValidationError(_('Points already added.'))
                    return HttpResponse('Points already added.')

            messages.success(request, 'Request submitted succesfully!')
            form.save()
            form = PointsForm()
            # Save the form. Also adds a point entry
    context = {
        'form' : form,
    }
    return render(request, 'points/entry.html', context)






