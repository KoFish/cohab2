from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _, ugettext_lazy as __
from hab.models import IMPORTANCE

class CreateAssignmentForm(forms.Form):
    verb = forms.CharField(label=__("Verb"), max_length=50)
    subject = forms.CharField(label=__("Subject"), max_length=50)
    owner = forms.ModelChoiceField(label=__("Owner"), queryset=User.objects.all())
    importance = forms.ChoiceField(label=__("Importance"), widget=forms.Select(attrs={'class': 'grade'}), choices=IMPORTANCE)
    deadline = forms.CharField(label=__("Deadline"), required=False, help_text=_('Deadline in number of days from today'))
    mine = forms.BooleanField(label=__("Mine"), required=False)
    repeat = forms.BooleanField(label=__("Repeat"), required=False)
    repeat_delay = forms.CharField(label=__("Repeat delay"), required=False, help_text=_('Number of days between creating new assignments'))
    allowed_owners = forms.ModelMultipleChoiceField(label=__("allowed owners"), queryset=User.objects.all(), required=False)

    def __init__(self, *a, **kw):
        super(CreateAssignmentForm, self).__init__(*a, **kw)
        self.fields['allowed_owners'].initial = User.objects.all()

class CreateViewAssignmentForm(forms.Form):
    subject = forms.CharField(label=__("Subject"), max_length=50)
    importance = forms.ChoiceField(label=__("Importance"), widget=forms.Select(attrs={'class': 'grade'}), choices=IMPORTANCE)
    deadline = forms.CharField(label=__("Deadline"), required=False, help_text=_('Deadline in number of days from today'))
    mine = forms.BooleanField(label=__("Mine"), required=False)

