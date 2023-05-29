from django import forms
from django.contrib.auth.models import User
from .models import Schedule, AppUser, Advisor, Student

CHOICES = [('S', 'Student'), ('A', 'Advisor')]
APPROVAL = [('Y', 'Approve'), ('N', 'Don\'t Approve')]



class CreateAccountForm(forms.Form):
    role = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)

class ScheduleForm(forms.Form):
    name = forms.CharField()

class AddCourseForm(forms.Form):
    schedule = forms.ModelChoiceField(queryset=Schedule.objects.none())
    
    def __init__(self, user, *args, **kwargs):
        super(AddCourseForm, self).__init__(*args, **kwargs)
        self.fields['schedule'].queryset = Schedule.objects.filter(student=user.email)


class ChangeCreditsForm(forms.Form):
    creds = forms.IntegerField(min_value=1, label="Credits")

'''
class SendScheduleToAdvisor(forms.Form):
    advisor = forms.ModelChoiceField(queryset=Advisor.objects.all())
'''

class ScheduleApprovalForm(forms.Form):
    approvalStatus = forms.ChoiceField(widget=forms.RadioSelect, choices=APPROVAL) #why is printing this
    #schedule = forms.ModelChoiceField(queryset=Schedule.objects.all())
    #def cleaned_data(self):

     #   return self.cleaned_data 

class AddStudentForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all())




