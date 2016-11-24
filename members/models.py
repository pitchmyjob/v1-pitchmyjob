# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from myc2v.mixins import UnicodeNameMixin
from easy_thumbnails.fields import ThumbnailerImageField
from django.conf import settings
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
import os
import json
from elasticsearch import Elasticsearch
from django.db.models.signals import pre_delete
from django.dispatch import receiver
import uuid
import time, datetime

def generate_filename(self, filename):
	filename, file_extension = os.path.splitext(filename)
	filename = slugify(filename)
	name = str(uuid.uuid4()) + str(file_extension)
	url = "c2v/%s/%s" % (self.id, name )
	return url

def validate_file_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.pdf']
    if not ext in valid_extensions:
        raise ValidationError(u'Format non valide. Veuillez importer un fichier pdf.')

def candidature_file(self, filename):
	filename, file_extension = os.path.splitext(filename)
	filename = slugify(filename)
	url = "candidatures/%s" % (str(filename) + str(file_extension) )
	return url

class Study(UnicodeNameMixin, models.Model):
	name 	= models.CharField(max_length=200, null=True)
	active 	= models.BooleanField(default=True)
	ordre 	= models.IntegerField(default=0)

	class Meta:
		ordering = ["ordre"]
		verbose_name = "Niveau d'étude"
		verbose_name_plural = "Liste niveau d'étude"

class Experience(UnicodeNameMixin, models.Model):
	name 	= models.CharField(max_length=200, null=True)
	active 	= models.BooleanField(default=True)
	ordre 	= models.IntegerField(default=0)

	class Meta:
		ordering = ["ordre"]
		verbose_name = "Expérience"
		verbose_name_plural = "Liste expérience"

class Member(models.Model): 
	user 			= models.OneToOneField(User)
	first_name 		= models.CharField(max_length=150, null=True)
	last_name 		= models.CharField(max_length=150, null=True)
	email 			= models.CharField(max_length=200, null=True)
	birthday		= models.DateField(null = True, blank=True)
	job_wanted		= models.CharField(max_length=150, null=True, blank=True)
	study 			= models.ForeignKey(Study, null=True)
	activity_area	= models.ManyToManyField("pro.ActivityArea", blank=True)
	experience 		= models.ForeignKey(Experience, null=True)
	contracts		= models.ManyToManyField('pro.Contract', blank=True)
	phone 			= models.CharField(max_length=200, null=True, blank=True)
	salary			= models.DecimalField(max_digits=9, decimal_places=2, null=True, blank=True)
	availability	= models.DateField(null = True, blank=True)
	search_location = models.CharField(max_length=200, null=True, blank=True)
	locality 		= models.CharField(max_length=200, null=True, blank=True)
	administrative_area_level_2 = models.CharField(max_length=200, null=True, blank=True)
	administrative_area_level_1 = models.CharField(max_length=200, null=True, blank=True)
	country			= models.CharField(max_length=200, null=True, blank=True)
	image 			= ThumbnailerImageField(upload_to=generate_filename, default="c2v/mycv_default.png")
	last_visit 		= models.DateTimeField(null=True, blank=True)
	token_password 	= models.CharField(max_length=200, null=True, blank=True)
	rs_pwd 		 	= models.BooleanField(default=False)
	rs_type 		= models.IntegerField(null=True, default=0) #inscription normal, 1 - inscription linkedin, 2 - inscription doyoubuzz, 3 - facebook, 4 - Viadeo
	rs_doyoubuzz_cv = models.FileField(null=True, blank=True, upload_to='doyoubuzz/')
	tags 			= models.ManyToManyField("pro.Tag", blank=True)
	cv_pdf 			= models.FileField(upload_to=generate_filename, null=True, blank=True)
	school			 = models.CharField(max_length=150, null=True, blank=True)


	def save(self, *args, **kwargs):
		try:
			if self.cv :
				self.save_on_elasticsearch()
		except Exception:
			pass
		super(Member, self).save(*args, **kwargs)

	def experiences_count(self):
		return self.cv.cvexperience_set.count()

	def filename(self):
		return os.path.basename(self.cv_pdf.name)

	def delete_on_elasticsearch(self):
		try:
			es = Elasticsearch(['https://search-pitch-2k2jxfngnsvechhmkt5xiyyc4m.eu-west-1.es.amazonaws.com/'])
			es.delete(index="pitch", doc_type="cv", id=self.id)
		except Exception:
			pass

	def save_on_elasticsearch(self):
		try:
			member = self
			js = {
				"first_name": member.first_name,
				"last_name": member.last_name,
				"email": member.email,
				"image": member.image.url,
				"study": member.study.name if member.study else '',
				"industry": list(member.activity_area.values_list('name', flat=True)),
				"experience": member.experience.name if member.experience else  '',
				"contracts": list(member.contracts.values_list('name', flat=True)),
				"tags": {
					"count": member.tags.count(),
					"datas": list(member.tags.values_list('name', flat=True)) if member.tags else []
				},
				"location": {
					"locality": member.locality,
					"country": member.country,
					"administrative_area_level_1": member.administrative_area_level_1,
					"administrative_area_level_2": member.administrative_area_level_2
				},
				"poste": member.cv.poste,
				"experiences": {
					"count": member.cv.cvexperience_set.count(),
					"datas": [{"title": exp.title, "company": exp.company,"description": exp.description.replace('\r', '').replace('\n',' ') if exp.description else ''}for exp in member.cv.cvexperience_set.all()]
				},
				"formations": {
					"count": member.cv.cvformation_set.count(),
					"datas": [{"school": fm.school, "degree": fm.degree} for fm in member.cv.cvformation_set.all()]
				},
				"skills": {
					"count": member.cv.cvskill_set.count(),
					"datas": list(member.cv.cvskill_set.values_list('name', flat=True))
				},
				"languages": [lg.name for lg in member.cv.cvlanguage_set.all()],
				"interets": [inter.name for inter in member.cv.cvinterest_set.all()],
				"timestamp_joined": int(time.mktime(member.user.date_joined.timetuple())),
				"date_joined": str(member.user.date_joined)
			}

			es = Elasticsearch(['https://search-pitch-2k2jxfngnsvechhmkt5xiyyc4m.eu-west-1.es.amazonaws.com/'])
			es.index(index="pitch", doc_type="cv", id=member.id, body=json.dumps(js))
		except Exception:
			pass

	def __unicode__(self):
			return self.first_name+" "+self.last_name+" - "+self.user.email


