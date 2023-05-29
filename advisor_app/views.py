from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.urls import reverse

from advisor_app.admin import StudentAdmin
from .models import AppUser, Course, Student, Advisor, Schedule, Room, Message
from django.views import generic
from advisor_app.forms import CreateAccountForm, ScheduleApprovalForm, ScheduleForm, AddCourseForm, ChangeCreditsForm, AddStudentForm
import requests
import json

# Create your views here.


def app_user_home(request):
    appuser = get_object_or_404(AppUser, user=request.user)
    if appuser.is_advisor:
        role = "an Advisor"
    else:
        role = "a Student"
    return render(request, 'advisor_app/appuser.html', {
        'role': role,
    })


def logged_in(request):
    try:
        app_user = AppUser.objects.get(user=request.user)
    except AppUser.DoesNotExist:
        return HttpResponseRedirect('create/')
    return HttpResponseRedirect(reverse('advisor_app:app_home'))


def create_account(request):
    if request.method == 'POST':
        form = CreateAccountForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data['role']
            if role == "S":
                AppUser.create(request.user, False)
                latest_user = AppUser.objects.all().last()
                student = Student()
                student.userID = latest_user.user.id
                student.name = latest_user.user.first_name + " " + latest_user.user.last_name
                student.email = latest_user.user.email
                student.save()
            else:
                AppUser.create(request.user, True)
                latest_user = AppUser.objects.all().last()
                advisor = Advisor()
                advisor.userID = latest_user.user.id
                advisor.name = latest_user.user.first_name + " " + latest_user.user.last_name
                advisor.email = latest_user.user.email
                advisor.save()
        return HttpResponseRedirect(reverse('advisor_app:app_home'))
    else:
        form = CreateAccountForm()
    return render(request, 'advisor_app/create_account.html', {'form': form})


def add_course(request):
    course_id = request.GET.get("course")
    if request.method == 'POST':
        user = request.user
        student_email = user.email
        form = AddCourseForm(user,request.POST)
        if form.is_valid():
            s = form.cleaned_data['schedule']
            schedule = Schedule.objects.filter(name=s).last()
            course = Course.objects.filter(id=course_id).last()
            schedule.add_course(course)
            schedule.is_approved = False # Schedule has changed, thus no longer approved


            # student.schedules[Some_val]['\n    \"courses\"'] =     # Attempting to add student data to a list
            return HttpResponseRedirect('/advisor_app/schedule/')
    else:
        form = AddCourseForm(request.user)

    return render(request, 'advisor_app/add_course.html', {'form': form})


def remove_course(request):
    course_id = request.GET.get("course")
    schedule_id = request.GET.get("schedule")
    course = Course.objects.filter(id=course_id).last()
    schedule = Schedule.objects.filter(id=schedule_id).last()
    schedule.remove_course(course)
    schedule.is_approved = False # Schedule has changed, thus no longer approved
    return HttpResponseRedirect('/advisor_app/schedule/')


def change_credits(request):
    course_id = request.GET.get("course")
    schedule_id = request.GET.get("schedule")
    course = Course.objects.filter(id=course_id).last()
    schedule = Schedule.objects.filter(id=schedule_id).last()

    if request.method == "POST":
        form = ChangeCreditsForm(request.POST)
        if form.is_valid():
            c = int(form.cleaned_data['creds'])
            if course.min_credits() <= c <= course.max_credits():
                schedule.change_credits(course, c)
                return HttpResponseRedirect('/advisor_app/schedule/')
    else:
        form = ChangeCreditsForm()

    return render(request, 'advisor_app/change_credits.html', {'form': form, 'min': course.min_credits(),
                                                               'max': course.max_credits(), 'course': course,
                  'schedule': schedule})


class CourseSearchView(generic.TemplateView):
    template_name = 'advisor_app/course_search.html'


def create_schedule(request):
    if request.method == 'POST':
        form = ScheduleForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            user = request.user
            #full_name = user.first_name + " " + user.last_name
            email = user.email
            student = Student.objects.filter(email=email).last()
            schedule = Schedule()
            schedule.student = email
            schedule.name = name

            # -----------
            # Attempting to Grab Schedule Data from a particular student
            #student.schedules.append(schedule.toJSON())
            #student.save()

            # ----

            schedule.save()
            schedule.courses.all().delete()
            return HttpResponseRedirect('/advisor_app/schedule/')
    else:
        form = ScheduleForm()

    return render(request, 'advisor_app/create_schedule.html', {'form': form})


