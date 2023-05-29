import json
from django.db import models
from django.contrib.auth.models import User
from advisor_app.nonmodel_methods import overlaps
from django.http import JsonResponse
from datetime import datetime

class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_advisor = models.BooleanField()

    @classmethod
    def create(cls, user, is_advisor):
        a = cls(user=user, is_advisor=is_advisor)
        a.save()
    def __str__(self):
        s = self.user.first_name + " " + self.user.last_name
        return s



# Course class, used for a single class
class Course(models.Model):
    title = models.CharField(max_length=300)
    department = models.CharField(max_length=300)
    section = models.CharField(max_length=300)
    catalog_nbr = models.CharField(default='0000', max_length=300)
    meetings = models.JSONField(default=dict)  # includes days, start_time, end_time, and instructor
    credit = models.CharField(default='3', max_length=300)  # made this a CharField since some courses have a range of credits like '1 - 3'
    component = models.CharField(default="LEC", max_length=300)
    def __str__(self):
        s = self.department + " " + str(self.catalog_nbr) + "-" + self.section + ": " + self.title + " (" + self.component + ")"
        return s
    def equals(self, course):
        return (self.department==course.department and self.section==course.section) and (
            self.component==course.component and self.catalog_nbr==course.catalog_nbr)


# Some methods for accessing data in the meetings JSONField:
    def get_days(self):
        try:
            days = self.meetings[0]['days']
            if days == "-":
                return ""
            return days
        except IndexError:
            return ""

    def get_start_time(self):
        try:
            time_string = self.meetings[0]['start_time']
            if time_string == "-" or time_string == "":
                return ""
            m = "am"
            hour = int(time_string[0:2])
            if hour > 12:
                hour -= 12
                m = "pm"
            if hour == 12:  # I'm assuming there's no midnight courses
                m = "pm"
            minute = time_string[3:5]
            return str(hour) + ":" + minute + m
        except IndexError:
            return ""

    def get_end_time(self):
        try:
            time_string = self.meetings[0]['end_time']
            if time_string == "-" or time_string == "":
                return ""
            m = "am"
            hour = int(time_string[0:2])
            if hour > 12:
                hour -= 12
                m = "pm"
            if hour == 12:
                m = "pm"
            minute = time_string[3:5]
            return str(hour) + ":" + minute + m
        except IndexError:
            return ""

    def is_ranged(self):
        try:
            int(self.credit)
            return False
        except ValueError:
            return True

    def max_credits(self):
        try:
            return int(self.credit)
        except ValueError:
            return int(self.credit[4:])

    def min_credits(self):
        return int(self.credit[0])

