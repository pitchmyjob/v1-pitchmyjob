# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from myc2v.mixins import UnicodeNameMixin
from easy_thumbnails.fields import ThumbnailerImageField
import urlparse, re, datetime, json
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.conf import settings
from django.template.defaultfilters import slugify
from elasticsearch import Elasticsearch
import os
import uuid

def generate_unique_filename(self, filename):
	filename, file_extension = os.path.splitext(filename)
	filename = slugify(filename)
	name = str(filename) + "-" +str(uuid.uuid4()) + str(file_extension)
	url = "job/%s" % ( name )
	return url

def generate_filename(self, filename):
    url = "pro/%s/%s" % (self.id, slugify(filename))
    return url

def cover_filename(self, filename):
    url = "pro/%s/cover-%s" % (self.id, slugify(filename))
    return url

class ActivityArea(UnicodeNameMixin, models.Model):
	name	= models.CharField(max_length=200, null=True)
	active 	= models.BooleanField(default=True)
	ordre 	= models.IntegerField(default=0)

	class Meta:
		verbose_name = "Secteur d'activité"
		verbose_name_plural = "Liste des secteur d'activité"
		ordering = ['-ordre', 'name']

class Contract(UnicodeNameMixin, models.Model):
	name 	= models.CharField(max_length=200, null=True)
	active 	= models.BooleanField(default=True)

	class Meta:
		verbose_name = "Type de contrat"
		verbose_name_plural = "liste des type de contrat"

class JobList(UnicodeNameMixin, models.Model):
	name 	= models.CharField(max_length=200, null=True)
	active 	= models.BooleanField(default=True)

	class Meta:
		verbose_name = "Metier"
		verbose_name_plural = "liste des metiers"

class Employes(UnicodeNameMixin, models.Model):
	name 	= models.CharField(max_length=200, null=True)
	active 	= models.BooleanField(default=True)

	class Meta:
		verbose_name = "Nombre d'employés"
		verbose_name_plural = "Liste nombre employés"

class ContractTime(UnicodeNameMixin, models.Model):
	name 	= models.CharField(max_length=200, null=True)
	active 	= models.BooleanField(default=True)

class Tag(UnicodeNameMixin, models.Model):
	name 	= models.CharField(max_length=250, null=True)

class Pro(models.Model):
	user 			= models.OneToOneField(User)
	company			= models.CharField(max_length=250, null=True)
	phone 			= models.CharField(max_length=250, null=True)
	first_name 		= models.CharField(max_length=250, null=True)
	last_name 		= models.CharField(max_length=250, null=True)
	email 			= models.CharField(max_length=250, null=True)
	web_site		= models.CharField(max_length=250, null=True, blank = True)
	activity_area	= models.ForeignKey(ActivityArea, null=True)
	headquarters 	= models.CharField(max_length=250, null=True, blank = True)
	latitude		= models.FloatField(null=True, blank=True)
	longitude 		= models.FloatField(null=True, blank=True)
	street_number 	= models.CharField(max_length=250, null=True, blank=True)
	route 			= models.CharField(max_length=250, null=True, blank=True)
	cp   	 		= models.CharField(max_length=250, null=True, blank=True)
	locality 		= models.CharField(max_length=250, null=True, blank=True)
	administrative_area_level_2 = models.CharField(max_length=250, null=True, blank=True)
	administrative_area_level_1 = models.CharField(max_length=250, null=True, blank=True)
	country			= models.CharField(max_length=250, null=True, blank=True)
	employes		= models.ForeignKey(Employes, null=True)
	ca 				= models.CharField(max_length=250, null=True, blank=True)
	video_url		= models.CharField(max_length=250, null=True, blank = True)
	description		= models.TextField(null=True, blank = True)
	image 			= ThumbnailerImageField(upload_to=generate_filename, blank=True, default="pro/default.jpg")
	cover 			= ThumbnailerImageField(upload_to=cover_filename, blank=True, null = True )
	link_facebook 	= models.CharField(max_length=250, null=True, blank=True)
	link_twitter	= models.CharField(max_length=250, null=True, blank=True)
	link_youtube	= models.CharField(max_length=250, null=True, blank=True)
	token_password 	= models.CharField(max_length=250, null=True, blank=True)
	view 			= models.IntegerField(default=0)
	credit_job		= models.IntegerField(default=1)
	scraper 		= models.BooleanField(default=False)
	mp 				= models.BooleanField(default=False)
	mp_type 		= models.CharField(max_length=200, null=True, blank=True)
	mp_multiposting_id = models.CharField(max_length=200, null=True, blank=True)
	active  		= models.BooleanField(default=True)

	def count_job(self):
		return self.job_set.filter(active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB)).count()
	
	def type_video(self):
		if self.video_url:
			parsed = urlparse.urlparse( self.video_url )
			if "youtube" in self.video_url:
				return "https://www.youtube.com/embed/"+urlparse.parse_qs(parsed.query)['v'][0]+"?rel=0&amp;showinfo=0"
			elif "dailymotion" in self.video_url:
				return "//www.dailymotion.com/embed/video/"+re.search('video\/([a-zA-Z0-9]+)_',  self.video_url ).group(1)
			elif "vimeo" in self.video_url:
				return "https://player.vimeo.com/video/"+parsed[2][1:]+"?color=ab2203&title=0&byline=0&portrait=0&badge=0"
			else:
				return False
		return False


	def __unicode__ (self):
		return self.company

