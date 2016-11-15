from __future__ import unicode_literals
from django.db import models
from members.models import Member
from easy_thumbnails.fields import ThumbnailerImageField
from django.template.defaultfilters import slugify
import os
import uuid

def generate_filename(self, filename):
	filename, file_extension = os.path.splitext(filename)
	filename = slugify(filename)
	name = str(filename) + "-" +str(uuid.uuid4()) + str(file_extension)
	url = "c2v/logo/%s" % ( name )
	return url

class Cv(models.Model):
	member 		= models.OneToOneField(Member)
	first_name  = models.CharField(max_length=250, null=True, blank = True)
	last_name   = models.CharField(max_length=250, null=True, blank = True)
	email		= models.CharField(max_length=250, null=True, blank = True)
	birthday	= models.DateField(null = True)
	title		= models.CharField(max_length=250, null=True, blank = True)
	poste		= models.CharField(max_length=250, null=True, blank = True) #headline
	city		= models.CharField(max_length=250, null=True, blank = True)
	country		= models.CharField(max_length=250, null=True, blank = True)
	phone		= models.CharField(max_length=250, null=True, blank = True)
	site		= models.CharField(max_length=250, null=True, blank = True)
	description	= models.TextField(null=True, blank = True)
	theme 		= models.IntegerField(default=1, blank=True)

class CvExperience(models.Model):
	cv 			= models.ForeignKey(Cv) 
	company		= models.CharField(max_length=250, null=True)
	title		= models.CharField(max_length=250, null=True)
	location	= models.CharField(max_length=250, null=True, blank = True)
	date_start  = models.DateField(null=True)
	date_end    = models.DateField(null=True, blank = True)
	description	= models.TextField(null=True, blank = True)
	image 		= ThumbnailerImageField(upload_to=generate_filename, null = True, blank = True)

	class Meta:
		ordering = ['-date_start', '-date_end'] 

class CvFormation(models.Model):
	cv 			= models.ForeignKey(Cv) 
	school  	= models.CharField(max_length=250, null=True)
	date_start  = models.DateField(null=True)
	date_end    = models.DateField(null=True)
	degree		= models.CharField(null=True, max_length=250)
	discipline	= models.CharField(null=True, max_length=250)
	description	= models.TextField(null=True, blank = True)
	image 		= ThumbnailerImageField(upload_to=generate_filename, null = True, blank = True)

	class Meta:
		ordering = ['-date_start', '-date_end'] 

class CvSkill(models.Model):
	cv 			= models.ForeignKey(Cv) 
	name 		= models.CharField(max_length=250, null=True)
	level 		= models.IntegerField(null=True)

class CvLanguage(models.Model):
	cv 			= models.ForeignKey(Cv) 
	name 		= models.CharField(max_length=250, null=True)
	level 		= models.IntegerField(null=True)

class CvInterest(models.Model):
	cv 			= models.ForeignKey(Cv) 
	name 		= models.CharField(max_length=250, null=True)