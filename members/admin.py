from django.contrib import admin
from .models import Study, Experience, Member, Video, Candidature, CandidatureReponse, Audio, Interest, Tips
from pro.models import JobQuestion
from django import forms
from myc2v.autocomplete.forms import CandidatureFormAutocomplete
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

class UserAdmin(UserAdmin):
	list_display = ('username', 'email','first_name','last_name', 'date_joined', 'is_staff')


class StudyAdmin(admin.ModelAdmin):
	list_display = ('name', 'active')

class ExperienceAdmin(admin.ModelAdmin):
	list_display = ('name', 'active')

class MemberAdmin(admin.ModelAdmin):
	list_display = ('id', 'email', 'first_name', 'last_name')
	search_fields = ('email', 'first_name', 'last_name')
	list_filter = ('rs_type',)

class CandidatureReponseAdmin(admin.ModelAdmin):
	list_display = ('id', 'candidature', 'nb')

class CandidatureReponseModeleInCandidature(admin.TabularInline):
	model = CandidatureReponse
	can_delete = False
	can_add = False   
	extra = 1
	max_num = 1
	verbose_name_plural = 'Reponses'
	readonly_fields = ('id', 'nb', "text", 'active', "video", "audio", "time")

class CandidatureAdmin(admin.ModelAdmin):
	inlines = (CandidatureReponseModeleInCandidature,)
	list_display = ('id', 'job', 'member', 'date_posted', 'active')
	list_filter = ('active', )
	search_fields = ('job__id', 'job__job_title', 'job__pro__id', 'job__pro__company')
	form = CandidatureFormAutocomplete

class InterestAdmin(admin.ModelAdmin):
	list_display = ('member', 'job', 'date')
	search_fields = ('job__id', 'job__job_title', 'job__pro__id', 'job__pro__company')

class VideoAdmin(admin.ModelAdmin):
	list_display = ('id', 'video_id', 'candidature_reponse', 'member', 'job', 'date_updated')
	search_fields = ('candidature_reponse__id', 'member__id', 'member__email')

	class Media:
		js = ('/static/js/admin/video_id.js',)

admin.site.register(Study, StudyAdmin)
admin.site.register(Experience, ExperienceAdmin) 
admin.site.register(Member, MemberAdmin) 
admin.site.register(Video, VideoAdmin) 
admin.site.register(Audio) 
admin.site.register(Interest, InterestAdmin)
admin.site.register(Candidature, CandidatureAdmin)
admin.site.register(CandidatureReponse, CandidatureReponseAdmin)
admin.site.register(Tips)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)