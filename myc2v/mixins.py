# -*- coding: utf-8 -*-
from django import forms
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404

class UnicodeNameMixin(object):
	def __unicode__(self):
		return self.name

class BaseInscriptionMixin(forms.ModelForm):
	email = forms.CharField(error_messages={'required': 'Le champs Email est obligatoire.'})
	first_name = forms.CharField(error_messages={'required': 'Le champs Prénom est obligatoire.'})
	last_name = forms.CharField(error_messages={'required': 'Le champs Nom est obligatoire.'})
	password = forms.CharField(error_messages={'required': 'Le mot de passe est obligatoire.'})
	confirm_password = forms.CharField(error_messages={'required': 'La confirmation du mot de passe est obligatoire.'})
	cgu = forms.BooleanField( error_messages={'required': 'Veuillez accepter les conditions générales d\'utilisation.'} )

	def clean_password(self):
		pwd1 = self.cleaned_data.get('password')
		pwd2 = self.cleaned_data.get('confirm_password')
		if pwd1 != pwd2 :
			raise forms.ValidationError(u'Les mots de passe ne sont pas identique.', code='invalid')
		return pwd1

	def clean_email(self):
		email = self.cleaned_data['email'].strip()
		if 'yopmail' in email :
			raise forms.ValidationError(u'Les adresses yopmail ne sont pas accepté.', code='invalid')
		if User.objects.filter(username=email).exists() :
			raise forms.ValidationError(u'L\'email "%s" est déjà utilisée. Veuillez en choisir un autre.' % email, code='invalid')
		return email
 

class OnlyProLoginRequiredMixin(object):
	@method_decorator(login_required(login_url=settings.LOGIN_URL_PRO))
	def dispatch(self, *args, **kwargs):
		if not self.request.user.groups.filter(name='pro').exists():
			return redirect(settings.LOGIN_URL_PRO)
		return super(OnlyProLoginRequiredMixin, self).dispatch(*args, **kwargs )

class OnlyMemberLoginRequiredMixin(object):
	login_redirect = settings.LOGIN_URL
	@method_decorator(login_required(login_url = login_redirect))
	def dispatch(self, *args, **kwargs):
		if not self.request.user.groups.filter(name='member').exists():
			return redirect(self.login_redirect)
		return super(OnlyMemberLoginRequiredMixin, self).dispatch(*args, **kwargs )


class MyC2VLoginRequiredMixin(object):
	login_redirect = "/myc2v/connexion"
	@method_decorator(login_required(login_url = login_redirect))
	def dispatch(self, *args, **kwargs):
		if not self.request.user.groups.filter(name='member').exists():
			return redirect(self.login_redirect)
		return super(MyC2VLoginRequiredMixin, self).dispatch(*args, **kwargs )

class UpdateMemberMixin(object):
	def get_object(self, queryset=None):
		return self.request.user.member

class UpdateJobProMixin(object):
	def get_object(self, queryset=None):
		from pro.models import Job
		return get_object_or_404(Job, id= self.kwargs.get(self.pk_url_kwarg, None), pro = self.request.user.pro )

class TokenMixin(object):
	def get_context_data(self, **kwargs):
		from rest_framework.authtoken.models import Token
		context = super(TokenMixin, self).get_context_data(**kwargs)
		obj, created = Token.objects.get_or_create(user = self.request.user)
		context['key'] = obj
		return context