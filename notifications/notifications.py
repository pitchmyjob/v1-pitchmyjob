# -*- coding: utf-8 -*-
from .models import Notification
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
import datetime, urllib2, os
from c2v.models import Cv, CvExperience, CvFormation, CvSkill, CvLanguage, CvInterest
from members.models import Member
from pro.models import Job
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from django.conf import settings
from django.core.mail import send_mail
from multiprocessing import Pool
from django.http import HttpResponse


def test_cron(request):
	send_mail('Hello cron!', 'No bug', 'contact@pitchmyjob.com', ['tannier.yannis@gmail.com'], fail_silently=False)
	return HttpResponse("")

def async_multiposting():
	from pro.multiposteur.multiposting import Multiposting
	Multiposting()

def cron_import_flatchr():
	from pro.multiposteur.flatchr import Flatchr
	Flatchr()
	#send_mail('Flatchr cron!', 'No bug', 'contact@pitchmyjob.com', ['tannier.yannis@gmail.com'],fail_silently=False)

def async_remixjob_import():
	from remixjob_scraper import RemixJobScraper
	rj = RemixJobScraper()
	rj.parse()
	#send_mail('Remixjob - Cron import effectue !', 'No bug', 'contact@pitchmyjob.com', ['tannier.yannis@gmail.com'], fail_silently=False)

def async_jobteaser_import():
	from jobteaser_scraper import JobTeaserScraper
	jb = JobTeaserScraper()
	jb.parse()
	#send_mail('JobTeaser - Cron import effectue !', 'No bug', 'contact@pitchmyjob.com', ['tannier.yannis@gmail.com'], fail_silently=False)

def remixjob_check():
	from remixjob_scraper import RemixJobScraper
	rj = RemixJobScraper()
	list_id = rj.get_list_id()

	jobs = Job.objects.filter(scraper=True, active=True, scraper_site="remixjob")
	rm=0
	for job in jobs:
		if job.scraper_id not in list_id:
			job.active=False
			job.save()
			job.delete_on_elasticsearch()
			rm=rm+1

	#send_mail('Remixjob - Cron check effectue', 'Nombre remove : '+str(rm), 'contact@pitchmyjob.com', ['tannier.yannis@gmail.com'], fail_silently=False)


def jobteaser_check():
	from jobteaser_scraper import JobTeaserScraper
	jb = JobTeaserScraper()
	list_id = jb.get_list_id()

	jobs = Job.objects.filter(scraper=True, active=True, scraper_site="jobteaser")

	rm=0
	for job in jobs:
		if job.scraper_id not in list_id:
			job.active=False
			job.save()
			job.delete_on_elasticsearch()
			rm=rm+1

	#send_mail('JobTeaser - Cron check effectue', 'Nombre remove : '+str(rm), 'contact@pitchmyjob.com', ['tannier.yannis@gmail.com'], fail_silently=False)


def linkedin_cv_connected(html):
	from linkedin_scraper import LinkedInScraper
	ld = LinkedInScraper()
	ld.set_html(html)
	ld.parse()

	print ld.data['interests']


def async_linkedin_cv(pk, url):
	from linkedin_scraper import LinkedInScraper
	mr = LinkedInScraper(url, pk)
	print mr.data
	script_import_linkedin(mr, pk)

