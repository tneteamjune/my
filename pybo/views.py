from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect, resolve_url
from django.http import HttpResponse
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.models import Profile, PointsEntry, hashUserNo, Point
from common.forms import PointsForm, PointForm
from .models import Question, Answer, Comment
from .forms import QuestionForm, AnswerForm, CommentForm


# 공지사항 게시판 
def notice(request):

    """
    pybo 목록 출력
    """
    # 입력 파라미터
    page = request.GET.get('page', '1')  # 페이지
    kw = request.GET.get('kw', '')  # 검색어
    so = request.GET.get('so', 'recent')  # 정렬기준

    # 정렬
    if so == 'recommend':
        question_list = Question.objects.annotate(num_voter=Count('voter')).order_by('-num_voter', '-create_date')
    elif so == 'popular':
        question_list = Question.objects.annotate(num_answer=Count('answer')).order_by('-num_answer', '-create_date')
    else:  # recent
        question_list = Question.objects.order_by('-create_date')

    # 검색
    if kw:
        question_list = question_list.filter(
            Q(subject__icontains=kw) |  # 제목검색
            Q(content__icontains=kw) |  # 내용검색
            Q(author__username__icontains=kw) |  # 질문 글쓴이검색
            Q(answer__author__username__icontains=kw)  # 답변 글쓴이검색
        ).distinct()

    # 페이징처리
    paginator = Paginator(question_list, 10)  # 페이지당 10개씩 보여주기
    page_obj = paginator.get_page(page)

    context = {'question_list': page_obj, 'page': page, 'kw': kw, 'so': so}  # <------ so 추가
    return render(request, 'pybo/question_list.html', context)

def detail(request, question_id):
    """
    pybo 내용 출력
    """
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'pybo/question_detail.html', context)

@login_required(login_url='common:login')
def answer_create(request, question_id):
    """
    pybo 답변등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user  # 추가한 속성 author 적용
            answer.create_date = timezone.now()
            answer.question = question
            answer.save()
            return redirect('{}#answer_{}'.format(
                resolve_url('pybo:detail', question_id=question.id), answer.id))
    else:
        form = AnswerForm()
    context = {'question': question, 'form': form}
    return render(request, 'pybo/question_detail.html', context)

@login_required(login_url='common:login')
def answer_modify(request, answer_id):
    """
    pybo 답변수정
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=answer.question.id)

    if request.method == "POST":
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.author = request.user
            answer.modify_date = timezone.now()
            answer.save()
            return redirect('{}#answer_{}'.format(
                resolve_url('pybo:detail', question_id=answer.question.id), answer.id))
    else:
        form = AnswerForm(instance=answer)
    context = {'answer': answer, 'form': form}
    return render(request, 'pybo/answer_form.html', context)

@login_required(login_url='common:login')
def answer_delete(request, answer_id):
    """
    pybo 답변삭제
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user != answer.author:
        messages.error(request, '삭제권한이 없습니다')
    else:
        answer.delete()
    return redirect('pybo:detail', question_id=answer.question.id)

@login_required(login_url='common:login')
def question_create(request):
    """
    pybo 질문등록
    """
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user  # 추가한 속성 author 적용
            question.create_date = timezone.now()
            question.save()
            return redirect('pybo:index')
    else:
        form = QuestionForm()
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login')
def question_modify(request, question_id):
    """
    pybo 질문수정
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '수정권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)

    if request.method == "POST":
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.modify_date = timezone.now()  # 수정일시 저장
            question.save()
            return redirect('pybo:detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    context = {'form': form}
    return render(request, 'pybo/question_form.html', context)

@login_required(login_url='common:login')
def question_delete(request, question_id):
    """
    pybo 질문삭제
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user != question.author:
        messages.error(request, '삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=question.id)
    question.delete()
    return redirect('pybo:index')

@login_required(login_url='common:login')
def comment_create_question(request, question_id):
    """
    pybo 질문댓글등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.question = question
            comment.save()
            return redirect('{}#comment_{}'.format(
                resolve_url('pybo:detail', question_id=comment.question.id), comment.id))
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)

@login_required(login_url='common:login')
def comment_modify_question(request, comment_id):
    """
    pybo 질문댓글수정
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.question.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('{}#comment_{}'.format(
                resolve_url('pybo:detail', question_id=comment.question.id), comment.id))
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)

@login_required(login_url='common:login')
def comment_delete_question(request, comment_id):
    """
    pybo 질문댓글삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.question_id)
    else:
        comment.delete()
    return redirect('pybo:detail', question_id=comment.question_id)

@login_required(login_url='common:login')
def comment_create_answer(request, answer_id):
    """
    pybo 답글댓글등록
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.create_date = timezone.now()
            comment.answer = answer
            comment.save()
            return redirect('{}#comment_{}'.format(
                resolve_url('pybo:detail', question_id=comment.answer.question.id), comment.id))
    else:
        form = CommentForm()
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)

@login_required(login_url='common:login')
def comment_modify_answer(request, comment_id):
    """
    pybo 답글댓글수정
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글수정권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.answer.question.id)

    if request.method == "POST":
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.modify_date = timezone.now()
            comment.save()
            return redirect('{}#comment_{}'.format(
                resolve_url('pybo:detail', question_id=comment.answer.question.id), comment.id))
    else:
        form = CommentForm(instance=comment)
    context = {'form': form}
    return render(request, 'pybo/comment_form.html', context)

@login_required(login_url='common:login')
def comment_delete_answer(request, comment_id):
    """
    pybo 답글댓글삭제
    """
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user != comment.author:
        messages.error(request, '댓글삭제권한이 없습니다')
        return redirect('pybo:detail', question_id=comment.answer.question.id)
    else:
        comment.delete()
    return redirect('pybo:detail', question_id=comment.answer.question.id)

