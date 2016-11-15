"""myc2v URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls import patterns
from django.conf import settings
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView

sitemaps = {
    'static': StaticViewSitemap,
}

urlpatterns = i18n_patterns(
	url(r'^', include('members.urls', namespace="members")),
    url(r'^', include('pro.urls', namespace="pro")),
    url(r'^', include('c2v.urls', namespace="c2v")),
    url(r'^', include('pages.urls', namespace="pages")),
    url(r'^', include('notifications.urls', namespace="notifications")),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
	url(r'^admin/', admin.site.urls),
    url(r'^autocomplete/', include('myc2v.autocomplete.urls', namespace="autocomplete")),
)

urlpatterns += [
    url(r'^', include('api.urls', namespace="api")),
    url(r'^', include('factures.urls', namespace="factures")),
    url(r'^robots.txt$', TemplateView.as_view(template_name="robots.txt"), name='robots'),
]

urlpatterns += [
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT} )
]
