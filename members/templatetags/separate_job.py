from django import template

register = template.Library()

@register.filter()
def separate_job(lists):
	i=0
	for job in lists:
		if job.scraper==False:
			i=i+1
	return i