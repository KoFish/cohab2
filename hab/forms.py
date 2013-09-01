from django import forms
from django.contrib.auth.models import User
from hab.models import IMPORTANCE

class CreateAssignmentForm(forms.Form):
    verb = forms.CharField(max_length=50)
    subject = forms.CharField(max_length=50)
    owner = forms.ModelChoiceField(queryset=User.objects.all())
    importance = forms.ChoiceField(widget=forms.Select(attrs={'class': 'grade'}), choices=IMPORTANCE)
    deadline = forms.CharField(required=False, help_text='Deadline in number of days from today')
    mine = forms.BooleanField(required=False)
    repeat = forms.BooleanField(required=False)
    repeat_delay = forms.CharField(required=False, help_text='Number of days between creating new assignments')
    allowed_owners = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)

    def __init__(self, *a, **kw):
        super(CreateAssignmentForm, self).__init__(*a, **kw)
        self.fields['allowed_owners'].initial = User.objects.all()

class CreateViewAssignmentForm(forms.Form):
    subject = forms.CharField(max_length=50)
    importance = forms.ChoiceField(widget=forms.Select(attrs={'class': 'grade'}), choices=IMPORTANCE)
    deadline = forms.CharField(required=False, help_text='Deadline in number of days from today')
    mine = forms.BooleanField(required=False)

