# -*- coding: utf-8 -*-
from django import forms
from members.models import Member, Study, Experience, Video, Candidature, CandidatureReponse, Audio
from pro.models import ActivityArea, Contract, ContractTime, Job
from myc2v.mixins import BaseInscriptionMixin
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils.translation import ugettext_lazy as _
from django.core.files.base import ContentFile
import base64

class LoginForm(forms.Form):
	username = forms.EmailField(error_messages={'required': _(u'Le champs Email est obligatoire.'), 'invalid':_(u'L\'email n\'est pas valide.')})
	password = forms.CharField(error_messages={'required': _(u'Le mot de passe est obligatoire.')})

class InscriptionForm(forms.ModelForm):
	#birthday = forms.DateField(required=False, error_messages={'required': _(u'Le champs Date de naissance est obligatoire.'), 'invalid':_(u'Veuillez saisir une date valide (sous forme dd/mm/YYYY).')}, widget=forms.DateInput(format = '%d/%m/%Y'))
	#phone = forms.CharField(required=False, error_messages={'required': _(u'Le numero de téléphone permet au recruteur de vous contacter.')})
	mdp = forms.CharField()

	def clean_email(self):
		email = self.cleaned_data['email'].strip()
		if 'yopmail' in email:
			raise forms.ValidationError(u'Les adresses yopmail ne sont pas accepté.', code='invalid')
		if User.objects.filter(username=email).exists():
			raise forms.ValidationError(u'L\'email "%s" est déjà utilisée. Veuillez en choisir un autre.' % email,code='invalid')
		return email

	class Meta:
		model = Member
		fields = ['first_name', 'last_name', 'email', 'mdp'] #confirm_password


class OldInscriptionForm(forms.ModelForm):
	birthday = forms.DateField(required=False, error_messages={'required': _(u'Le champs Date de naissance est obligatoire.'), 'invalid':_(u'Veuillez saisir une date valide (sous forme dd/mm/YYYY).')}, widget=forms.DateInput(format = '%d/%m/%Y'))
	phone = forms.CharField(required=False, error_messages={'required': _(u'Le numero de téléphone permet au recruteur de vous contacter.')})
	password = forms.CharField()

	def clean_email(self):
		email = self.cleaned_data['email'].strip()
		if 'yopmail' in email:
			raise forms.ValidationError(u'Les adresses yopmail ne sont pas accepté.', code='invalid')
		if User.objects.filter(username=email).exists():
			raise forms.ValidationError(u'L\'email "%s" est déjà utilisée. Veuillez en choisir un autre.' % email,code='invalid')
		return email

	class Meta:
		model = Member
		fields = ['first_name', 'last_name', 'email', 'password', 'phone', 'birthday'] #confirm_password


class InscriptionStepTwoForm(forms.ModelForm):
	study = forms.ModelChoiceField(queryset=Study.objects.filter(active=True), empty_label=_(u"Niveau d'étude actuel"), error_messages={'required': _(u'Veuillez choisir un niveau d\'étude.')})
	activity_area = forms.ModelMultipleChoiceField(queryset=ActivityArea.objects.filter(active=True), error_messages={'required': _(u'Veuillez choisir un secteur d\'activité.')})
	experience = forms.ModelChoiceField(queryset=Experience.objects.filter(active=True), empty_label=_(u"Année d'expérience professionnel"), error_messages={'required': _(u'Veuillez choisir un niveau d\'expérience professionnel.')})
	contracts = forms.ModelMultipleChoiceField(queryset=Contract.objects.filter(active=True), widget=forms.CheckboxSelectMultiple,  error_messages={'required': _(u'Veuillez choisir au minimum un type de contrat.')})
	#job_wanted = forms.CharField(error_messages={'required': _(u'Veuillez indiquer un métier recherché.')}, required=False)
	salary = forms.DecimalField(required=False)
	#availability = forms.DateField(required=False, error_messages={'invalid':_(u'Veuillez saisir une date de disponibilité valide (sous forme dd/mm/YYYY).')}, widget=forms.DateInput(format = '%d/%m/%Y'))
	tags_field = forms.CharField(required=True, error_messages={'required': _(u'Veuillez remplir au moins un tag.')})
	image = forms.ImageField(required=True, error_messages={'required': _(u'Veuillez mettre une photo.')})
	
	
	class Meta:
		model = Member
		fields = ['image', 'study', 'activity_area', 'experience', 'contracts', 'salary', 'search_location', 'locality', 'administrative_area_level_2', 'administrative_area_level_1', 'country', 'tags_field'] 


class VideoForm(forms.ModelForm):
	class Meta:
		model = Video
		fields = "__all__"


class AudioForm(forms.Form):
	class Meta:
		model = Audio

