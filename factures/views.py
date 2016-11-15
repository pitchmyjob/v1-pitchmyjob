# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from pro.models import Pro, Job
from .models import Facture, PaymentLink
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from c2v.views import render_to_pdf
from .paiement import Paiement
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User, Group
from django.contrib import messages
import datetime

@login_required()
def generate_facture(request, pk):
	facture = Facture.objects.filter(id=pk, user=request.user)
	if facture.exists():
		facture = facture.first()
		return render_to_pdf('factures/facture.html', {'facture': facture}, "facture-"+str(facture.id) ) 
	else:
		return HttpResponseRedirect( reverse('pro:factures') )

@login_required()
def payment_link(request, slug):
	if not request.user.groups.filter(name='pro').exists():
		return HttpResponseRedirect( reverse('pro:login') )

	link = PaymentLink.objects.filter(link=slug, user=request.user, paid=False)
	if link.exists() is False:
		return HttpResponseRedirect( reverse('pro:offres') )

	link = link.first()
	amount = float(link.prix_ht)*float(1.20)*float(100)
	p = Paiement(int(amount), 2, request.user.id, link.id, normal_return="http://www.pitchmyjob.com/pro/lien-paiement/retour", cancel_return="http://www.pitchmyjob.com/pro/lien-paiement/retour")
	code = p.call_request()
	html = code[3]

	return HttpResponse( render(request, 'factures/pro-lien-paiement.html', {'object' : link, 'code' : html} ) )


@csrf_exempt
def paiement_auto_response(request):
	from django.core.mail import send_mail
	
	if request.method == 'POST':
		p = Paiement()
		data = request.POST.get('DATA')
		data = p.response(data)
		type_paiement = str(data['data'])	

		if type_paiement == "1":
			user = User.objects.get(id=data['customer_id'])
			job = Job.objects.get(id=data['order_id'])
			job.complet=True
			job.active=True
			job.save()
			if str(data['bank_response_code']) == "00" :
				job.paid=True
				job.date_posted=datetime.datetime.now() 
				job.save()
				facture = Facture(user=user, job=job, type_facture=1, first_name=user.pro.first_name, last_name=user.pro.last_name, company=user.pro.company)
				facture.adresse = str(user.pro.street_number)+" "+str(user.pro.route)
				facture.cp = user.pro.cp
				facture.city = user.pro.locality
				facture.email = user.pro.email
				facture.designation  = "Publication offre d'emploi"
				facture.reference  = job.id
				facture.quantite  = 1
				prix_ttc  = float(data['amount']) / 100
				facture.prix_ttc = float(prix_ttc)
				facture.save()

		if type_paiement == "2":
			user = User.objects.get(id=data['customer_id'])
			link = PaymentLink.objects.get(id=data['order_id'])

			if str(data['bank_response_code']) == "00" :
				link.paid=True
				link.save()
				pro = user.pro
				pro.credit_job = pro.credit_job + link.credit_job
				pro.save()
	
				facture = Facture(user=user, type_facture=2, first_name=user.pro.first_name, last_name=user.pro.last_name, company=user.pro.company)
				facture.adresse = str(user.pro.street_number)+" "+str(user.pro.route)
				facture.cp = user.pro.cp
				facture.city = user.pro.locality
				facture.email = user.pro.email
				facture.designation  = link.designation
				facture.reference  = "LP"+str(link.id)
				facture.quantite  = 1
				prix_ttc  = float(data['amount']) / 100
				facture.prix_ttc = float(prix_ttc)
				facture.save()

	return HttpResponse() 


@login_required()
@csrf_exempt
def return_payement_link(request):
	if request.method == 'POST':
		p = Paiement()
		data = request.POST.get('DATA')
		data = p.response(data)

		if not data :
			return HttpResponseRedirect( reverse('pro:offres') )

		link = PaymentLink.objects.filter(id=data['order_id'])
		if link.exists() is False:
			return HttpResponseRedirect( reverse('pro:offres') )

		link = link.first()

		if str(data['bank_response_code']) == "00" :
			paid = True
		else:
			paid = False

		return HttpResponse( render(request, 'factures/retour-lien-paiement.html',  {'paid' : paid, 'object' : link} ) )
	else:
		return HttpResponseRedirect( reverse('pro:offres') ) 

@csrf_exempt
def paiement_offre(request):
	if request.method == 'POST':
		p = Paiement()
		data = request.POST.get('DATA')
		data = p.response(data)
		type_paiement = str(data['data'])
		job = Job.objects.get(id=data['order_id'])
		job.complet=True
		job.active=True
		job.save()
		if str(data['bank_response_code']) == "00" :
			messages.add_message(request, messages.SUCCESS, 'Paiement accepté : Votre offre a été publié pour une durée de 30 jours.')
		else:
			messages.add_message(request, messages.ERROR, 'Paiement refusé.')

	return HttpResponseRedirect( reverse('pro:offres') ) 