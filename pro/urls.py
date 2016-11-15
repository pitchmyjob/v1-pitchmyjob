from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^pro/$', views.home, name='home'),
    url(r'^pro/home$', views.home_2, name='home_2'),
    url(r'^pro/login$', views.login_view, name='login'),
    url(r'^pro/inscription$', views.InscriptionCreate.as_view(), name='inscription'),
    url(r'^pro/inscription/step-2$', views.InscriptionStepTwoUpdate.as_view(), name='inscription-step-2'),
    url(r'^pro/inscription/(?P<slug>[-\w\d]+)$', views.InscriptionProUpdate.as_view(), name='inscription-pro'),
    url(r'^pro/profil$', views.ProfilUpdate.as_view(), name='profil'),
    url(r'^pro/offres$', views.ListeOffreView.as_view(), name='offres'),
    url(r'^pro/offres/(?P<pk>\d+)/confirm-delete$', views.OffreDelete.as_view(), name='delete-offre'),
    url(r'^pro/offre/(?P<pk>\d+)/candidatures$', views.JobCandidaturesView.as_view(), name='job-candidatures'),
    url(r'^pro/offre/(?P<slug>\d+)/candidature/(?P<pk>\d+)$', views.JobReponseCandidatureView.as_view(), name='job-reponse-candidature'),
    url(r'^pro/job-create/step-1$', views.JobStepOneCreate.as_view(), name='job-create'),
    url(r'^pro/job/(?P<pk>\d+)/step-1$', views.JobStepOneUpdate.as_view(), name='job-step-1'),
    url(r'^pro/job/(?P<pk>\d+)/step-2$', views.JobStepTwoUpdate.as_view(), name='job-step-2'),
    url(r'^pro/job/(?P<pk>\d+)/step-3$', views.JobStepTreeUpdate.as_view(), name='job-step-3'),
    url(r'^pro/job/(?P<pk>\d+)/step-4$', views.JobStepFourUpdate.as_view(), name='job-step-4'),
    url(r'^pro/job/(?P<pk>\d+)/step-5$', views.JobStepFiveUpdate.as_view(), name='job-step-5'),
    url(r'^pro/cv-theque$', views.C2vThequeList.as_view(), name='c2v-theque'),
    url(r'^pro/cv-theque/(?P<pk>\d+)$', views.C2vThequeDetail.as_view(), name='c2v-theque-candidat'),
    url(r'^pro/messages$', views.MessagesTemplateView.as_view(), name='messages'),
    url(r'^pro/message/(?P<pk>\d+)$', views.MessageTemplateView.as_view(), name='message'),
    url(r'^pro/credits/$', TemplateView.as_view(template_name="pro/credits.html"), name='credits'),
    url(r'^pro/mon-compte/$', views.MyAccountUpdate.as_view(), name='my-account'), 
    url(r'^pro/mon-compte/password$', views.MyAccountPasswordUpdate.as_view(), name='my-account-password'), 
    url(r'^pro/factures$', views.FactureListView.as_view(), name='factures'),
]