from django import template
from members.models import Candidature

register = template.Library()

@register.filter()
def nbcandidature(value):
	return value.filter( active = True, decline=False ).count()

@register.filter()
def candidature_active(value):
	return value.filter(active=True, decline=False).order_by('-date_posted')

@register.filter()
def get_question(value, nb):
	return value.job.questions.filter(nb = nb).first()

@register.filter()
def nboffres(value):
	return value.filter( active = True, complet= True ).count()

@register.filter()
def pro_nbcandidatures(value):
	return Candidature.objects.filter(job__pro = value, active=True).count()