def script_import_linkedin(mr, pk):
	member = Member.objects.get(id=pk)
	cv = Cv.objects.get(member=member)

	CvExperience.objects.filter(cv = cv).delete()
	CvFormation.objects.filter(cv = cv).delete()
	CvInterest.objects.filter(cv = cv).delete()
	CvLanguage.objects.filter(cv = cv).delete()
	CvSkill.objects.filter(cv = cv).delete()

	if 'user' in mr.data:
		if 'img' in mr.data['user']:
			tt = str(datetime.datetime.now())
			img_temp = NamedTemporaryFile(delete=True)
			img_temp.write(urllib2.urlopen(mr.data['user']['img']).read())
			img_temp.flush()
			member.image.save(str(member.id)+str(tt)+".jpg", File(img_temp))
			try:
				os.chmod(settings.MEDIA_ROOT+"c2v/"+str(member.id),0777)
				os.chmod(member.image.path,0777)
			except:
				error=True

			if 'address' in mr.data['user']:
				if mr.data['user']['address']:
					cv.city = mr.data['user']['address']
					cv.save()

			if 'title' in mr.data['user']:
				if mr.data['user']['title']:
					cv.poste = mr.data['user']['title']
					cv.save()

	if 'experiences' in mr.data:
		for exp in mr.data['experiences']:
			cvExp = CvExperience(cv=cv, company=exp['company'], title=exp['title'])
			try:
				if 'month' in exp['date_range']['start']:
					dd = str(exp['date_range']['start']['year'])+"-"+str(exp['date_range']['start']['month'])
					dd = datetime.datetime.strptime(dd, '%Y-%m')
				else:
					dd = datetime.datetime.strptime(exp['date_range']['start']['year'], '%Y')
				cvExp = CvExperience(cv=cv, company=exp['company'], title=exp['title'], date_start=dd)
			except Exception:
				cvExp = CvExperience(cv=cv, company=exp['company'], title=exp['title'])
			if exp['date_range']['end']:
				try:
					if 'month' in exp['date_range']['end']:
						df = str(exp['date_range']['end']['year'])+"-"+str(exp['date_range']['end']['month'])
						df = datetime.datetime.strptime(df, '%Y-%m')
					else:
						df = datetime.datetime.strptime(exp['date_range']['end']['year'], '%Y')
					cvExp.date_end = df
				except Exception:
					pass
			if exp['description']:
				cvExp.description = exp['description']
			if exp['location']:
				cvExp.location = exp['location']
			cvExp.save()
			if exp['company_logo']:
				img_temp = NamedTemporaryFile(delete=True)
				img_temp.write(urllib2.urlopen(exp['company_logo']).read())
				img_temp.flush()
				cvExp.image.save(str(cvExp.id)+".jpg", File(img_temp))

	if 'education' in mr.data:
		for educ in mr.data['education']:
			cvEduc = CvFormation(cv=cv, school=educ['school'], degree=educ['diploma'])
			if educ['date_range']:
				if 'start' in educ['date_range']:
					if educ['date_range']['start']:
						try:
							dd = str(educ['date_range']['start']['year'])
							dd = datetime.datetime.strptime(dd, '%Y')
							cvEduc.date_start = dd
						except Exception:
							pass
				if 'end' in educ['date_range']:
					if educ['date_range']['end']:
						try:
							df = str(educ['date_range']['end']['year'])
							df = datetime.datetime.strptime(df, '%Y')
							cvEduc.date_end = df
						except Exception:
							pass
			cvEduc.save()
			if educ['logo']:
				img_temp = NamedTemporaryFile(delete=True)
				img_temp.write(urllib2.urlopen(educ['logo']).read())
				img_temp.flush()
				cvEduc.image.save(str(cvEduc.id)+".jpg", File(img_temp))

	if 'skills' in mr.data:
		for skill in mr.data['skills']:
			CvSkill(cv=cv, name=skill).save()

	if 'languages' in mr.data:
		for lang in mr.data['languages']:
			cvLang = CvLanguage(cv=cv, name=lang['name'])
			if 'proficiency' in lang:
				if lang['proficiency']:
					cvLang.level = lang['proficiency']
			cvLang.save()

	if 'interests' in mr.data:
		for inter in mr.data['interests']:
			CvInterest(cv=cv, name=inter).save()

	member.save_on_elasticsearch()


def send_email(subject, to, template, ctx, from_email ):
	message = render_to_string(template, ctx)
	msg = EmailMessage(subject, message, to=to, from_email=from_email)
	msg.content_subtype = 'html'
	msg.send()

def send_email_attach(subject, to, template, ctx, att ):
	message = render_to_string(template, ctx)
	msg = EmailMessage(subject, message, to=to, from_email='Pitch my job <no-reply@pitchmyjob.com>')
	msg.content_subtype = 'html'
	msg.attach(att['name'], att['file'], att['type'])
	msg.send()

