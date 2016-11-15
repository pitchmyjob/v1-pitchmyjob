from django import template
from django.conf import settings
from datetime import date

register = template.Library()

@register.filter()
def age(value):
	if value:
		today = date.today()
		return today.year - value.year - ((today.month, today.day) < (value.month, value.day))
	else:
		return None