@receiver(pre_delete, sender=Member, dispatch_uid='delete_es_signal')
def delete_on_es(sender, instance, using, **kwargs):
	instance.delete_on_elasticsearch()


class Video(models.Model):
	video_id		= models.CharField(max_length=250, null=True, blank=True, help_text="https://s3.eu-central-1.amazonaws.com/pitchmyjob/[video_id].mp4")
	type_video		= models.IntegerField(default=0, blank=True, null=True) # 0 = direct upload, 1 = webcam, 2 = lien youtube, 3 lien dailymotion, 4 lien vimeo
	embed_url		= models.CharField(max_length=250, null=True, blank=True)
	link_url		= models.CharField(max_length=250, null=True, blank=True)
	file_on_server 	= models.FileField(upload_to='videos', null=True, blank=True)
	date_created	= models.DateField(auto_now_add=True, null=True, blank=True)
	member 			= models.ForeignKey(Member, null=True, blank=True)
	job 			= models.ForeignKey("pro.Job", null=True, blank=True)
	date_updated	= models.DateTimeField(auto_now=True, null=True)
	aws 			= models.BooleanField(default=False)

	def url(self):
		if self.type_video == 2 or  self.type_video == 0 :
			return "http://www.youtube.com/embed/"+self.video_id+"?rel=0&amp;showinfo=0"
		if self.type_video == 3 :
			return "//www.dailymotion.com/embed/video/"+self.video_id
		if self.type_video == 4:
			return "https://player.vimeo.com/video/"+self.video_id+"?color=ab2203&title=0&byline=0&portrait=0&badge=0"

	def path_video(self):
		return "/media/records/"+self.video_id+".mp4"

	def path_aws(self):
		return "https://s3.eu-central-1.amazonaws.com/pitchmyjob/candidatures/"+str(self.video_id)+".mp4"

	def path_aws_v2(self):
		return "https://s3.eu-central-1.amazonaws.com/pitchmyjob/" + str(self.video_id) + ".mp4"

	def __unicode__(self):
		return str("https://s3.eu-central-1.amazonaws.com/pitchmyjob/" + self.video_id + ".mp4")

class Audio(models.Model):
	audio_id 		= models.CharField(max_length=250, null=True, blank=True)
	file_on_server 	= models.FileField(upload_to='audios', null=True, blank=True)
	date_created	= models.DateField(auto_now_add=True, null=True,  blank=True)


class Candidature(models.Model):
	job 		 = models.ForeignKey("pro.Job", null=True, blank=True)
	member 		 = models.ForeignKey(Member, null=True, blank=True)
	mode 		 = models.IntegerField(default=0, blank=True)
	active 		 = models.BooleanField(default=False) #signifie que la candiature a ete faite jusqu'au bout
	decline 	 = models.BooleanField(default=False) #True = la candidature a été decliné
	video 		 = models.OneToOneField(Video, related_name = "candidature",  null=True, blank=True)
	audio 		 = models.OneToOneField(Audio, related_name = "candidature",  null=True, blank=True)
	date_posted  = models.DateField(auto_now_add=True, null=True,  blank=True)
	date_updated = models.DateTimeField(auto_now=True,  null=True)
	cv 		 	 = models.FileField(upload_to=candidature_file, null=True,  blank=True, validators=[validate_file_extension] )
	new 		 = models.BooleanField(default=False)  # nouveau systeme de candidature

	def __unicode__(self):
			return str(self.id)

class CandidatureReponse(models.Model):
	candidature  = models.ForeignKey(Candidature, null=True)
	nb 			 = models.IntegerField(null=True, blank=True)
	text 		 = models.TextField(null=True, blank=True)
	active 		 = models.BooleanField(default=False)
	video 		 = models.OneToOneField(Video, related_name = "candidature_reponse",  null=True, blank=True)
	audio 		 = models.OneToOneField(Audio, related_name = "candidature_reponse",  null=True, blank=True)
	time 		 = models.IntegerField(null=True, blank=True)

	def __unicode__(self):
			return str(self.id)
	class Meta : 
		ordering = ['nb']

class Interest(models.Model):
	job    	= models.ForeignKey("pro.Job", null=True)
	member 	= models.ForeignKey(Member, null=True)
	date   	= models.DateField(auto_now_add=True, null=True, blank=True)
	decline = models.BooleanField(default=False)

	class Meta:
		verbose_name = "Interet"
		verbose_name_plural = "Liste des interessés"
		ordering = ['-date']


class Tips(models.Model):
	tips = models.CharField(max_length=250, null=True, blank=True)

	def __unicode__(self):
		return unicode(self.tips)