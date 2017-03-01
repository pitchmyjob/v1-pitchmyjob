from django.conf.urls import url
from . import views
from . import notifications
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^notif-message/(?P<pk>\d+)$', views.message, name='message'),
    url(r'^get-notification$', views.get_notification, name='get-notification'),

    url(r'^cron/test$', notifications.test_cron, name='cron-test'),

    url(r'^cron/multiposting', notifications.async_multiposting, name='async_multiposting'),

    url(r'^cron/flatchr', notifications.cron_import_flatchr, name='cron_import_flatchr'),
    url(r'^flatchr/job/(?P<ref>[-\w\d]+)', notifications.flatchr_job_redirect, name='cron_import_flatchr'),

    url(r'^cron/remixjob', notifications.async_remixjob_import, name='async_remixjob_import'),
    url(r'^cron/jobteaser', notifications.async_jobteaser_import, name='async_jobteaser_import'),

    url(r'^cron/remixjob-check', notifications.remixjob_check, name='remixjob_check'),
    url(r'^cron/jobteaser-check', notifications.jobteaser_check, name='jobteaser_check'),

    url(r'^cron/letudiant', notifications.async_letudiant_import, name='async_letudiant_import'),

    url(r'^scraper/linkedin', notifications.api_rest_scraper_linkedin, name='linkedin_scraper'),
]