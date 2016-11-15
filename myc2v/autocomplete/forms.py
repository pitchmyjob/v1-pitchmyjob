from dal import autocomplete
from members.models import Candidature, Member
from django import forms

class CandidatureFormAutocomplete(forms.ModelForm):
    class Meta:
        model = Candidature
        fields = ('__all__')
        widgets = {
            'job': autocomplete.ModelSelect2(url='/autocomplete/job-autocomplete'),
            'member': autocomplete.ModelSelect2(url='/autocomplete/member-autocomplete'),
        }
