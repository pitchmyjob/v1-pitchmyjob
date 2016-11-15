from django.contrib import sitemaps
from django.core.urlresolvers import reverse
from pro.models import Job

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return Job.objects.filter(active=True)