@login_required(login_url='common:login')
def vote_question(request, question_id):
    """
    pybo 질문추천등록
    """
    question = get_object_or_404(Question, pk=question_id)
    if request.user == question.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        question.voter.add(request.user)
    return redirect('pybo:detail', question_id=question.id)

@login_required(login_url='common:login')
def vote_answer(request, answer_id):
    """
    pybo 답글추천등록
    """
    answer = get_object_or_404(Answer, pk=answer_id)
    if request.user == answer.author:
        messages.error(request, '본인이 작성한 글은 추천할수 없습니다')
    else:
        answer.voter.add(request.user)
    return redirect('pybo:detail', question_id=answer.question.id)


# 메인 메뉴
def index(request):
    return render(request, 'pybo/index.html')

def greenpoint(request):
    return render(request, 'pybo/greenpoint.html')

def tip(request):
    return render(request, 'pybo/tip.html')
def plastic(request):
    return render(request,'pybo/tip/plastic.html')
def glass(request):
    return render(request,'pybo/tip/glass.html')
def balpo(request):
    return render(request,'pybo/tip/balpo.html')
def vinyl(request):
    return render(request,'pybo/tip/vinyl.html')


@login_required(login_url='common:login')
def mypage(request):
    """
    mypage 구현
    """
    myuser = request.user
    pic_url = ''

    context = {
        'id': myuser.username,
        'email': myuser.email,
        'picture': pic_url,
        }
    return render(request, 'pybo/mypage.html', context=context)


# 포인트 리스트
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
    return render(request, 'pybo/points_list.html', context)

# def points_list(request):
#     toplist = []
#     users = User.objects.all()
#     points = Profile.objects.all().order_by("-greenpoint")
#     for i in range(len(points)):
#         for j in range(len(users)):
#             if points[i].id == users[j].id:
#                 toplist.append(users[j])
#     context = {
#         'users' : users,
#         'topusers' : toplist[:10]
#     }
#     return render(request, 'pybo/points_list.html', context)



# 작업중

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
    return render(request, 'pybo/points_detail.html', context)


# @login_required(login_url='common:login')
# def points_detail(request, id):
#     user = User.objects.get(id=id)
#     totalPoints = 0
#     for users in User.objects.all():
#         totalPoints += users.profile.greenpoint
#     pointArr = PointsEntry.objects.filter(user=user).order_by('date')
#     startMonth = pointArr.first().date.month
#     endMonth = pointArr.last().date.month
#     if endMonth <= 6:
#         endMonth += 12
#     lenn = endMonth - startMonth + 1
#     points = [0]*lenn
#     months = [""]*lenn
#     colors = [""]*lenn
#     for i in range(lenn):
#         for x in pointArr:
#             month = x.date.month
#             if (month <= 6):
#                 month += 12
#             if (month == startMonth + i):
#                 points[i] += x.points
#         month = startMonth + i
#         if (month > 12):
#             month -= 12
#         months[i] = monthRef[month]
#         if points[i] < 10:
#             colors[i] = "rgba(255, 99, 132,"
#         elif points[i] < 20:
#             colors[i] = "rgba(255, 206, 86,"
#         elif points[i] < 30:
#             colors[i] = "rgba(54, 162, 235,"
#         else:
#             colors[i] = "rgba(129, 247, 173,"

#     avgPoints = (sum(points)/len(points))
#     recentPoints = points[-1]
#     avgStatus, avgColor = getStatus(avgPoints)[0], getStatus(avgPoints)[1]
#     recentStatus, recentColor = getStatus(recentPoints)[0], getStatus(recentPoints)[1]
#     avgPoints /= 40
#     recentPoints /= 40
#     avgPoints *= 100
#     recentPoints *= 100

#     context = {
#         'totalPoints' : totalPoints,
#         'user' : user,
#         'pointArr' : pointArr,
#         'months' : months,
#         'points' : points,
#         'colors' : colors,
#         'avgPoints' : avgPoints,
#         'recentPoints' : recentPoints,
#         'avgStatus' : avgStatus,
#         'recentStatus' : recentStatus,
#         'avgColor' : avgColor,
#         'recentColor' : recentColor
#     }
#     print(context)
#     return render(request, 'pybo/points_detail.html', context)


@login_required(login_url='common:login')
def points_get(request, instance):
    if request.method == "POST":
        obj = PointsEntry.objects.create(user = instance)
        obj.user = request.user.id
        obj.points = 10
        obj.reason = "get 10 points!"
        obj.save()
    
    #     if form.is_valid():
    #         formInput = form.cleaned_data
    #         newID = hashUserNo(formInput['username'])
    #         if User.objects.filter(userNo=newID).exists() == False:
    #             newID = hashUserNo(formInput['username'])
    #             newUser = User(userNo=formInput['username'], firstName=(formInput['firstName']).lower(), lastName=(formInput['lastName']).lower(), points=0)
    #             newUser.save()
        
    #     # currentUser = User.objects.filter(userNo=request.user.id).first()

    #     # for object in PointsEntry.objects.filter(user=request.user.id):
    #     #     if object.reason == pointentry.reason :
    #     #         # raise ValidationError(_('Points already added.'))
    #     #         return HttpResponse('Points already added.')

    #         messages.success(request, 'Request submitted succesfully!')
    #         form.save()
    #         form = PointsForm()
    #     # Save the form. Also adds a point entry
    # context = {
    #     'form' : form,
    # }
    return render(request, 'pybo/points_get.html')


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



