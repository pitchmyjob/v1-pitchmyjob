from django import forms
from django.contrib.auth.models import User


class ResetPasswordStepOneForm(forms.Form):
	email = forms.CharField(error_messages={'required': 'Veuillez saisir une adresse email.'})

	def clean_email(self):
		email = self.cleaned_data['email'].strip()
		if not User.objects.filter(username=email).exists() :
			raise forms.ValidationError(u'L\'email "%s" n\'exite pas.' % email, code='invalid')
		return email


class ResetPasswordStepThreeForm(forms.Form):
	confirm_password = forms.CharField(error_messages={'required': 'Veuillez confirmer le mot de passe.'})
	password = forms.CharField(error_messages={'required': 'Le mot de passe est obligatoire.'}, min_length=5)

	def clean_password(self):
		pwd1 = self.cleaned_data.get('password')
		pwd2 = self.cleaned_data.get('confirm_password')
		if pwd1 != pwd2 :
			raise forms.ValidationError(u'Les mots de passe ne sont pas identique.')
		return pwd1