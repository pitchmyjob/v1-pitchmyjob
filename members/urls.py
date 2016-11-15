from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

from socialnetwork import sn_views

urlpatterns = [
    #url(r'^$', views.home, name='home'),
    #url(r'^login$', views.login_view, name='login'),
    url(r'^$', views.HomeInscriptionCreate.as_view(), name='home'),
    #url(r'^login/refonte$', views.login_view_refonte, name='login_refonte'),
    url(r'^disable', views.disable_account, name='disable_account'),
    url(r'^logout', views.logout_view, name='logout'),
    url(r'^login$', views.login_view_refonte, name='login'),
    url(r'^inscription$', views.InscriptionCreate.as_view(), name='inscription'),
    url(r'^invitation$', views.invitation, name='invitation'),
    url(r'^inscription/step-2$', views.InscriptionStepTwoUpdate.as_view(), name='inscription-step-2'),
    url(r'^entreprises$', views.ProList.as_view(), name='list-pro'),
    url(r'^entreprise/(?P<pk>\d+)$', views.ProDetail.as_view(), name='detail-pro'),
    url(r'^annonces$', views.JobList.as_view(), name='list-job'), 
    url(r'^annonces/(?P<pk>\d+)-(?P<slug>[-\w\d]+)$', views.JobListEntreprise.as_view(), name='list-job-pro'), 
    url(r'^annonce/(?P<pk>\d+)$', views.JobDetail.as_view(), name='detail-job'),
    url(r'^annonce/(?P<pk>\d+)/ma-candidature$', views.CandidatureDetail.as_view(), name='detail-candidature'),

    #url(r'^annonce/(?P<pk>\d+)/candidature$', views.CandidatureStepOne.as_view(), name='candidature-1'),
    url(r'^annonce/(?P<pk>\d+)/candidature$', views.refonte_candidature, name='candidature-1'),


    url(r'^annonce/(?P<pk>\d+)/candidature/validation$', views.CandidatureStepTwo, name='candidature-2'),
    url(r'^annonce/(?P<job>\d+)/candidature/(?P<cd>\d+)/mode$', views.CandidatureStepThree, name='candidature-3'),
    url(r'^annonce/(?P<job>\d+)/candidature/(?P<cd>\d+)/question/(?P<nb>\d+)$', views.CandidatureStepFour, name='candidature-4'),
    url(r'^annonce/(?P<job>\d+)/candidature/(?P<cd>\d+)/questions$', views.CandidatureStepFourVideo, name='candidature-4-video'),
    url(r'^annonce/(?P<job>\d+)/candidature/(?P<cd>\d+)/felicitation$', views.CandidatureStepFive, name='candidature-5'),
    url(r'^profil/$', views.MyAccountUpdate.as_view(), name='my-account'),
    url(r'^profil/informations$', views.MyAccountInformationUpdate.as_view(), name='my-account-information'),
    url(r'^profil/password$', views.MyAccountPasswordUpdate.as_view(), name='my-account-password'),
    url(r'^mes-candidatures/$', views.MyCandidatureJob.as_view(), name='mes-candidatures-offre'),
    url(r'^mes-candidatures/interesse', views.MyCandidatureInterestJob.as_view(), name='mes-candidatures-offre-interest'),
    url(r'^messages$', views.MessagesTemplateView.as_view(), name='messages'),
    url(r'^message/(?P<pk>\d+)$', views.MessageTemplateView.as_view(), name='message'),
    url(r'^test$', views.test, name='test'),
    url(r'^ajax/list-job-suggested$', views.SuggestedJobList.as_view(), name='ajax-list-job-suggested'),
    url(r'^sn/doyoubuzz-connect$', sn_views.doyoubuzz_connect, name='doyoubuzz-connect'),
    url(r'^sn/doyoubuzz-return$', sn_views.doyoubuzz_return, name='doyoubuzz-return'),
    url(r'^sn/password$', sn_views.SnConnectPassword.as_view(), name='sn-password'),
    url(r'^sn/linkedin-connect$', sn_views.linkedin_connect, name='linkedin-connect'),
    url(r'^sn/linkedin-return$', sn_views.linkedin_return, name='linkedin-return'),
    url(r'^sn/facebook-connect$', sn_views.facebook_connect, name='facebook-connect'),
    url(r'^sn/facebook-return$', sn_views.facebook_return, name='facebook-return'),
    url(r'^sn/viadeo-connect$', sn_views.viadeo_connect, name='viadeo-connect'),
    url(r'^sn/viadeo-return', sn_views.viadeo_return, name='viadeo-return'),
    #url(r'^home/refonte$', views.HomeInscriptionCreate.as_view(), name='home-refonte'),
]