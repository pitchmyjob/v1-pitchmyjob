from django.contrib import admin
from .models import ActivityArea, Contract, Employes, Pro, Job, JobList, ContractTime, JobQuestion, Tag, SearchJob, SeenJob

class ActivityAreaAdmin(admin.ModelAdmin):
	list_display = ('name', 'active')

class ContractAdmin(admin.ModelAdmin):
	list_display = ('name', 'active')

class EmployesAdmin(admin.ModelAdmin):
	list_display = ('name', 'active')

class JobListAdmin(admin.ModelAdmin):
	list_display = ('name', 'active')

class JobQuestionModeleInCommande(admin.TabularInline):
	model = JobQuestion
	verbose_name_plural = 'Questions'


def make_active(modeladmin, request, queryset):
	queryset.update(active=True)
	make_deactive.short_description = "Activer"

def make_deactive(modeladmin, request, queryset):
	queryset.update(active=False)
	make_deactive.short_description = "Desactiver"

class JobAdmin(admin.ModelAdmin):
	inlines = (JobQuestionModeleInCommande,)
	list_display = ('job_title', 'active', 'pro')
	list_filter = ('active', 'scraper_site' )
	search_fields = ('job_title', 'id', 'pro__company', 'company')
	actions=[make_deactive, make_active]

	def get_queryset(self, request):
		return super(JobAdmin,self).get_queryset(request).filter(complet=True)
 
class ProAdmin(admin.ModelAdmin):
	list_display = ('company', 'email', 'first_name', 'last_name')
	search_fields = ('company',)
	list_filter = ('scraper',)


class SeenJobAdmin(admin.ModelAdmin):
	list_display = ('member', 'job', 'date_seen')
	readonly_fields = ('date_seen',) 

class TagAdmin(admin.ModelAdmin):
	list_display = ('name',)
	search_fields = ('name',)



admin.site.register(ActivityArea, ActivityAreaAdmin)
admin.site.register(Contract, ContractAdmin) 
admin.site.register(Employes, EmployesAdmin) 
admin.site.register(Pro, ProAdmin) 
admin.site.register(Job, JobAdmin) 
#admin.site.register(ContractTime) 
admin.site.register(JobList, JobListAdmin) 
admin.site.register(Tag, TagAdmin) 
admin.site.register(SearchJob) 
admin.site.register(SeenJob, SeenJobAdmin) 
