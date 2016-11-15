# -*- coding: utf-8 -*-
from django import forms
from django.forms import ModelChoiceField
from myc2v.mixins import BaseInscriptionMixin
from members.models import Study, Experience
from .models import ActivityArea, Contract, Pro, Employes, ContractTime, Job
from django.core.files.base import ContentFile
import base64
from django.utils.translation import ugettext_lazy as _

class InscriptionForm(BaseInscriptionMixin, forms.ModelForm):
	company = forms.CharField(error_messages={'required': _(u'Le nom de société est obligatoire.')})
	phone = forms.CharField(error_messages={'required': _(u'Le téléphone est obligatoire.')})
	
	class Meta:
		model = Pro
		fields = ['first_name', 'last_name', 'email', 'confirm_password', 'password', 'company', 'phone']

class InscriptionStepTwoForm(forms.ModelForm):
	activity_area = forms.ModelChoiceField(queryset=ActivityArea.objects.filter(active=True), empty_label=_(u"Secteur d'activité"), error_messages={'required': _(u'Veuillez choisir un secteur d\'activité.')})
	employes = forms.ModelChoiceField(queryset=Employes.objects.filter(active=True), empty_label=_(u"Nombres d'employés"), error_messages={'required': _(u'Veuillez choisir un nombre d\'employés.')})

	class Meta:
		model = Pro
		fields = ['web_site', 'activity_area', 'headquarters', 'employes', 'ca', 'video_url', 'description', 'image', 'longitude', 'latitude', 'street_number', 'route', 'cp', 'locality', 'administrative_area_level_2', 'administrative_area_level_1', 'country'] 


class JobStepTwoForm(forms.ModelForm):
	contracts = forms.ModelMultipleChoiceField(queryset=Contract.objects.filter(active=True), widget=forms.CheckboxSelectMultiple,  error_messages={'required': _(u'Veuillez choisir au minimum un type de contrat.')})
	contract_time = forms.ModelMultipleChoiceField(queryset=ContractTime.objects.filter(active=True), widget=forms.CheckboxSelectMultiple,  error_messages={'required': _(u'Veuillez choisir au minimum une durée de contrat.')})
	experiences = forms.ModelMultipleChoiceField(queryset=Experience.objects.filter(active=True), widget=forms.CheckboxSelectMultiple, error_messages={'required': _(u'Veuillez choisir au minimum un niveau d\'expérience professionnel.')})
	studies = forms.ModelMultipleChoiceField(queryset=Study.objects.filter(active=True), widget=forms.CheckboxSelectMultiple, error_messages={'required': _(u'Veuillez choisir un niveau d\'étude.')})

	class Meta:
		model = Job
		fields = ['contract_time', 'contracts', 'experiences', 'studies', 'salary']


class JobStepTreeForm(forms.ModelForm):
	tags_field = forms.CharField(error_messages={'required': _(u'Veuillez saisir au moins 3 tags.')})
	description = forms.CharField( error_messages={'required': _(u'Veuillez écrire une description.')}, widget=forms.Textarea )

	def clean_tags_field(self):
		tags = self.cleaned_data['tags_field'].split(',')
		if len(tags) < 3:
			raise forms.ValidationError(_(u'Veuillez saisir au moins 3 tags.'))
		return self.cleaned_data['tags_field']

	class Meta:
		model = Job
		fields = ['description', 'mission', 'profile', 'tags_field', 'video_url']

class JobStepFourForm(forms.ModelForm):
	qt = forms.CharField(error_messages={'required': _(u'Veuillez ecrire au moins une question.')})

	def clean(self):
		if not self.cleaned_data['is_video'] and not self.cleaned_data['is_audio'] and not self.cleaned_data['is_text'] :
			raise forms.ValidationError(_(u'Veuillez choisir au moins un type de reponse.'))
		else :
			return self.cleaned_data

	class Meta:
		model = Job
		fields = ['qt', 'is_video', 'is_audio', 'is_text']

class ProfilForm(forms.ModelForm):
	qt = forms.CharField(required=False)
	video_url = forms.CharField(required=False)
	cover = forms.CharField(required=False)

	def clean_video_url(self):
		if self.cleaned_data['video_url']:
			if "youtube" in self.cleaned_data['video_url'] or "dailymotion" in self.cleaned_data['video_url'] or "vimeo" in self.cleaned_data['video_url']:
				return self.cleaned_data['video_url']
			raise forms.ValidationError(_(u"L'url de la video doit etre un lien Youtube, Dailymotion ou Viemo uniquement.")) 

	def clean_cover(self):
		if self.cleaned_data['cover']:
			data = self.cleaned_data['cover']
			if isinstance(data, basestring) and data.startswith('data:image'):
				# base64 encoded image - decode
				format, imgstr = data.split(';base64,')  # format ~= data:image/X,
				ext = format.split('/')[-1]  # guess file extension 

				return ContentFile(base64.b64decode(imgstr), name='cover.' + ext)

	class Meta:
		model = Pro
		fields = ['company', 'web_site', 'activity_area', 'employes', 'ca', 'description', 'image', 'cover', 'link_facebook', 'link_twitter', 'link_youtube', 'qt', 'video_url']


class C2VThequeSearchForm(forms.Form):
	s   = forms.CharField()
	p   = forms.CharField()
	sa 	= forms.ModelChoiceField(queryset=ActivityArea.objects.filter(active=True), empty_label="Secteur d'activité") #secteur d'activite
	c 	= forms.ModelChoiceField(queryset=Contract.objects.filter(active=True), empty_label="Tous les contrats") #type de contrat
	e 	= forms.ModelChoiceField(queryset=Study.objects.filter(active=True), empty_label="Niveau d'étude actuel") #niveau d'etude 
	exp = forms.ModelMultipleChoiceField(queryset=Experience.objects.filter(active=True), widget=forms.CheckboxSelectMultiple ) #experience
	sd  = forms.DecimalField() #salare debut
	sf  = forms.DecimalField() #salaire fin
	d   = forms.ChoiceField(choices = ( (1, _(u'Immediate')), (0, _(u'Avec préavis')) ) ,widget=forms.RadioSelect  ) #disponibilite
	cn 	= forms.MultipleChoiceField(choices = ( (1, _(u'Il y a 1 jour')), (5, _(u'Moins de 5 jours')), (30, _(u'Moins de 1 mois')), (180, _(u'Moins de 6 mois')) ) , widget=forms.CheckboxSelectMultiple  ) #derniere connexion
	la 	= forms.CharField()
	a1	= forms.CharField()
	a2  = forms.CharField()
	ct 	= forms.CharField()

class BaseSearchC2vThequeFormMixin(object):
	def get_context_data(self, **kwargs):
		context= super(BaseSearchC2vThequeFormMixin, self).get_context_data(**kwargs)
		context['form'] = C2VThequeSearchForm(self.request.GET)
		return context 