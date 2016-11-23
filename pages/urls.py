from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^log/user/(?P<id>\d+)', views.connect_all_user, name='log_all_user'),
    url(r'^c5507ed7ef50129ee77acb33c55a9066.txt$', TemplateView.as_view(template_name="pages/cgu.html"), name='cgu'),
    url(r'^cgu/$', TemplateView.as_view(template_name="pages/cgu.html"), name='cgu'),
    url(r'^a-propos/$', TemplateView.as_view(template_name="pages/a-propos.html"), name='a-propos'),
    url(r'^presse/$', TemplateView.as_view(template_name="pages/presse.html"), name='presse'),
    url(r'^partenaires/$', TemplateView.as_view(template_name="pages/partenaires.html"), name='partenaires'),
    url(r'^faq/general/$', TemplateView.as_view(template_name="pages/faq-general.html"), name='faq-general'),
    url(r'^faq/c2v/$', TemplateView.as_view(template_name="pages/faq-c2v.html"), name='faq-c2v'),
    url(r'^faq/entretiens-differes/$', TemplateView.as_view(template_name="pages/faq-entretiens-differes.html"), name='faq-entretiens-differes'),
    url(r'^faq/offres-emploi/$', TemplateView.as_view(template_name="pages/faq-offres-emploi.html"), name='faq-offres-emploi'),
    url(r'^contact/$', views.ContactCreate.as_view(), name='contact'), 
    url(r'^password-reset/step1/$', views.ResetPasswordStep1.as_view(), name='reset-password-1'),
    url(r'^password-reset/step2/$', TemplateView.as_view(template_name="pages/reset-password-2.html"), name='reset-password-2'),
    url(r'^password-reset/step3/(?P<token>\w+)$', views.ResetPasswordStep3, name='reset-password-3'),
    url(r'^import/metier', views.import_metier, name='import-metier'),
    url(r'^test-email', views.test_email, name='test-email'),
    url(r'^get-cv', views.get_cv_incompleted, name='get-cv-incompleted'),
    url(r'^accept-invitation', views.invitation_ok, name='invitation_ok'),
    url(r'^test-apec', views.apec, name='apec'),
    url(r'^test-linkedin', views.test_linkedin, name='test-lienk'),
    url(r'^test-doyoubuzz', views.test_doyoubuzz, name='test-doyoubuzz'),
    url(r'^pro/mentions-legales/$', TemplateView.as_view(template_name="pages/mentions-legales.html"), name='mentions-legales'),
    url(r'^pro/a-propos/$', TemplateView.as_view(template_name="pages/a-propos-pro.html"), name='a-propos-pro'),
    url(r'^pro/presse/$', TemplateView.as_view(template_name="pages/presse-pro.html"), name='presse-pro'),
    url(r'^pro/partenaires/$', TemplateView.as_view(template_name="pages/partenaires-pro.html"), name='partenaires-pro'),
    url(r'^pro/tarifs/$', TemplateView.as_view(template_name="pages/tarifs-pro.html"), name='tarifs-pro'),
    url(r'^pro/cgv/$', TemplateView.as_view(template_name="pages/cgv.html"), name='cgv-pro'),
    url(r'^xml/flatchr-4gdp54F', views.xml_indeed, name='xml_indeed'),
    url(r'^xml/indeed-gR94mDf5c6', views.xml_indeed, name='xml_indeed'),
    url(r'^xml/optioncarriere-gR94mDf5c6', views.xml_optioncarriere, name='xml_optioncarriere'),
    url(r'^xml/jobrapido', views.xml_jobrapido, name='xml_jobrapido'),
    url(r'^xml/jobijoba-8fmePfS19d5', views.xml_jobijoba, name='xml_jobijoba'),
    url(r'^emailing', views.emailing, name='emailing'),
    url(r'^recorder', TemplateView.as_view(template_name="pages/recorder.html"), name='cgv-pro'),
    url(r'^react', TemplateView.as_view(template_name="pages/react.html"), name='react'),
    url(r'^whosnext', views.whosnext, name='whosnext'),
    url(r'^broadben', views.import_broadben, name='import_broadben'),
    url(r'^flatchr', views.import_flatchr, name='import_flatchr'),
    url(r'^scraper-apec', views.apec, name='apec'),

    url(r'^pro/offre-speciale$', views.LandingPageCreate.as_view(),name='landing-page'),
    url(r'^pro/offre-speciale/merci$', TemplateView.as_view(template_name="pages/landing-merci.html"), name='landing-page-merci'),

    url(r'^email/candidature-avorte', views.candidature_avorte, name='candidature_avorte'),
]