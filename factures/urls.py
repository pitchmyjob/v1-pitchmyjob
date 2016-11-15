from django.conf.urls import url
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    url(r'^facture/paiement-auto-response$', views.paiement_auto_response, name='paiement_auto_response'),
    url(r'^pro/facture/(?P<pk>\d+)$', views.generate_facture, name='generate_facture'),  
    url(r'^pro/paiement/(?P<slug>[-\w\d]+)$', views.payment_link, name='payment_link'),
    url(r'^pro/lien-paiement/retour', views.return_payement_link, name='return_payement_link'),
    url(r'^pro/paiement-offre$', views.paiement_offre, name='paiement_offre'),
]