def finish(elem):
	pass

def async_send_email(subject, to, template, ctx, from_email = 'Pitch my job <contact@pitchmyjob.com>' ):
	pool = Pool(processes=1)
	result = pool.apply_async(send_email, [subject, to, template, ctx, from_email ], callback=finish)
	pool.close()

def async_send_email_attach(subject, to, template, ctx, att ):
	pool = Pool(processes=1)  
	result = pool.apply_async(send_email_attach, [subject, to, template, ctx, att], callback=finish)
	pool.close()


def reset_password(user=None, first_name=None, token=None):
	async_send_email("Réinitialisez votre mot de passer Pitch my job.", [user.email], "emails/mot_de_passe_oublie.html", {"token":token, "first_name":first_name, "email":user.email})

def notification(ntype, member=None, pro=None, job=None, params=None):
	if ntype == 1:
		async_send_email("Votre candidature a été envoyé !", [member.email], "emails/candidature_envoyee.html", {"job":job.job_title, "first_name":member.first_name, "company":job.company})
	if ntype == 2:
		#async_send_email("Votre offre a été modifié.", [pro.email], "emails/candidature_envoyee.html", {"job":job.job_title, "first_name":pro.first_name, "id":job.id})
		async_send_email("Votre offre a été modifié.", [pro.email], "emails/modification_offre.html", {"job":job.job_title, "first_name":pro.first_name, "id":job.id})
	if ntype == 3:
		async_send_email("Votre offre a été publiée avec succès.", [pro.email], "emails/offre_publiee.html", {"job":job.job_title, "first_name":pro.first_name, "id":job.id})
	if ntype == 4:
		async_send_email("Suppression de votre offre.", [pro.email], "emails/suppression_offre.html", {"job":job.job_title, "first_name":pro.first_name, "id":job.id})
	if ntype == 5:
		Notification(sender=member.user, receiver=job.pro.user, job=job, type_notif=5, group=1).save()
		context = {"job":job.job_title, "first_name":job.pro.first_name, "id":job.id}
		async_send_email('Nouvelle candidature pour votre offre "%s" ' % job.job_title, [job.pro.email], "emails/nouvelle_candidature_pro.html", context)
	if ntype == 6:
		context = {"company":job.company, "text" : params.encode('utf8')}
		async_send_email(u"Votre candidature pour l'offre %s a été refusé" % job.job_title, [member.email], "emails/candidature_refusee.html", context)
	if ntype == 7:
		notif = Notification.objects.filter(sender=pro.user, receiver=member.user, type_notif=7)
		if notif.exists():
			notif = notif.first()
			notif.view = 0
			notif.save()
		else:
			Notification(sender=pro.user, receiver=member.user, type_notif=7, group=2).save()

def alert_message(sender, receiver, group, last_message):
	if last_message.exists() is False:
		if group == 1:
			title=u"Nouveau message de %s" % sender.member.first_name
			async_send_email(title, [receiver.email], "emails/nouveau_message_pro.html", {'pro' : receiver.pro.first_name, 'member' : sender.member.first_name, 'id' : sender.member.id, 'photo':sender.member.image['profil100'].url })
		if group == 2:
			title=u"Nouveau message de %s" % sender.pro.company
			async_send_email(title, [receiver.email], "emails/nouveau_message_user.html", {'pro' : sender.pro.company, 'first_name' : receiver.member.first_name, 'id' : sender.pro.id })


def asyn_emailing():
	from django.core.mail import EmailMessage
	from django.template.loader import render_to_string, get_template
	from django.template import Context
	from pages.models import Apec

	users = Apec.objects.filter(sent=False)[0:1500]
	i=0

	for user in users:
		user.sent=True
		user.save()
		if i < 750:
			from_email="antoine@pitchmyjob.com"
			template_name="emails/email-antoine.html"
			print "antoine" 

		if i >= 750:
			from_email="martial@pitchmyjob.com"
			template_name="emails/email-martial.html"
			print "martial"


		print " USER : %s - %s " % (user.prenom, user.email)

		ctx={ 'name' : user.prenom.title() }
		subject=u"✸ %s dechirez votre lettre de motivation !" % user.prenom.title()
		

		message = get_template(template_name).render(Context(ctx))
		to=[user.email, ]
		msg = EmailMessage(subject, message, to=to, from_email=from_email)
		msg.content_subtype = 'html'
		msg.send()

		i=i+1


