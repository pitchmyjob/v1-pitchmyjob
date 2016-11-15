from django import template
from django.conf import settings

register = template.Library()

@register.filter()
def web_url(value):
	if value :
		return "http://pitch6.eu-west-1.elasticbeanstalk.com"+value
		return settings.WEB_URL+value
	return ""