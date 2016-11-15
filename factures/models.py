from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
import datetime, hashlib

class Facture(models.Model):
	user 			= models.ForeignKey(User, null=True)
	job 		 	= models.ForeignKey("pro.Job", null=True, blank=True)
	type_facture 	= models.IntegerField(null=True)
	first_name 		= models.CharField(max_length=150, null=True, blank=True)
	last_name 		= models.CharField(max_length=150, null=True, blank=True)
	company 		= models.CharField(max_length=150, null=True, blank=True)
	adresse 		= models.CharField(max_length=200, null=True, blank=True)
	cp 				= models.CharField(max_length=200, null=True, blank=True)
	city	 		= models.CharField(max_length=200, null=True, blank=True)
	email 			= models.CharField(max_length=200, null=True, blank=True)
	designation		= models.CharField(max_length=200, null=True, blank=True)
	reference 		= models.CharField(max_length=200, null=True, blank=True)
	quantite 		= models.CharField(max_length=200, null=True, blank=True)
	prix_ttc 		= models.DecimalField(default=0, max_digits=8, decimal_places=2)
	prix_ht 		= models.DecimalField(default=0, max_digits=8, decimal_places=2)
	tva 			= models.DecimalField(default=0, max_digits=8, decimal_places=2)
	date_created	= models.DateField(auto_now_add=True, null=True)
	paid 		 	= models.BooleanField(default=True)

	def save(self, *args, **kwargs):
		if not self.pk :
			self.prix_ht = float(self.prix_ttc) / 1.20
			self.tva = float(self.prix_ttc) - float(self.prix_ht)
		super(Facture, self).save(*args, **kwargs)

	class Meta:
		ordering = ["-date_created"]


class PaymentLink(models.Model):
	user 			= models.ForeignKey(User, null=True)
	designation		= models.CharField(max_length=200, null=True)
	description		= models.TextField(null=True, blank = True)
	prix_ht			= models.DecimalField(default=0, max_digits=8, decimal_places=2)
	paid 		 	= models.BooleanField(default=False)
	link 			= models.CharField(max_length=250, null=True, blank=True, help_text="http://pitchmyjob.com/pro/paiement/[link]")
	credit_job 		= models.IntegerField(default=0)
	credit_cv 		= models.IntegerField(default=0)

	def save(self, *args, **kwargs):
		if not self.pk :
			token = "sf5i9gd96P" + datetime.datetime.now().strftime("%s")
			self.link = hashlib.sha1(token).hexdigest()
		super(PaymentLink, self).save(*args, **kwargs)