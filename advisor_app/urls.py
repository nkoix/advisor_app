from django.urls import path
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'advisor_app'
urlpatterns = [
    path('', TemplateView.as_view(template_name="advisor_app/index.html"), name='landing'),
    path('home/', views.app_user_home, name='app_home'),
    path('home/logout/', LogoutView.as_view()),
    path('welcome/', views.logged_in, name='logged_in'),
    path('welcome/create/', views.create_account, name='create'),
    path('course_search/', views.CourseSearchView.as_view(), name='course_search'),
    path('search_results/', views.SearchResultsView.as_view(), name='search_results'),
    path('add_course/', views.add_course, name="add_course"),
    path('schedule/remove_course/', views.remove_course, name="remove_course"),
    path('schedule/change_credits/', views.change_credits, name="change_credits"),
    path('schedule/delete_schedule/', views.delete_schedule, name='delete_schedule'),



    path('schedule/', views.schedule_view, name='schedule'),
    path('adv_schedule/', views.adv_schedule_view, name='adv_schedule'),  # advisor Schedule view version
    path('schedule/create/', views.create_schedule, name='create_schedule'), 
    path('schedule/send_schedule/', views.send_schedule, name='send_schedule'),
    path('schedule/withd_schedule/', views.withd_schedule, name='withd_schedule'),
    path('schedule/schedule_status', views.approve_schedule, name='schedule_status'),


    path('students/', views.student_view, name='student'),
    path('schedule/remove_student/', views.remove_student, name="remove_student"),
    path('add_student/', views.add_student, name='add_student'),

    path('chat/', views.chat_view, name='chat'),
    path('chat/<str:room>/', views.room, name='room'),
    path('chat/checkview', views.checkview, name='checkview'),
    path('send', views.send, name='send'),
    path('getMessages/<str:room>/', views.getMessages, name='getMessages'),
]
