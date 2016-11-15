from django.conf.urls import url
from . import autocomplete

urlpatterns = [
    url(
        r'^job-autocomplete$',
        autocomplete.JobAutocomplete.as_view(),
        name='job-autocomplete',
    ),
    url(
        r'^member-autocomplete$',
        autocomplete.MemberAutocomplete.as_view(),
        name='member-autocomplete',
    ),
]