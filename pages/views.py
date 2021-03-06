# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView, FormView, UpdateView
from django.views.generic.edit import CreateView
from .models import Contact, Apec, LandingPage
from c2v.models import Cv
from members.models import Member
from pro.models import Pro, JobList, Job
from django.contrib import messages
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.core.urlresolvers import reverse
from .forms import ResetPasswordStepOneForm, ResetPasswordStepThreeForm
from django.contrib.auth.models import User
import hashlib, datetime
from django.core.mail import send_mail
from django.contrib.auth import login
from notifications.notifications import async_send_email, reset_password, notification, async_jobteaser_import, async_remixjob_import, async_send_email_attach
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings

class ContactCreate(CreateView):
	model = Contact
	fields = ['first_name', 'last_name', 'email', 'objets', 'message']

	def get_initial(self):
		initial = super(ContactCreate, self).get_initial()
		if self.request.user.is_authenticated() and self.request.user.groups.filter(name='member').exists():
			initial['first_name'] = self.request.user.member.first_name
			initial['last_name'] = self.request.user.member.last_name
			initial['email'] = self.request.user.member.email
		return initial

	def form_valid(self, form):
		form.save()
		message = form.cleaned_data.get('message')
		objet = form.cleaned_data.get('objets')
		email = form.cleaned_data.get('email')
		messages.add_message(self.request, messages.INFO, 'Votre demande a bien été prise en compte et sera traité dans les plus brefs délais.')
		async_send_email("Nouveau contact de %s" % email, ["yannis@pitchmyjob.com", "antoine@pitchmyjob.com", "martial@pitchmyjob.com"], "emails/contact.html", {"message" : message, "objet" : objet})
		return HttpResponseRedirect( reverse('pages:contact') ) 

	def get_template_names(self):
		if self.request.user.is_authenticated() and self.request.user.groups.filter(name='pro').exists():
			return 'pages/contact-pro.html'
		else:
			return 'pages/contact.html'

class ResetPasswordStep1(FormView):
	template_name = 'pages/reset-password-1.html'
	form_class = ResetPasswordStepOneForm 

	def form_valid(self, form):
		user = User.objects.get(username = form.cleaned_data.get('email') )
		hash_object = hashlib.sha1(str(user.id)+str(datetime.datetime.now()))
		token = hash_object.hexdigest()
		if user.groups.filter(name='member').exists():
			user.member.token_password = token
			user.member.save()
			reset_password(user, user.member.first_name ,token)
		if user.groups.filter(name='pro').exists():
			user.pro.token_password = token
			user.pro.save()
			reset_password(user, user.pro.first_name ,token)
		return HttpResponseRedirect( reverse('pages:reset-password-2') )  

class AProposView(TemplateView):
	def get_template_names(self):
		if self.request.user.is_authenticated() and self.request.user.groups.filter(name='pro').exists():
			return 'pages/a-propos-pro.html'
		else:
			return 'pages/a-propos.html'

def ResetPasswordStep3(request, token):
	if Member.objects.filter(token_password=token).exists():
		user = Member.objects.get(token_password=token)
	elif Pro.objects.filter(token_password=token).exists():
		user = Pro.objects.get(token_password=token)
	else:
		raise Http404
	form = ResetPasswordStepThreeForm(request.POST or None)	

	if form.is_valid():
		user.user.set_password( form.cleaned_data.get('password')  )
		user.token_password = None
		user.save()
		user.user.save()
		user.user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user.user)
		#messages.add_message(request, messages.INFO, 'Votre mot de passe a bien été modifié ! Vous pouvez maintenant vous connecter avec votre nouveau mot de passe')
		return HttpResponseRedirect( reverse('members:home') )  

	context = {"form": form}

	return render(request, 'pages/reset-password-3.html', context)


class LandingPageCreate(CreateView):
	model = LandingPage
	fields = ['first_name', 'last_name', 'email', 'company', 'phone', 'fonction', 'employes']
	template_name = 'pages/landing.html'

	def form_valid(self, form):
		obj = form.save()
		obj.landing = "offre-speciale-viadeo"
		obj.save()

		return HttpResponseRedirect( reverse('pages:landing-page-merci') )


