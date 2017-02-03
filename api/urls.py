from django.conf.urls import url
from . import views

from pages.views import xml_indeed, xml_optioncarriere, xml_jobrapido, xml_jobijoba

urlpatterns = [
    url(r'^api/token-auth/', 'rest_framework.authtoken.views.obtain_auth_token'),
    url(r'^api/media$', views.MediaDetail.as_view() ),
    url(r'^api/video/url$', views.VideoDetail.as_view() ),
    url(r'^api/video/record$', views.VideoRecordDetail.as_view() ),
    url(r'^api/video/entretien$', views.VideoRecordEntretien.as_view() ),
    url(r'^api/video/entretien/time$', views.VideoRecordEntretienTime.as_view() ),
    url(r'^api/mycv$', views.MycvDetail.as_view() ),
    url(r'^api/mycv/experience$', views.MycvExperienceList.as_view() ),
    url(r'^api/mycv/experience/(?P<pk>[0-9]+)$', views.MycvExperienceDetail.as_view() ),
    url(r'^api/mycv/formation$', views.MycvFormationList.as_view() ),
    url(r'^api/mycv/formation/(?P<pk>[0-9]+)$', views.MycvFormationDetail.as_view() ),
    url(r'^api/mycv/skill$', views.MycvSkillList.as_view() ),
    url(r'^api/mycv/skill/(?P<pk>[0-9]+)$', views.MycvSkillDetail.as_view() ),
    url(r'^api/mycv/language$', views.MycvLanguageList.as_view() ),
    url(r'^api/mycv/language/(?P<pk>[0-9]+)$', views.MycvLanguageDetail.as_view() ),
    url(r'^api/mycv/interest$', views.MycvInterestList.as_view() ),
    url(r'^api/mycv/interest/(?P<pk>[0-9]+)$', views.MycvInterestDetail.as_view() ),
    url(r'^api/audio/entretien$', views.AudioRecordEntretien.as_view() ),
    url(r'^api/import/linkedin$', views.ImportLinkedin.as_view() ),
    url(r'^api/metier$', views.MetierList.as_view() ),
    url(r'^api/send-c2v-email$', views.SendC2VEmail.as_view() ),
    url(r'^api/decline-candidature$', views.DeclineCandidature.as_view() ),
    url(r'^api/send-invitation$', views.SendInvitationAnnonce.as_view() ),
    url(r'^api/send-demande-entretien', views.SendDemandeEntretien.as_view() ),
    url(r'^api/messages$', views.GroupMessage.as_view() ),
    url(r'^api/message/(?P<pk>[0-9]+)$', views.MessagesList.as_view() ),
    url(r'^api/notifications$', views.NotificationList.as_view() ),
    url(r'^api/jobs', views.JobApiList.as_view() ),
    url(r'^api/verification-cv', views.VerificationCvApply.as_view() ),
    url(r'^api/verification-email', views.VerificationEmail.as_view() ),

    url(r'^api/video/question$', views.VideoQuestionEntretien.as_view()),
    url(r'^api/video/question/params', views.VideoQuestionEntretienParams.as_view()),
    url(r'^api/entretien/close', views.ValideEntretien.as_view()),

    url(r'^xml/flatchr-4gdp54F', xml_indeed, name='xml_indeed'),
    url(r'^xml/indeed-gR94mDf5c6', xml_indeed, name='xml_indeed'),
    url(r'^xml/optioncarriere-gR94mDf5c6', xml_optioncarriere, name='xml_optioncarriere'),
    url(r'^xml/jobrapido', xml_jobrapido, name='xml_jobrapido'),
    url(r'^xml/jobijoba-8fmePfS19d5', xml_jobijoba, name='xml_jobijoba'),

    url(r'^api/export/member/gde561fmlsdf5646sdfkjsdf5213dfg', views.FullDataBaseMember.as_view(), name='exporte'),
]