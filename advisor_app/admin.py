from django.contrib import admin
from .models import AppUser, Course, Student, Advisor, Schedule, Room, Message

# Register your models here.
class AppUserAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['user']}),
        (None, {'fields': ['is_advisor']}),
    ]

class CourseAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['title']}),
        (None, {'fields': ['department']}),
        (None, {'fields': ['catalog_nbr']}),
        (None, {'fields': ['section']}),
        (None, {'fields': ['meetings']}),
        (None, {'fields': ['credit']}),
        (None, {'fields': ['component']}),
    ]

class StudentAdmin(admin.ModelAdmin):
    fieldsets = [
    (None, {'fields': ['userID']}),
    (None, {'fields': ['name']}),
    (None, {'fields': ['computingID']}),
    (None, {'fields': ['email']}),
    (None, {'fields': ['year']}), 
    (None, {'fields': ['department']}), 
    (None, {'fields': ['majors']}), 
    (None, {'fields': ['minors']}),  
    (None, {'fields': ['advisors']}),  
    (None, {'fields': ['schedules']}), 
    ]   

class AdvisorAdmin(admin.ModelAdmin):
    fieldsets = [
    (None, {'fields': ['userID']}),
    (None, {'fields': ['name']}),
    (None, {'fields': ['email']}),
    (None, {'fields': ['computingID']}),
    (None, {'fields': ['department']}),
    (None, {'fields': ['students']}),
    ]

class ScheduleAdmin(admin.ModelAdmin):
    fieldsets = [
    (None, {'fields': ['name']}), 
    (None, {'fields': ['student']}), 
    (None, {'fields': ['courses']}),
    (None, {'fields': ['credit']}),
    (None, {'fields': ['pending_approval']}),
    (None, {'fields': ['isapproved']}),
    ]

class RoomAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']}), 
    ]

class MessageAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['value']}), 
        (None, {'fields': ['date']}),
        (None, {'fields': ['user']}),
        (None, {'fields': ['room']}),    
    ]


admin.site.register(AppUser, AppUserAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Advisor, AdvisorAdmin)
admin.site.register(Schedule, ScheduleAdmin)
admin.site.register(Room, RoomAdmin)
admin.site.register(Message, MessageAdmin)
