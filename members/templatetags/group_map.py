from django import template
from django.core.urlresolvers import reverse

register = template.Library()

@register.filter()
def group_map(value):

	tags = []
	for coord in value:
		if coord.latitude and coord.longitude :
			lat = coord.latitude
			lng = coord.longitude

			exist=False

			obj = {'lat':lat, 'lng':lng, 'nb':1, 'job':[], 'id' : coord.id }

			for tag in tags:
				if 'lat' in tag and 'lng' in tag:
					if tag['lng'] == lng and tag['lat'] == lat:
						tag['nb'] = int(tag['nb']) + 1
						tag['job'].append( {'title':coord.job_title, 'link':reverse('members:detail-job', args=[coord.id]) } )
						exist=True

			if exist==False:
				newjob = {'title':coord.job_title, 'link':reverse('members:detail-job', args=[coord.id]) } 
				try:
					newjob['img'] = coord.image['logo100'].url
				except:
					newjob['img']=False

				obj['job'].append( newjob )
				tags.append(obj)


	return tags