def delete_schedule(request):
    schedule_id = request.GET.get("schedule")
    schedule = Schedule.objects.filter(id=schedule_id).last()
    schedule.delete()
    return HttpResponseRedirect('/advisor_app/schedule/')



class SearchResultsView(generic.ListView):
    model = Course
    template_name = "advisor_app/search_results.html"

    def get_queryset(self):
        department = self.request.GET.get("department")
        number = self.request.GET.get("number")
        title = self.request.GET.get("title")

        requirement = self.request.GET.get("requirement")
        object_list = Course.objects.filter(title__icontains=title, department__icontains=department, catalog_nbr__icontains=number)
        return object_list 


def populate_courses():  # populates the database with every Fall 2023 course from SIS (should be 8499 courses)
    base_url = 'https://sisuva.admin.virginia.edu/psc/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_CLASS_SEARCH.FieldFormula.IScript_ClassSearch?institution=UVA01&term=1238'
    page = 1
    url = base_url + '&page=' + str(page)
    r = requests.get(url)
    while len(r.json()) > 0:
        for c in r.json():
            new_course = Course(title=c['descr'], department=c['subject'], section=c['class_section'],
                                catalog_nbr=c['catalog_nbr'], meetings=c['meetings'], credit=c['units'],
                                component=c['component'])
            new_course.save()
        page += 1
        url = base_url + '&page=' + str(page)
        r = requests.get(url)

# class CreateScheduleView(generic.TemplateView):
#    template_name = "advisor_app/create_schedule.html"


def schedule_view(request):
    user = request.user
    email = user.email
    schedules = Schedule.objects.filter(student=email)
    context = {
        "schedules": schedules,
    }
    return render(request, "advisor_app/schedule.html", context)
#--------------------------------------------------------------------------------------------------------------------------------------------------
def adv_schedule_view(request):
    user = request.user
    emailInput = user.email    
    schedules1 = Schedule.objects.filter(student=emailInput)
    theAdvisor = Advisor.objects.filter(email = emailInput)
    #print(theAdvisor[0].students.all())
    students = theAdvisor[0].students.all()

    schedules2 =[]
    schedules3 = []
    for eachStudent in students:
        #print(eachStudent, "hehehe")
        schedules2.append(Schedule.objects.filter(student = eachStudent.email))

    for eachSchedule in schedules2:
        
        #print(eachSchedule[0], "dog")
        i = 0
        while i < len(eachSchedule):
            if eachSchedule[i].pending_approval == True:
                #changing "schedule3" into a list of tuple so that I can better display student names -Mohsen
                student = Student.objects.get(email = eachSchedule[i].student)
                schedules3.append((eachSchedule[i],student))
            i+=1

    context = {
        "schedules1": schedules1,
        "schedules2": schedules2,
        "schedules3": schedules3,
    }
    return render(request, "advisor_app/advs_schedules.html/", context)

#---------------------------------------------------------------------------------------------------------------------------------------------------




def send_schedule(request):
    schedule_id = request.GET.get("schedule")
    schedule = Schedule.objects.filter(id=schedule_id).last()
    schedule.pending_approval = True
    schedule.isapproved = False
    schedule.isrejected = False
    schedule.save()
    return HttpResponseRedirect('/advisor_app/schedule/')

def withd_schedule(request):
    schedule_id = request.GET.get("schedule")
    schedule = Schedule.objects.filter(id=schedule_id).last()
    schedule.pending_approval = False
    schedule.isapproved = False
    schedule.isrejected = False
    schedule.save()
    return HttpResponseRedirect('/advisor_app/schedule/')


def approve_schedule(request):
    appuser = get_object_or_404(AppUser, user=request.user)
    if appuser.is_advisor and request.method == 'POST':# or True:
        form = ScheduleApprovalForm(request.POST)
        #test = request.GET.get("schedule")
        #print(test)
        #schedule = Schedule()
        schedule_id = request.POST.get('schedule_id')
        schedule = Schedule.objects.get(id=schedule_id)
        print(schedule)
        if form.is_valid():
            #print(form.cleaned_data)
            #app_status = form.cleaned_data=('approvalStatus', None)
            app_status = form.cleaned_data['approvalStatus']
            #s = form.cleaned_data=('schedule', None)
            #s = form.cleaned_data['schedule']
            #print(form.cleaned_data)
            #print(app_status)
            #print(s)
            
            #schedule = Schedule.objects.filter(name=s).last()

            if app_status == "Y":
                #print('dog')
                schedule.isapproved = True
                schedule.isrejected = False
                schedule.pending_approval = False  # If the schedule is approved it is no longer pending
                schedule.save()
                return HttpResponseRedirect('/advisor_app/adv_schedule/')
            elif app_status == "N":
                #print("not dog")
                schedule.isapproved = False
                schedule.isrejected = True
                schedule.pending_approval = False  # Unsure If the schedule is not approved it should also no longer be pending
                schedule.save()
                return HttpResponseRedirect('/advisor_app/adv_schedule/')
    else:
        form = ScheduleForm()
        return HttpResponseRedirect('/advisor_app/adv_schedule/')
        #return HttpResponseRedirect(reverse('advisor_app:course_search'))
    

    return render(request, 'advisor_app/update_approval.html', {'form': form, 'schedule': schedule})



