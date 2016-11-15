from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^mycv/$', views.Myc2vView.as_view(), name='myc2v'),
    url(r'^myc2v/connexion$', views.Myc2vLoginView, name='myc2v_login'),
    url(r'^myc2v/theme$', views.theme, name='myc2v-theme'),
    url(r'^myc2v/webcam$', views.webcam, name='youtube'), 
    url(r'^myc2v/download$', views.download, name='download'), 
    url(r'^myc2v/audio$', views.audio, name='audio'), 
    url(r'^myc2v/upload_audio$', views.upload_audio, name='upload_audio'), 
    url(r'^cv/(?P<pk>\d+)-(?P<slug>[-\w\d]+)$$', views.C2vView, name='c2v_view'),
    url(r'^cv/linkedin$', views.ManualImportLinkedin, name='manual-import'),
]