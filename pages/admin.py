from django.contrib import admin
from .models import Contact, Apec, LandingPage


class ContactAdmin(admin.ModelAdmin):
	list_display = ('email', 'first_name', 'last_name', 'objets')

class LandingPageAdmin(admin.ModelAdmin):
	list_display = ('email', 'first_name', 'last_name', 'company', 'landing', 'date_created')
	list_filter = ('landing',)
	search_fields = ('company', 'email', 'company')

class ApecAdmin(admin.ModelAdmin):
	list_display = ('titre', 'nom', 'prenom', 'email', 'phone', 'age', 'publication', 'sent')
	list_filter = ('dispo', 'region', 'sent')
	search_fields = ('titre', 'formation', 'experience', 'ville', 'nom', 'prenom')


admin.site.register(Contact, ContactAdmin) 
admin.site.register(Apec, ApecAdmin) 
admin.site.register(LandingPage, LandingPageAdmin)
