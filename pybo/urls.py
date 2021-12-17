from django.urls import path
from . import views

app_name = 'pybo'

urlpatterns = [
    # path('', views.index, name='index'),

    path('tip/', views.tip, name='tip'),
    path('tip/plastic/' ,views.plastic, name='plastic'),
    path('tip/glass/' ,views.glass, name='glass'),
    path('tip/balpo/' ,views.balpo, name='balpo'),
    path('tip/vinyl/' ,views.vinyl, name='vinyl'),
    path('tip/paper/' ,views.paper, name='paper'),
    path('tip/can/' ,views.can, name='can'),


    # notice 
    path('notice/', views.notice, name='notice'),
    path('<int:question_id>/', views.detail, name='detail'),
    path('error/', views.error, name='error'),

    path('question/create/', views.question_create, name='question_create'),
    path('question/modify/<int:question_id>/', views.question_modify, name='question_modify'),
    path('question/delete/<int:question_id>/', views.question_delete, name='question_delete'),

    path('answer/create/<int:question_id>/', views.answer_create, name='answer_create'),
    path('answer/modify/<int:answer_id>/', views.answer_modify, name='answer_modify'),
    path('answer/delete/<int:answer_id>/', views.answer_delete, name='answer_delete'),

    path('comment/create/question/<int:question_id>/', views.comment_create_question, name='comment_create_question'),
    path('comment/modify/question/<int:comment_id>/', views.comment_modify_question, name='comment_modify_question'),
    path('comment/delete/question/<int:comment_id>/', views.comment_delete_question, name='comment_delete_question'),
    path('comment/create/answer/<int:answer_id>/', views.comment_create_answer, name='comment_create_answer'),
    path('comment/modify/answer/<int:comment_id>/', views.comment_modify_answer, name='comment_modify_answer'),
    path('comment/delete/answer/<int:comment_id>/', views.comment_delete_answer, name='comment_delete_answer'),

    path('vote/question/<int:question_id>/', views.vote_question, name='vote_question'),
    path('vote/answer/<int:answer_id>/', views.vote_answer, name='vote_answer'),
]