def student_view(request): # Advisor Adding Students View
    user = request.user
    email = user.email
    advisor = Advisor.objects.filter(email=email).last()
    students = advisor.students.all()   # Nonetype Error
    context = {
        "students": students,
    }
    return render(request, "advisor_app/students.html", context)

def add_student(request):
    if request.method == 'POST':
        user = request.user
        form = AddStudentForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            advisor = Advisor.objects.filter(email=user.email).last()
            advisor.add_student(student)

            return HttpResponseRedirect('/advisor_app/students/')
    else:
        form = AddStudentForm()
    
    return render(request, 'advisor_app/add_student.html', {'form': form})

def remove_student(request):
    student_ID = request.GET.get("student")
    email = request.user.email
    advisor = Advisor.objects.filter(email=email).last()
    student = Student.objects.filter(id=student_ID).last()
    advisor.remove_student(student)
    return HttpResponseRedirect('/advisor_app/students/')

#Chatroom fucntions
'''
REFERENCES
Title:  django-chat-app
Author: Tomi Tokko
Date: Apr 18, 2021
Code version: 1
URL: https://github.com/tomitokko/django-chat-app/commits?author=tomitokko
'''

def chat_view(request):
    email = request.user.email
    #User is an advisor
    if Advisor.objects.filter(userID=request.user.id).exists():
        advisor = Advisor.objects.filter(email=email).last()
        students = advisor.students.all()
        is_advisor = True
        context = {
        "students": students,
        "is_advisor": is_advisor,
        }
        return render(request, 'advisor_app/chat.html', context)

    #User is a student
    else:
        student = Student.objects.filter(email=email).last()
        advisors = Advisor.objects.filter(students__email__startswith=student.email)   
        is_advisor = False
        context = {
        "advisors": advisors,
        "is_advisor": is_advisor,
        }
        return render(request, 'advisor_app/chat.html', context)



def room(request,room):
    if Advisor.objects.filter(userID=request.user.id).exists():
        is_advisor = True
    else:
        is_advisor = False
    username = request.GET.get('username')
    room_details = Room.objects.get(name=room)
    return render(request, 'advisor_app/room.html', {
        'username': username,
        'room': room,
        'room_details': room_details,
        'is_advisor': is_advisor
    })


def checkview(request):

    #User is an advisor
    if Advisor.objects.filter(userID=request.user.id).exists():
        student_ID = request.GET.get("student")
        email = request.user.email
        advisor = Advisor.objects.filter(email=email).last()
        student = Student.objects.filter(id=student_ID).last()
        username = advisor.name

    if Student.objects.filter(userID=request.user.id).exists():
        advisor_ID = request.GET.get("advisor")
        email = request.user.email
        student = Student.objects.filter(email=email).last()
        advisor = Advisor.objects.filter(id=advisor_ID).last()
        username = student.name

    room = str(advisor.id) + "-" + str(student.id)
    if Room.objects.filter(name=room).exists():
        return HttpResponseRedirect('/advisor_app/chat/'+room+'/?username='+username)
    else:
        new_room = Room.objects.create(name=room, student_name=student.name, advisor_name = advisor.name)
        new_room.save()
        return HttpResponseRedirect('/advisor_app/chat/'+room+'/?username='+username)

def send(request):
    message = request.POST['message']
    username = request.POST['username']
    room_id = request.POST['room_id']
    new_message = Message.objects.create(value=message, user=username, room=room_id)
    new_message.save()
    return HttpResponse('Message sent successfully')

def getMessages(request, room):
    room_details = Room.objects.get(name=room)

    messages = Message.objects.filter(room=room_details.id)
    return JsonResponse({"messages":list(messages.values())})