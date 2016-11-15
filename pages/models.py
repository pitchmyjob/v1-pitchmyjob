from __future__ import unicode_literals
from django.db import models
from datetime import date

class Contact(models.Model): 
	first_name 	= models.CharField(max_length=150, null=True)
	last_name 	= models.CharField(max_length=150, null=True)
	email 		= models.CharField(max_length=150, null=True)
	objets 		= models.CharField(max_length=200, null=True)
	message 	= models.TextField(null=True)


class Apec(models.Model): 
	identifiant = models.CharField(max_length=150, null=True)
	titre 		= models.CharField(max_length=150, null=True) 
	nom 		= models.CharField(max_length=150, null=True)
	prenom 		= models.CharField(max_length=150, null=True)
	email 		= models.CharField(max_length=150, null=True)
	phone 		= models.CharField(max_length=150, null=True)
	formation   = models.CharField(max_length=150, null=True)
	experience  = models.CharField(max_length=150, null=True)
	ville 		= models.CharField(max_length=150, null=True)
	birthday 	= models.DateField(null=True)
	dispo 		= models.CharField(max_length=150, null=True)
	publication = models.DateField(null=True)
	region  	= models.CharField(max_length=150, null=True)
	sent    	= models.BooleanField(default=False)
	vague    	= models.IntegerField(null=True)

	def age(self):
		today = date.today()
		return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day))

	class Meta:
		ordering = ['-publication', ]