class SearchForm(forms.Form):
	activity_area   = forms.ModelChoiceField(queryset=ActivityArea.objects.filter(active=True), empty_label=_(u"Secteur d'activité"))	
	study 			= forms.ModelChoiceField(queryset=Study.objects.filter(active=True), empty_label=_(u"Niveau d'étude actuel"))
	experiences   	= forms.ModelMultipleChoiceField(queryset=Experience.objects.filter(active=True), widget=forms.CheckboxSelectMultiple)
	contracts 		= forms.ModelMultipleChoiceField(queryset=Contract.objects.filter(active=True), widget=forms.CheckboxSelectMultiple)
	contract_time   = forms.ModelMultipleChoiceField(queryset=ContractTime.objects.filter(active=True), widget=forms.CheckboxSelectMultiple)
	search 			= forms.CharField()
	place 			= forms.CharField()
	locality 					= forms.CharField()
	administrative_area_level_2	= forms.CharField()
	administrative_area_level_1 = forms.CharField()
	country 					= forms.CharField()


class CandidatureStepTwoForm(forms.ModelForm):
	cv 	= forms.FileField(required=False)

	class Meta:
		model = Candidature
		fields = ['cv', ]

class CandidatureStepThreeForm(forms.ModelForm):
	mode = forms.IntegerField(min_value=1, max_value=3, required=True)
	class Meta:
		model = Candidature
		fields = ['mode', 'member', 'active', 'job']

class ReponseForm(forms.ModelForm):
	text = forms.CharField(required=True, widget=forms.Textarea, error_messages={'required': _(u'Veuillez repondre à la question.')})
	class Meta:
		model = CandidatureReponse
		fields = ['text']


class BaseSearchFormMixin(object):
	def get_context_data(self, **kwargs):
		context= super(BaseSearchFormMixin, self).get_context_data(**kwargs)
		context['form'] = SearchForm(self.request.GET)
		return context 


class MyAccountForm(BaseInscriptionMixin, forms.ModelForm):
	class Meta:
		model = Member
		fields = ['first_name', 'last_name', 'email', 'birthday']

class ChangePasswordForm(forms.Form):
	old_password = forms.CharField(required=True, error_messages={'required': _(u'Veuillez saisir l\'ancien mot de passe.')})
	confirm_password = forms.CharField(required=False)
	password = forms.CharField(error_messages={'required': _(u'Veuillez saisir votre nouveau mot de passe.')}, min_length=5)

	def __init__(self, *args, **kwargs):
		self.user = kwargs.pop('user')
		# now kwargs doesn't contain 'place_user', so we can safely pass it to the base class method
		super(ChangePasswordForm, self).__init__(*args, **kwargs)

	def clean_old_password(self):
		if authenticate(username=self.user, password=self.cleaned_data['old_password']) is None :
			raise forms.ValidationError(_(u'L\'ancien mot de passe n\'est pas bon. Veuillez recommencer.') )
		return self

	def clean_password(self):
		pwd1 = self.cleaned_data.get('password')
		pwd2 = self.cleaned_data.get('confirm_password')
		if pwd1 != pwd2 :
			raise forms.ValidationError(_(u'Les mots de passe ne sont pas identique.'))
		return pwd1


class FbConnectPasswordForm(forms.ModelForm):
	confirm_password = forms.CharField(required=False)
	password = forms.CharField(error_messages={'required': _(u'Veuillez saisir votre nouveau mot de passe.') }, min_length=5)

	def clean_password(self):
		pwd1 = self.cleaned_data.get('password')
		pwd2 = self.cleaned_data.get('confirm_password')
		if pwd1 != pwd2 :
			raise forms.ValidationError(_(u'Les mots de passe ne sont pas identique.'))
		return pwd1

	class Meta:
		model = Member
		fields = ['confirm_password', 'password']


class ApplyFormCv(forms.Form):
	cv = forms.FileField(required=False)


class ApplyForm(forms.Form):
	cv 			= forms.FileField(required=True)
	photo 		= forms.CharField(required=True)
	last_name  	= forms.CharField(required=True)
	first_name  = forms.CharField(required=True)
	email	    = forms.CharField(required=True)
	mdp	    	= forms.CharField(required=True)

	def clean_photo(self):
		if self.cleaned_data['photo']:
			data = self.cleaned_data['photo']

			missing_padding = len(data) % 4
			if missing_padding != 0:
				data += b'=' * (4 - missing_padding)

			if isinstance(data, basestring) and data.startswith('data:image'):
				# base64 encoded image - decode
				format, imgstr = data.split(';base64,')  # format ~= data:image/X,
				ext = format.split('/')[-1]  # guess file extension

				missing_padding = len(imgstr) % 4
				if missing_padding != 0:
					imgstr += b'=' * (4 - missing_padding)

				return ContentFile(base64.b64decode(imgstr), name='photo.' + ext)