# Schedule class, used to manage courses within a schedule
class Schedule(models.Model):
    # Initialize a blank schedule
    # @params: Student object
    name = models.CharField(max_length=50)
    student = models.CharField(max_length=100) #changed length from 10 to 100 (bandaid solution)
    courses = models.ManyToManyField(Course) #changed from JSONField to ManyToManyField; used to models.JSONField(default=list)
    credit = models.IntegerField(default=0)
    course_creds = models.JSONField(default=dict) 
    pending_approval = models.BooleanField(default=False) #A variable for advisors to view schedules that were sent for approval

    #---------------------- 
    isapproved = models.BooleanField(default=False) #Attempting to Develop a course approval structure
    isrejected = models.BooleanField(default=False)

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

    #----------------------

    # Adds a Course object
    # @params: Course object    
    def add_course(self, course):
        if course not in self.courses.all():
            self.courses.add(course)
            try:  # solution for avoiding ValueError from courses with range of credits
                creds = int(course.credit)
            except ValueError:
                s = course.credit[4:]
                creds = int(s)
            self.credit += creds
            self.course_creds[str(course.id)] = creds
            self.pending_approval = False
            self.isapproved = False
            self.isrejected = False
            self.save()
            return

    # Removes course from course list
    def remove_course(self, course):
        if course in self.courses.all():
            self.courses.remove(course)
            creds = self.course_creds[str(course.id)]
            self.credit -= creds
            self.course_creds[str(course.id)] = 0
            self.pending_approval = False
            self.isapproved = False
            self.isrejected = False
            self.save()
            return

    def has_conflict(self):
        for course1 in self.courses.all():
            if course1.get_start_time() == "":
                continue
            else:
                days_string1 = course1.get_days()
                days_list1 = []
                for i in range(0, len(days_string1), 2):
                    days_list1.append(days_string1[i:i+2])
                start_time_string1 = course1.meetings[0]['start_time']
                start_hour1 = int(start_time_string1[0:2])
                start_minute1 = int(start_time_string1[3:5]) / 60
                end_time_string1 = course1.meetings[0]['end_time']
                end_hour1 = int(end_time_string1[0:2])
                end_minute1 = int(end_time_string1[3:5]) / 60
                start_time1 = start_hour1 + start_minute1
                end_time1 = end_hour1 + end_minute1
                for course2 in self.courses.all():
                    if course2.get_start_time() == "" or course1 == course2:
                        continue
                    else:
                        days_string2 = course2.get_days()
                        shared_days = 0
                        for i in range(0, len(days_string2), 2):
                            day = days_string2[i:i+2]
                            if day in days_list1:
                                shared_days += 1
                                break
                        if shared_days > 0:
                            start_time_string2 = course2.meetings[0]['start_time']
                            start_hour2 = int(start_time_string2[0:2])
                            start_minute2 = int(start_time_string2[3:5]) / 60
                            start_time2 = start_hour2 + start_minute2
                            if start_time1 <= start_time2 <= end_time1:
                                return True
        return False

    # Checks if a schedule is valid
    def validate(self):
        # Check if there are any time conflicts
        does_overlap, instances = overlaps(self.courses.all())
        if does_overlap:
            return False, "time conflict", instances
        # Check if schedule is not above credit minimum and maximum
        if int(self.credit)<12:
            return False, "credit minimum", self.credit
        if int(self.credit)>19: 
            return False, "credit maximum", self.credit
        return True, "valid", None
    #to be changed
    '''
    def __str__(self):
        for i in self.courses:
            print(i)
        return
    '''

    def particular_course_credits(self, course):
        if course in self.courses.all():
            return self.course_creds[str(course.id)]
        return 0

    def change_credits(self, course, new_creds):
        if course in self.courses.all() and course.min_credits() <= new_creds <= course.max_credits():
            old_creds = self.course_creds[str(course.id)]
            self.credit -= old_creds
            self.credit += new_creds
            self.course_creds[str(course.id)] = new_creds
            self.pending_approval = False
            self.isapproved = False
            self.isrejected = False
            self.save()
        return

    def __str__(self):
        return self.name

   
# Student model
class Student(models.Model):
    userID = models.CharField(max_length=100) #bandaid solution
    name = models.CharField(max_length=50)
    computingID = models.CharField(max_length=10)
    email = models.CharField(max_length=100,default="") #Field created in case we need to distinguish between the computing ID and email later on
    year = models.IntegerField(default=1)
    department = models.JSONField(default=list)
    majors = models.JSONField(default=list)
    minors = models.JSONField(default=list)
    advisors = models.JSONField(default=list) #Will work around it
    schedules = models.JSONField(default=list) #Will work around it
    # @params: ID of advisor
    def add_advisor(self, advisorID):
        self.advisor.add(advisorID) #Changed from append to add (manytomany field)
    # @params: Student object
    def equals(self, student):
        return self.computingID==student.computingID
    def __str__(self):
        return self.name + self.computingID + str(self.year)

# Advisor class
class Advisor(models.Model):
    userID = models.CharField(max_length=100) #bandaid solution
    name = models.CharField(max_length=50)
    computingID = models.CharField(max_length=10)
    email = models.CharField(max_length=100,default="") #Field created in case we need to distinguish between the computing ID and email later on
    department = models.JSONField(default=list)
    students = models.ManyToManyField(Student) 
    #schedules = models.ManyToManyField(Schedule) #A list of schedules sent by the advisor's students 
    # @params: ID of student
    def add_student(self, student):
        if student not in self.students.all():
            self.students.add(student) #Changed from append to add (manytomany field)
            self.save()
            return

    def remove_student(self, student):
        print(self.students.all())
        if student in self.students.all():
            self.students.remove(student)
            self.save()
            return
    # @params: Advisor object
    def equals(self, advisor):
        return self.computingID==advisor.computingID

"""
REFERENCES
Title:  django-chat-app
Author: Tomi Tokko
Date: Apr 18, 2021
Code version: 1
URL: https://github.com/tomitokko/django-chat-app/commits?author=tomitokko
"""
#Chatroom class
class Room(models.Model):
    name = models.CharField(max_length=100)
    student_name = models.CharField(max_length=100)
    advisor_name = models.CharField(max_length=100)

#Message class
class Message(models.Model):
    value = models.CharField(max_length=1000000)
    date = models.DateTimeField(default=datetime.now, blank=True)
    user = models.CharField(max_length=1000000)
    room = models.CharField(max_length=1000000)

    def __str__(self):
        return self.user + " - " +  self.value