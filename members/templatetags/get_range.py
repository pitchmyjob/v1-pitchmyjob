from django import template
from django.conf import settings

register = template.Library()

@register.filter()
def get_range(value):
	if value :
		return range(value)
	else:
		return ""