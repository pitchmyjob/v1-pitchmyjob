from django.contrib import admin
from .models import Cv, CvExperience
from myc2v.autocomplete.forms import CvFormAutocomplete


class CVAdmin(admin.ModelAdmin):
	list_display = ('id', 'first_name', 'last_name', 'email', 'site')
	form = CvFormAutocomplete

admin.site.register(Cv, CVAdmin)
admin.site.register(CvExperience)