# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User


class Message(models.Model):
	sender 		 = models.ForeignKey(User, null=True, related_name="message_sent")
	receiver 	 = models.ForeignKey(User, null=True, related_name="message_received")
	message 	 = models.TextField(null=True)
	group		 = models.IntegerField(default = 0) # 1 = Message d'un member #2 = message d'un pro
	active 		 = models.BooleanField(default=True)
	date_posted  = models.DateTimeField(auto_now_add=True, null=True)
	view 		 = models.IntegerField(default=0)


class Block(models.Model):
	blocker  	 = models.ForeignKey(User, null=True, related_name="blocking")
	blocked  	 = models.ForeignKey(User, null=True, related_name="blocked")
	type_block	 = models.IntegerField(default = 0)
	motif		 = models.IntegerField(default = 0)
	date_block   = models.DateTimeField(auto_now_add=True)


class Notification(models.Model):
	sender 		 = models.ForeignKey(User, null=True, related_name="notification_sent", blank=True)
	receiver 	 = models.ForeignKey(User, null=True, related_name="notification_received", blank=True)
	job 		 = models.ForeignKey("pro.Job", null=True, blank=True)
	type_notif   = models.IntegerField(null=True)	
	group		 = models.IntegerField(default = 0) # 1 = Message d'un member #2 = message d'un pro
	view 		 = models.IntegerField( default = 0 )
	last_update	 = models.DateTimeField(auto_now=True, null = True)