class Job(models.Model):
	pro 			= models.ForeignKey(Pro) 
	company			= models.CharField(max_length=250, null=True)
	job_title		= models.CharField(max_length=250, null=True)
	contact 		= models.CharField(max_length=250, null=True, blank = True)
	job_location 	= models.CharField(max_length=250, null=True)
	latitude		= models.FloatField(null=True, blank=True)
	longitude 		= models.FloatField(null=True, blank=True)
	street_number 	= models.CharField(max_length=250, null=True, blank=True)
	route 			= models.CharField(max_length=250, null=True, blank=True)
	locality 		= models.CharField(max_length=250, null=True, blank=True)
	administrative_area_level_2 = models.CharField(max_length=250, null=True, blank=True)
	administrative_area_level_1 = models.CharField(max_length=250, null=True, blank=True)
	country			= models.CharField(max_length=250, null=True, blank=True)
	web_site		= models.CharField(max_length=250, null=True, blank = True)
	activity_area	= models.ForeignKey(ActivityArea, null=True) 
	contracts 		= models.ManyToManyField(Contract)
	studies 		= models.ManyToManyField("members.Study",  blank = True)
	experiences		= models.ManyToManyField("members.Experience",  blank = True)
	contract_time 	= models.ManyToManyField(ContractTime)
	salary_start 	= models.DecimalField(max_digits=9, decimal_places=2, null=True, blank = True)
	salary_end 		= models.DecimalField(max_digits=9, decimal_places=2, null=True, blank = True)
	salary  		= models.DecimalField(max_digits=9, decimal_places=2, null=True, blank = True)
	description		= models.TextField(null=True)
	mission			= models.TextField(null=True, blank = True)
	profile			= models.TextField(null=True, blank = True)
	video_url		= models.CharField(max_length=250, null=True, blank = True)
	tags 			= models.ManyToManyField(Tag, blank=True)
	is_video 		= models.BooleanField(default=False)
	is_audio 		= models.BooleanField(default=False)
	is_text 		= models.BooleanField(default=False)
	complet 		= models.BooleanField(default=False)
	active 			= models.BooleanField(default=False)
	paid 			= models.BooleanField(default=False)
	date_created	= models.DateField(auto_now_add=True, null=True)
	last_update		= models.DateTimeField(auto_now=True, null = True)
	date_posted 	= models.DateTimeField(null=True, blank=True)
	image 			= ThumbnailerImageField(upload_to=generate_unique_filename, blank=True)
	view 			= models.IntegerField(default=0)
	scraper 		= models.BooleanField(default=False)
	scraper_site	= models.CharField(max_length=250, null=True, blank=True)
	scraper_url		= models.CharField(max_length=250, null=True, blank=True)
	scraper_id  	= models.CharField(max_length=250, null=True, blank=True)
	mp 				= models.BooleanField(default=False)
	mp_type 		= models.CharField(max_length=200, null=True, blank=True)
	mp_email 		= models.CharField(max_length=200, null=True, blank=True)  # application_email
	mp_multiposting_id 	= models.CharField(max_length=200, null=True, blank=True)
	mp_multiposting_ref = models.CharField(max_length=200, null=True, blank=True)
	mp_broadbean_id 	= models.CharField(max_length=200, null=True, blank=True)
	mp_broadbean_ref 	= models.CharField(max_length=200, null=True, blank=True)
	mp_flatchr_ref 	   = models.CharField(max_length=200, null=True, blank=True)

	def type_video(self):
		if self.video_url:
			parsed = urlparse.urlparse( self.video_url )
			if "youtube" in self.video_url:
				return "https://www.youtube.com/embed/"+urlparse.parse_qs(parsed.query)['v'][0]+"?rel=0&amp;showinfo=0"
			elif "dailymotion" in self.video_url:
				return "//www.dailymotion.com/embed/video/"+re.search('video\/([a-zA-Z0-9]+)_',  self.video_url ).group(1)
			elif "vimeo" in self.video_url:
				return "https://player.vimeo.com/video/"+parsed[2][1:]+"?color=ab2203&title=0&byline=0&portrait=0&badge=0"
		else:
			return False

	def get_absolute_url(self):
		return reverse('members:detail-job', args=[self.id])

	def is_valid(self):
		if self.date_posted :
			if self.date_posted > timezone.now() - datetime.timedelta(days=settings.DAYS_JOB):
				return True
		return False

	def date_expire(self):
		return self.date_posted + datetime.timedelta(days=settings.DAYS_JOB)

	def interest_list(self):
		return self.interest_set.filter(decline=False)

	def delete_on_elasticsearch(self):
		try:
			es = Elasticsearch(['https://search-pitch-2k2jxfngnsvechhmkt5xiyyc4m.eu-west-1.es.amazonaws.com/'])
			es.delete(index="pitch", doc_type="job", id=self.id)
		except Exception:
			pass

	def save(self, *args, **kwargs):
		if self.active:
			if self.scraper == False:
				try:
					es = Elasticsearch(['https://search-pitch-2k2jxfngnsvechhmkt5xiyyc4m.eu-west-1.es.amazonaws.com/'])
					job=self
					js = {
						"id_pro": job.pro.id,
						"company": job.company,
						"title": job.job_title,
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
						"timestamp_posted": int(time.mktime(job.date_posted.timetuple())) if job.date_posted else "",
						"date_created": str(datetime.datetime.now()),
						"scraper": job.scraper
					}
					es.index(index="pitch", doc_type="job", id=job.id, body=json.dumps(js))
				except Exception:
					pass

		super(Job, self).save(*args, **kwargs)

	def __unicode__ (self):
		return self.job_title

	class Meta:
		ordering = ['-date_created']


class JobQuestion(models.Model):
	question = models.CharField(max_length=250, null=True)
	nb 		 = models.IntegerField(null=True)
	job 	 = models.ForeignKey(Job, related_name='questions', null=True, blank=True)
	pro 	 = models.ForeignKey(Pro, related_name='questions', null=True, blank=True)

	def __unicode__ (self):
		return self.question

	class Meta : 
		ordering = ['nb']


class SearchJob(models.Model):
	member = models.ForeignKey("members.Member", null=True)
	search = models.CharField(max_length=250, null=True, blank=True)

	def __unicode__ (self):
		return self.search

	class Meta:
		verbose_name = "Recherche job"
		verbose_name_plural = "Liste des recherches"

class SeenJob(models.Model):
	member 		= models.ForeignKey("members.Member", null=True)
	job    		= models.ForeignKey(Job, null=True)
	date_seen 	= models.DateTimeField(auto_now=True, null = True)

	class Meta:
		verbose_name = "Job consulté"
		verbose_name_plural = "Liste des jobs consultés"