def apec_async():
	import mechanize, datetime
	import cookielib
	import json, requests
	from bs4 import BeautifulSoup
	from pages.models import Apec

	criteres={'delaisDisponibilite':[200137], 'fonctions':[], 'fonctionsFacetable':True, 'lieux':[711], 'lieuxFacetable':True, 'motsCles':"", 'secteursActivite':[], 'secteursActiviteFacetable':True}

	for x in xrange(300,500):
		print "--------------------------------------------------------------------------------------------"
		print x
		print "--------------------------------------------------------------------------------------------"
		payload={
			'criteres':criteres,
			'limit':100,
			'offset':x
		}


		r = requests.post(
				url='https://recruteurs.apec.fr/cms/webservices/rechercheCv',
				headers={
					'accept':'application/json, text/plain, */*',
					'accept-encoding':'gzip, deflate',
					'accept-language':'en-US,en;q=0.8',
					'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
					'Cookie':'mogobiz_uuid=CgEK8lfNSwVFmnS0B0CGAg==; Recrutementdb2d4c60-f71a-432a-9f20-a5704187b5d0=Recrutementdb2d4c60-f71a-432a-9f20-a5704187b5d0; /sites/cadres/messages/bloc1/cookie-warning="Mon Sep 05 12:38:02 CEST 2016"; Recrutement43ef03ce-a3c0-44ae-9bdc-ac060f739f18=Recrutement43ef03ce-a3c0-44ae-9bdc-ac060f739f18; liveagent_oref=https://recruteurs.apec.fr/home/consulter-les-cv.html; liveagent_ptid=6f4af8a3-72f9-46e2-95de-f83ee2eb9f96; liveagent_sid=45300bf5-d2e9-47cd-a32d-c8e0ca524e34; liveagent_vc=4; JSESSIONID=67B36668CC174228DC2757AC0D797CE8; apec.user.cookie="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?> <userCookie>     <key>c5f09d71-6c39-4620-9452-a198313f29a7</key>     <numeroCompte>100020981W</numeroCompte>     <type>RECRUTEUR</type> </userCookie> "; nocache=1; mogobiz_time=2016-09-05T13:37:57+02:00; srv_id=3b892d209770410e299211a3edc11163; apec.activity.cookie=100020981W; apec.activity.cookie.timeout=1473077278817; APEC_USER_ID=100020981|1|1',
					'Content-Type':'application/json;charset=UTF-8'
				},
				data=json.dumps(payload)
		)

		res = json.loads(r.text)

		i=0
		for user in res['resultats']:
			datepublication = user['datePublication']=user['datePublication'].split('T')
			datepublication = datetime.datetime.strptime(user['datePublication'][0], "%Y-%m-%d").date()

			identifiant = user['id']

			public=requests.get(
					url='https://recruteurs.apec.fr/cms/webservices/cv/'+str(identifiant)+'/public',
					headers={
						'accept':'application/json, text/plain, */*',
						'accept-encoding':'gzip, deflate',
						'accept-language':'en-US,en;q=0.8',
						'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
						'Cookie':'mogobiz_uuid=CgEK8lfNSwVFmnS0B0CGAg==; Recrutementdb2d4c60-f71a-432a-9f20-a5704187b5d0=Recrutementdb2d4c60-f71a-432a-9f20-a5704187b5d0; /sites/cadres/messages/bloc1/cookie-warning="Mon Sep 05 12:38:02 CEST 2016"; Recrutement43ef03ce-a3c0-44ae-9bdc-ac060f739f18=Recrutement43ef03ce-a3c0-44ae-9bdc-ac060f739f18; liveagent_oref=https://recruteurs.apec.fr/home/consulter-les-cv.html; liveagent_ptid=6f4af8a3-72f9-46e2-95de-f83ee2eb9f96; liveagent_sid=45300bf5-d2e9-47cd-a32d-c8e0ca524e34; liveagent_vc=4; JSESSIONID=67B36668CC174228DC2757AC0D797CE8; apec.user.cookie="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?> <userCookie>     <key>c5f09d71-6c39-4620-9452-a198313f29a7</key>     <numeroCompte>100020981W</numeroCompte>     <type>RECRUTEUR</type> </userCookie> "; nocache=1; mogobiz_time=2016-09-05T13:37:57+02:00; srv_id=3b892d209770410e299211a3edc11163; apec.activity.cookie=100020981W; apec.activity.cookie.timeout=1473077278817; APEC_USER_ID=100020981|1|1',
						'Content-Type':'application/json;charset=UTF-8'
					}
			)
			public = json.loads(public.text)

			if 'idCompteCadre' in public:
				print identifiant

				idCompteCadre=public['idCompteCadre']

				etat=requests.get(
						url='https://recruteurs.apec.fr/cms/webservices/compteCadre/'+str(idCompteCadre)+'/etatcivil',
						headers={
							'accept':'application/json, text/plain, */*',
							'accept-encoding':'gzip, deflate',
							'accept-language':'en-US,en;q=0.8',
							'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
							'Cookie':'mogobiz_uuid=CgEK8lfNSwVFmnS0B0CGAg==; Recrutementdb2d4c60-f71a-432a-9f20-a5704187b5d0=Recrutementdb2d4c60-f71a-432a-9f20-a5704187b5d0; /sites/cadres/messages/bloc1/cookie-warning="Mon Sep 05 12:38:02 CEST 2016"; Recrutement43ef03ce-a3c0-44ae-9bdc-ac060f739f18=Recrutement43ef03ce-a3c0-44ae-9bdc-ac060f739f18; liveagent_oref=https://recruteurs.apec.fr/home/consulter-les-cv.html; liveagent_ptid=6f4af8a3-72f9-46e2-95de-f83ee2eb9f96; liveagent_sid=45300bf5-d2e9-47cd-a32d-c8e0ca524e34; liveagent_vc=4; JSESSIONID=67B36668CC174228DC2757AC0D797CE8; apec.user.cookie="<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?> <userCookie>     <key>c5f09d71-6c39-4620-9452-a198313f29a7</key>     <numeroCompte>100020981W</numeroCompte>     <type>RECRUTEUR</type> </userCookie> "; nocache=1; mogobiz_time=2016-09-05T13:37:57+02:00; srv_id=3b892d209770410e299211a3edc11163; apec.activity.cookie=100020981W; apec.activity.cookie.timeout=1473077278817; APEC_USER_ID=100020981|1|1',
							'Content-Type':'application/json;charset=UTF-8'
						}
				)
				etat = json.loads(etat.text)

				etat['dateNaissance'] = etat['dateNaissance'].split("T")
				birthday = datetime.datetime.strptime(etat['dateNaissance'][0], "%Y-%m-%d").date()

				if 'adresseEmail' in etat:

					if Apec.objects.filter(identifiant=identifiant).exists():
						print "exist"
						continue

					apec = Apec(email=etat['adresseEmail'], nom=etat['nom'], prenom=etat['prenom'], titre=user['titre'], identifiant=identifiant, dispo="Immediate")
					if 'intituleDiplomeSignificatif' in user:
						apec.formation = user['intituleDiplomeSignificatif']

					if 'titreExperienceSignificative' in user:
						apec.experience = user['titreExperienceSignificative']

					if 'numeroTelephoneMobile' in etat:
						apec.phone = etat['numeroTelephoneMobile']

					if 'dateNaissance' in etat:
						try :
							apec.birthday = datetime.datetime.strptime(etat['dateNaissance'][0], "%Y-%m-%d").date()
						except:
							pass

					if 'adressePostale' in etat:
						if 'adresseVille' in etat['adressePostale']:
							apec.ville=etat['adressePostale']['adresseVille']

					apec.publication=datepublication
					apec.region="Ile de france"
					apec.vague=2

					apec.save()

					print "OKKK"