def connect_all_user(request, id):
	member = Member.objects.get(id=id)
	user = member.user
	user.backend = 'django.contrib.auth.backends.ModelBackend'
	login(request, user)
	return HttpResponseRedirect(reverse('members:home'))


def xml_indeed(request):
	jobs = Job.objects.filter(scraper=False,active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by('-date_posted')
	return render(request, 'xml/indeed.xml', {"jobs":jobs}, content_type="application/xhtml+xml")

def xml_optioncarriere(request):
	jobs = Job.objects.filter(scraper=False,active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by('-date_posted')
	return render(request, 'xml/optioncarriere.xml', {"jobs":jobs}, content_type="application/xhtml+xml")

def xml_jobrapido(request):
	jobs = Job.objects.filter(scraper=False,active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by('-date_posted')
	return render(request, 'xml/jobrapido.xml', {"jobs":jobs}, content_type="application/xhtml+xml")

def xml_jobijoba(request):
	jobs = Job.objects.filter(scraper=False,active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by('-date_posted')
	return render(request, 'xml/jobijoba.xml', {"jobs":jobs}, content_type="application/xhtml+xml")

def import_broadben(request):
	from pro.multiposteur.broadbean import Broadbean
	Broadbean()
	return HttpResponse('ok')

def import_flatchr(request):
	from pro.multiposteur.flatchr import Flatchr
	Flatchr()
	return HttpResponse('ok')

def letudiant_scraper(request):
	from notifications.letudiant_scraper import LetudiantScraper
	LetudiantScraper().parse()
	return HttpResponse('ok')


#----------------------------------------------------------
#----------------------------------------------------------
#----------------------------------------------------------

def elasticsearch_import_cv():
	from elasticsearch import Elasticsearch
	import datetime, json, time

	members = Member.objects.order_by("-id")

	es = Elasticsearch(['https://search-pitch-2k2jxfngnsvechhmkt5xiyyc4m.eu-west-1.es.amazonaws.com/'])

	for member in members:
		print member.id
		js = {
			"first_name": member.first_name,
			"last_name": member.last_name,
			"email": member.email,
			"image" : "https://v1-pitchmyjob.s3.amazonaws.com"+member.image.url,
			"study": member.study.name if member.study else '',
			"industry": list(member.activity_area.values_list('name', flat=True)),
			"experience": member.experience.name if member.experience else  '',
			"contracts": list(member.contracts.values_list('name', flat=True)),
			"tags": {
				"count" : member.tags.count(),
				"datas" : list(member.tags.values_list('name', flat=True)) if member.tags else []
			},
			"location": {
				"locality": member.locality,
				"country": member.country,
				"administrative_area_level_1": member.administrative_area_level_1,
				"administrative_area_level_2": member.administrative_area_level_2
			},
			"poste": member.cv.poste,
			"experiences": {
				"count" : member.cv.cvexperience_set.count(),
				"datas" : [{"title": exp.title, "company": exp.company,"description": exp.description.replace('\r', '').replace('\n',' ') if exp.description else ''}for exp in member.cv.cvexperience_set.all()]
			},
			"formations": {
				"count" : member.cv.cvformation_set.count(),
				"datas" : [{"school": fm.school, "degree": fm.degree} for fm in member.cv.cvformation_set.all()]
			},
			"skills" : {
				"count" : member.cv.cvskill_set.count(),
				"datas" : list(member.cv.cvskill_set.values_list('name', flat=True))
			},
			"languages": [lg.name for lg in member.cv.cvlanguage_set.all()],
			"interets": [inter.name for inter in member.cv.cvinterest_set.all()],
			"timestamp_joined": int(time.mktime(member.user.date_joined.timetuple())),
			"date_joined" : str(member.user.date_joined)
		}

		es.index(index="pitch", doc_type="cv", id=member.id, body=json.dumps(js))

def elasticsearch_import_job():

	from elasticsearch import Elasticsearch
	import datetime, json
	import time
	from django.utils import timezone

	es = Elasticsearch(['https://search-pitch-2k2jxfngnsvechhmkt5xiyyc4m.eu-west-1.es.amazonaws.com/'])

	jobs = Job.objects.filter(active=True, paid=True, date_posted__gte=timezone.now().date() - datetime.timedelta(days=30)).order_by('scraper')
	print jobs.count()

	for job in jobs:

		print job.id
		js = {
			"id_pro": job.pro.id,
			"company": job.company,
			"title": job.job_title,
			"image" : "https://v1-pitchmyjob.s3.amazonaws.com"+job.image.url,
			"description": job.description.replace('\r', '').replace('\n', ' ') if job.description else '',
			"mission": job.mission.replace('\r', '').replace('\n', ' ') if job.mission else '',
			"profile": job.profile.replace('\r', '').replace('\n', ' ') if job.profile else '',
			"tags": {
				"count": job.tags.count(),
				"datas": list(job.tags.values_list('name', flat=True)) if job.tags else []
			},
			"industry": job.activity_area.name if job.activity_area else '',
			"experience": list(job.experiences.values_list('name', flat=True)) if job.experiences else [],
			"studies": list(job.studies.values_list('name', flat=True)) if job.studies else [],
			"contracts": list(job.contracts.values_list('name', flat=True)) if job.contracts else [],
			"location": {
				"lat": job.latitude,
				"lon": job.longitude,
				"locality": job.locality,
				"country": job.country,
				"administrative_area_level_1": job.administrative_area_level_1,
				"administrative_area_level_2": job.administrative_area_level_2
			},
			"date_posted": str(job.date_posted),
			"timestamp_posted" : int(time.mktime(job.date_posted.timetuple())) if job.date_posted else "",
			"date_created": str(datetime.datetime.now()),
			"scraper" : job.scraper
		}
		es.index(index="pitch", doc_type="job", id=job.id, body=json.dumps(js))



def import_metier(request):
	import csv
	ok = ""
	with open('/var/www/vhosts/myc2v/media/db-metier.csv') as f:
		reader = csv.reader(f)
		for row in reader:
			if row:
				objet, created = JobList.objects.get_or_create(name=row[0])

	return HttpResponse( ok )

def candidature_avorte(request):
	from members.models import Candidature
	from django.core.mail import EmailMessage
	from django.template.loader import render_to_string

	date = timezone.now() - datetime.timedelta(days=10) #last 19 oct 2016

	candidatures = Candidature.objects.filter(active=False, date_posted__gte=date).exclude(job__id=28004)

	for cd in candidatures:
		object = u"%s ta candidature pour l’offre %s n’as pas aboutie" % (unicode(cd.member.first_name), unicode(cd.job.job_title))
		async_send_email(object, [cd.member.email], "emails/satisfaction.html", {"name": cd.member.first_name, "offre": cd.job.job_title, "id": cd.job.id})

	return HttpResponse('ok')

def test_email(request):
	#async_remixjob_import.delay()
	#async_send_email.delay("Un candidat correspond à votre offre", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/candidats_correspondant_a_loffre.html", {})
	#async_send_email.delay("Candidature envoyée", ["tannier.yannis@gmail.com"], "emails/candidature_envoyee.html", {})
	#async_send_email.delay("Candidature refusée", ["tannier.yannis@gmail.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/candidature_refusee.html", {})
	#async_send_email.delay("Inscription accepté pro", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/Inscription_acceptee_pro.html", {})
	#async_send_email.delay("Inscription User", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/Inscription_user.html", {})
	#async_send_email.delay("Invitation user accepté", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/Invitation_acceptee_user.html", {})
	#async_send_email.delay("Les offres qui vous correspondent", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/les_offres_qui_vous_correspondent.html", {})
	#async_send_email.delay("Modification offre", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/modification_offre.html", {})
	#async_send_email.delay("mot de passe oublié", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/mot_de_passe_oublie.html", {})
	#async_send_email.delay("Nouveau message entreprise", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/nouveau_message_entreprise.html", {})
	#async_send_email.delay("Offre publié", ["tannier.yannis@gmail.com", "yannis@pitchmyjob.com", "yannis6@hotmail.com", "antoine.boudic@gmail.com", "martialdahan@hotmail.fr"], "emails/offre_publiee.html", {})
	#async_send_email("Test email", ["tannier.yannis@gmail.com"], "emails/candidature_refusee.html", {})
	#async_jobteaser_first_import.delay()
	#send_mail('Tannier Yannis', 'Bonjour vous allez bien?', 'contact@pitchmyjob.com', ['tannier.yannis@gmail.com'], fail_silently=False)
	#print "okkkkkkkk"
	#cv = Cv.objects.annotate(num_exp=Count('cvexperience', distinct=True)).annotate(num_for=Count('cvformation', distinct=True)).filter(num_exp__lte=1).filter(num_for__lte=1)
	#async_send_email.delay("Créé ton cv en 1 clic", ["tannier.yannis@gmail.com"], "emails/linkedin.html", {'first_name':'Yannis'})
	#from notifications.notifications import async_multiposting

	#async_multiposting.delay()

	#from pro.multiposteur.broadbean import Broadbean
	#Broadbean()

	#job = Job.objects.filter(active=False, scraper=True,date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB)).order_by('-date_posted')

	#job.update(active=True)

	from pro.models import Pro
	import boto3
	import json
	import uuid

	pros = Pro.objects.all()

	sqs = boto3.resource('sqs')
	queue = sqs.get_queue_by_name(QueueName="v2-sqsEmail-dev")

	message = json.dumps({
		'uuid': str(uuid.uuid4()),
		'subject': "Pitchmyjob devient Spitch !",
		'to': ['tannier.yannis@gmail.com'],
		'from': "antoine@pitchmyjob.com",
		'replyto': ["antoine@pitchmyjob.com"],
		'template': "emailing/emailing-spitch-pro.html",
		'context': {"name": "Antoine"},
		'secure': 1,
	})

	#queue.send_message(MessageBody=message)


	for pro in pros:
		if "viadeo" not in pro.email and "pitchmyjob" not in pro.email:
			message = json.dumps({
				'uuid': str(uuid.uuid4()),
				'subject': "Pitchmyjob devient Spitch !",
				'to': [pro.email],
				'from': "antoine@pitchmyjob.com",
				'replyto': ["antoine@pitchmyjob.com"],
				'template': "emailing/emailing-spitch-pro.html",
				'context': {"name": pro.first_name},
				'secure': 1,
			})
			queue.send_message(MessageBody=message)



	return HttpResponse("Ok")


	from members.models import Member
	import boto3
	import json
	import uuid

	members = Member.objects.all()

	sqs = boto3.resource('sqs')
	queue = sqs.get_queue_by_name(QueueName="v2-sqsEmail-dev")



	#queue.send_message(MessageBody=message)

	tp = 0
	a = 0

	message = json.dumps({
		'uuid': str(uuid.uuid4()),
		'subject': "Pitchmyjob devient Spitch 3!",
		'to': ['tannier.yannis@gmail.com'],
		'from': "antoine@pitchmyjob.com",
		'replyto': ["antoine@pitchmyjob.com"],
		'template': "emailing/emailing-spitch-antoine.html",
		'context': {"name": "Antoine"},
		'secure': 1,
	})

	#queue.send_message(MessageBody=message)

	message = json.dumps({
		'uuid': str(uuid.uuid4()),
		'subject': "Pitchmyjob devient Spitch 2!",
		'to': ['tannier.yannis@gmail.com'],
		'from': "contact@pitchmyjob.com",
		'replyto': ["contact@pitchmyjob.com"],
		'template': "emailing/emailing-spitch.html",
		'context': {"name": "Antoine"},
		'secure': 1,
	})

	#queue.send_message(MessageBody=message)


	for member in members:

		if tp < 4000:
			template = "emailing/emailing-spitch.html"
			fr = "contact@pitchmyjob.com"
		else:
			template = "emailing/emailing-spitch-antoine.html"
			fr = "antoine@pitchmyjob.com"

		a = a + 1
		tp = tp + 1

		print template
		print fr

		message = json.dumps({
			'uuid': str(uuid.uuid4()),
			'subject': "Pitchmyjob devient Spitch !",
			'to': [member.user.email],
			'from': fr,
			'replyto': [fr],
			'template': template,
			'context': {"name": member.first_name},
			'secure': 1,
		})

		queue.send_message(MessageBody=message)



	return HttpResponse("Ok")

	elasticsearch_import_job()
	elasticsearch_import_cv()

	return HttpResponse("Ok")

	from bs4 import BeautifulSoup

	jobs = Job.objects.filter(scraper_site="letudiant")
	print jobs.count()
	for job in jobs:
		print job.id
		new = ""
		desc = BeautifulSoup(job.description, 'html.parser')
		nxt = 0
		for elem in desc.find_all(['h5', 'p']):

			if nxt == 1:
				nxt = 0
				continue

			if elem.get_text().strip() in ("Experience", "Type de contrat", u"Durée", "Infos localisation", u"Niveau(x) d'études"):
				nxt = 1
				continue

			new = new + elem.prettify()

		job.description = new
		job.save()

	return HttpResponse("Ok")

	import requests

	payload = {
		'ref': "eoLm5NdDvk9AGbZQ",
		'id': 26850,
		'first_name': "Yannis",
		'last_name':"Tannier",
		'email': "tannier.yannis@gmail.com",
		'cv': "https://www.pitchmyjob.com/media/candidatures/cv-tannier_77SzXFR.pdf",
		'questions': ["question test 1","question test 2"],
		'answers': ["https://s3.eu-central-1.amazonaws.com/pitchmyjob/vs1474623778185_277.mp4","https://s3.eu-central-1.amazonaws.com/pitchmyjob/vs1474623787009_835.mp4"]
	}

	response = requests.post("http://flatchr.io/vacancy/candidate/pitchmyjob", data=payload)

	return HttpResponse(payload)

	from members.models import Candidature


	#date = timezone.now() - datetime.timedelta(days=7)

	#candidatures = Candidature.objects.filter(active=False, date_posted__gte=date)

	#for cd in candidatures:
		#object = u"%s ta candidature pour l’offre %s n’as pas aboutie" % (unicode(cd.member.first_name), unicode(cd.job.job_title))
		#async_send_email.delay(object, [cd.member.user.email], "emails/satisfaction.html",{"name": cd.member.first_name, "offre": cd.job.job_title, "id": cd.job.id})

	# msg = EmailMessage(unicode(object), message, to=[cd.member.user.email], from_email='Pitch my job <contact@pitchmyjob.com>')
	# msg.content_subtype = 'html'
	# msg.send()

	return render(request, 'pages/test.html', {'jobs': candidatures})


	return render(request, 'pages/test.html', {'jobs': "d"})

	from members.models import Interest

	int = Interest.objects.get(id=334)

	obj = u"Nouveau message de %s" % int.job.company

	async_send_email(obj, [int.member.user.email], "emails/offre_suggerer.html",
						   {"name": int.member.first_name, "offre": int.job.job_title, "id": int.job.id})

	return HttpResponse(int)

	#for int in interest :
		#if not Candidature.objects.filter(member=int.member).exists():
			#obj = u"Nouveau message de %s" % (int.job.company)
			#async_send_email.delay(obj, ["tannier.yannis@gmail.com"], "emails/offre_suggerer.html", {"name": int.member.first_name, "offre" : int.job.job_title, "id" : int.job.id })
			#break

	return render(request, 'pages/test.html', {'jobs': ok})


	return render(request, 'pages/test.html', {'jobs': ok})


	from members.models import Candidature
	from django.core.mail import EmailMessage
	from django.template.loader import render_to_string

	date = timezone.now() - datetime.timedelta(days=5)

	candidatures = Candidature.objects.filter(active=False, date_posted__gte=date)

	return render(request, 'pages/test.html', {'jobs': candidatures})

	pro = Pro.objects.filter(scraper=False).exclude(id__in=(1896, 1903, 1895, 1900, 1870, 1877, 1897, 1879, 1819, 1842, 1782, 1880, 1112, 1795))

	for p in pro :
		msg = "Merci de nous avoir fait confiance %s" % ( unicode(p.email) )
		async_send_email(msg, [p.email], "emails/remerciement.html", {"name": p.first_name})

	return render(request, 'pages/test.html', {'jobs': pro})

	

	return HttpResponse('ok') 


	from members.models import Member
	from django.core.mail import EmailMessage
	from django.template.loader import render_to_string

	all = Member.objects.all()[600:]

	for m in all :
		async_send_email("Soutiens Pitch my Job", [m.user.email], "emails/soutiens.html",{"name": m.first_name})

	return HttpResponse('ok')


	from members.models import Candidature
	from django.core.mail import EmailMessage
	from django.template.loader import render_to_string

	candidatures = Candidature.objects.filter(active=False)

	for cd in candidatures :
		object = u"%s ta candidature pour l’offre %s n’as pas aboutie" % ( unicode(cd.member.first_name), unicode(cd.job.job_title) )
		message = render_to_string("emails/satisfaction.html", {"name": cd.member.first_name, "offre" : cd.job.job_title, "id":cd.job.id })
		#msg = EmailMessage(unicode(object), message, to=[cd.member.user.email], from_email='Pitch my job <contact@pitchmyjob.com>')
		#msg.content_subtype = 'html'
		#msg.send()

	return render(request, 'pages/test.html', {'jobs': "job"})
	return HttpResponse('ok')

	from c2v.views import generate_pdf

	member = Member.objects.get(id=1541)

	#async_send_email_attach("test", ["tannier.yannis@gmail.com"], "emails/send_cv.html", {"message": "yo"}, {"name": "mydoc.pdf", "file": generate_pdf('c2v/themes/pdf-theme-1.html',{'pagesize': 'A4','cv': member.cv}),"type": "application/pdf"})

	from django.core.mail import EmailMessage
	from django.template.loader import render_to_string

	message = render_to_string("emails/send_cv.html", {"message": "yo"})
	msg = EmailMessage("yo", message, to=['tannier.yannis@gmail.com'], from_email='Pitch my job <no-reply@pitchmyjob.com>')
	msg.content_subtype = 'html'
	msg.attach_file('/var/www/vhosts/preprod/static/images/refonte/candidature-06.png')
	msg.send()

	return render(request, 'pages/test.html', {'jobs' : 'jobs' })


def get_cv_incompleted(request):
	cv = Cv.objects.annotate(num_exp=Count('cvexperience', distinct=True)).annotate(num_for=Count('cvformation', distinct=True)).filter(num_exp__lte=1).filter(num_for__lte=1)
	
	#async_send_email("Tu n'as pas completé ton cv.", ["tannier.yannis@gmail.com"], "emails/linkedin.html", {'first_name':'Yannis'})
	#for c in cv:
		#async_send_email.delay("Tu n'as pas completé ton cv", [c.member.email], "emails/linkedin.html", {'first_name': c.member.first_name})

	return render(request, 'pages/test.html', {'cv' : cv }) 

def invitation_ok(request):
	if request.method == 'POST':
		context={"nom":request.POST.get('nom')}
		async_send_email(u"Demande d'inscription sur Pitch my job", [request.POST.get('email')], "emails/Invitation_acceptee_user.html", context)
	return render(request, 'pages/accept-invitation.html')


def test_linkedin(request):
	from notifications.linkedin_scraper import LinkedInScraper
	mr = LinkedInScraper("https://www.linkedin.com/in/florestinemorice")
	return render(request, 'pages/test.html', {'data' : mr.data })


def test_doyoubuzz(request):

	key = 'aupsiwmO3YRNTUxE1zIV'
	secret = 'TWwkaRDC0eMfl7KLvZGqVE3NO'
	site_url = 'http://www.pitchmyjob.com/test-doyoubuzz'
	callback_url = 'http://www.pitchmyjob.com/test-doyoubuzz'
	return render(request, 'pages/test.html')


def apec(request):
	from notifications.notifications import apec_async, asyn_emailing
	#apec_async.delay()
	asyn_emailing()
	return HttpResponse('ok')


def emailing(request):
	from notifications.notifications import asyn_emailing

	asyn_emailing()

	return HttpResponse('ok')

def whosnext(request):

	search = "développeur web"

	member = Member.objects.filter(administrative_area_level_1="Île-de-France")

	member = member.filter(Q(cv__cvexperience__title__icontains=search)  | Q(cv__poste__icontains=search) | Q(job_wanted__icontains=search)  | Q(cv__cvskill__name=search)  ).distinct()

	#async_send_email.delay(u"D2SI recherche un développeur Python", ['tannier.yannis@gmail.com'], "emails/email-recherche.html", {'member' :'test'})

	#for mbr in member:
		#context={'member' : mbr.first_name}
		#async_send_email.delay(u"D2SI recherche un développeur Python", [mbr.email], "emails/email-recherche.html", context)

	return render(request, 'pages/test.html', {'member' : member})