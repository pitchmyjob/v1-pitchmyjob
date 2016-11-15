from dal import autocomplete
from members.models import Member
from pro.models import Job

class JobAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Job.objects.none()

        qs = Job.objects.all()

        if self.q:
            qs = qs.filter(job_title__istartswith=self.q)

        return qs.distinct()


class MemberAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Member.objects.none()

        qs = Member.objects.all()

        if self.q:
            qs = qs.filter(email__istartswith=self.q)

        return qs.distinct()