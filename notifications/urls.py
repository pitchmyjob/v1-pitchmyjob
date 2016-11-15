from django.conf.urls import url
from . import views
from . import notifications
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^notif-message/(?P<pk>\d+)$', views.message, name='message'),
    url(r'^get-notification$', views.get_notification, name='get-notification'),

    url(r'^cron/test$', notifications.test_cron, name='cron-test'),
]