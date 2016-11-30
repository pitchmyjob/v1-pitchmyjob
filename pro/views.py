# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic import FormView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse, reverse_lazy
from pro.forms import InscriptionForm, InscriptionStepTwoForm, JobStepTwoForm, JobStepTreeForm, JobStepFourForm, ProfilForm, BaseSearchC2vThequeFormMixin
from myc2v.mixins import OnlyProLoginRequiredMixin, UpdateJobProMixin, TokenMixin
from members.forms import LoginForm, ChangePasswordForm
from members.models import Member
from .models import Pro, Job, Tag, JobQuestion
from members.models import Candidature
from django.conf import settings
from django import forms
import datetime
from django.db.models import Q, Count
from notifications.models import Message, Notification
from notifications.notifications import notification
from django.core.paginator import Paginator
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from factures.models import Facture, PaymentLink
from factures.paiement import Paiement
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from pure_pagination.mixins import PaginationMixin

def home(request):
	if request.user.is_authenticated() and request.user.groups.filter(name='pro').exists():
		return HttpResponseRedirect( reverse('pro:offres')  )
	return render(request, 'home-pro-2.html')

def home_2(request):
	return render(request, 'home-pro-2.html')

def login_view(request):
	form = LoginForm(request.POST or None)
	if form.is_valid():
		user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
		if user is not None:
			if user.groups.filter(name='pro').exists():
				login(request, user)
				if request.GET.get('next') :
					return HttpResponseRedirect( request.GET.get('next', '/') )
				else :
					return HttpResponseRedirect( reverse('pro:offres')  )
			else:
				form.add_error(None, _(u'Veuillez vous connecter avec un compte Pro.'))
		else:
			form.add_error(None, _(u'L\'email et le mot de passe ne correspondent pas.'))

	context = {"form":form}
	return render(request, 'pro/login.html', context)

class InscriptionCreate(CreateView):
	model = Pro
	form_class = InscriptionForm
	template_name = 'pro/inscription.html'

	def form_valid(self, form):
		self.object  = form.save( commit=False )
		user = User.objects.create_user(self.object.email, self.object.email, form.cleaned_data.get('password'))
		user.groups.add( Group.objects.get(name='pro')  )
		user.save()
		self.object.user = user
		self.object.save()
		login(self.request, authenticate(username=self.object.email, password=form.cleaned_data.get('password')))
		return HttpResponseRedirect( reverse('pro:inscription-step-2') )

class InscriptionProUpdate(UpdateView):
	model = Pro
	form_class = InscriptionForm
	template_name = 'pro/inscription.html'

	def get_context_data(self, **kwargs):
		context = super(InscriptionProUpdate, self).get_context_data(**kwargs)
		context['pro'] = True
		return context

	def get_initial(self):
		initial = super(InscriptionProUpdate, self).get_initial()
		initial['first_name'] = "" 
		initial['last_name'] = ""
		initial['email'] = ""
		initial['phone'] = ""
		return initial

	def get_object(self, queryset=None):
		username = self.kwargs.get(self.slug_url_kwarg, None)
		user = User.objects.filter(username__iexact=username)
		if user.exists():
			user = user.first()
			if not user.groups.filter(name='pro').exists() and not user.groups.filter(name='member').exists():
				return user.pro
		raise Http404

	def form_valid(self, form):
		pro = form.save()
		pro.user.set_password( form.cleaned_data.get('password') )
		pro.user.email = pro.email
		pro.user.username = pro.email
		pro.user.groups.add( Group.objects.get(name='pro')  )
		pro.user.save()
		login(self.request, authenticate(username=pro.user.username, password=form.cleaned_data.get('password')))
		return HttpResponseRedirect( reverse('pro:inscription-step-2') )

class InscriptionStepTwoUpdate(OnlyProLoginRequiredMixin, UpdateView):
	model = Pro
	form_class = InscriptionStepTwoForm
	template_name = 'pro/inscription-step-two.html'
	success_url = '/pro/offres'

	def get_object(self, queryset=None):
		return self.request.user.pro


class MyAccountUpdate(OnlyProLoginRequiredMixin, UpdateView):
	model = Pro
	success_url = '/pro/mon-compte'
	template_name = 'pro/my-account.html'
	fields = ['first_name', 'last_name', 'headquarters', 'phone', 'latitude', 'longitude', 'street_number', 'route', 'locality', 'administrative_area_level_2', 'administrative_area_level_1', 'country']

	def get_object(self, queryset=None):
		return self.request.user.pro


class MyAccountPasswordUpdate(OnlyProLoginRequiredMixin, FormView): 
	form_class = ChangePasswordForm
	template_name = 'pro/my-account-password.html'

	def get_form_kwargs(self):
		kwargs = super(MyAccountPasswordUpdate, self).get_form_kwargs()
		kwargs.update({'user': self.request.user})
		return kwargs

	def form_valid(self, form):
		email = self.request.user.email
		self.request.user.set_password( form.cleaned_data.get('password') )
		self.request.user.save()
		login(self.request, authenticate(username=email, password=form.cleaned_data.get('password')))
		messages.add_message(self.request, messages.INFO, _(u'Votre mot de passe a bien été modifié.'))
		return HttpResponseRedirect( reverse('pro:my-account-password') )

class ListeOffreView(OnlyProLoginRequiredMixin, ListView):
	model = Job
	template_name = 'pro/list-offre.html'

	def get_queryset(self):
		return self.request.user.pro.job_set.filter(active=True)

class OffreDelete(OnlyProLoginRequiredMixin, UpdateView):
	model = Job
	template_name = 'pro/list-offre.html'
	fields = ['active']

	def get_context_data(self, **kwargs):
		context = super(OffreDelete, self).get_context_data(**kwargs)
		context ['object_list'] = self.request.user.pro.job_set.filter(active=True)
		context ['delete'] 	= True
		return context

	def form_valid(self, form):
		self.object = form.save()
		self.object.delete_on_elasticsearch()
		notification(4, None, self.request.user.pro, self.object)
		return HttpResponseRedirect( reverse('pro:offres') ) 

class JobStepOneCreate(OnlyProLoginRequiredMixin, CreateView):
	model = Job
	fields = ['company', 'job_title', 'contact', 'job_location', 'web_site', 'activity_area', 'image', 'longitude', 'latitude', 'route', 'street_number' , 'route', 'locality', 'administrative_area_level_2', 'administrative_area_level_1', 'country'] 
	template_name = 'pro/job-form-step-one.html'

	def get_initial(self):
		initial = super(JobStepOneCreate, self).get_initial()
		initial['company'] = self.request.user.pro.company
		initial['contact'] = self.request.user.pro.email
		initial['job_location'] = self.request.user.pro.headquarters
		initial['web_site'] = self.request.user.pro.web_site
		initial['activity_area'] = self.request.user.pro.activity_area
		initial['latitude'] = self.request.user.pro.latitude
		initial['longitude'] = self.request.user.pro.longitude
		initial['street_number'] = self.request.user.pro.street_number
		initial['route'] = self.request.user.pro.route
		initial['locality'] = self.request.user.pro.locality
		initial['administrative_area_level_2'] = self.request.user.pro.administrative_area_level_2
		initial['administrative_area_level_1'] = self.request.user.pro.administrative_area_level_1
		initial['country'] = self.request.user.pro.country
		return initial

	def form_valid(self, form):
		self.object = form.save( commit=False )
		self.object.pro = self.request.user.pro
		if form.cleaned_data.get('image') is None:
			self.object.image = self.request.user.pro.image
		self.object.save()
		return HttpResponseRedirect( reverse('pro:job-step-2', args=[self.object.id]) ) 


class JobStepOneUpdate(OnlyProLoginRequiredMixin, UpdateJobProMixin, UpdateView):
	model = Job
	fields = ['company', 'job_title', 'contact', 'job_location', 'web_site', 'activity_area', 'image', 'locality', 'administrative_area_level_2', 'administrative_area_level_1', 'country'] 
	template_name = 'pro/job-form-step-one.html'

	def get_success_url(self):
		return reverse('pro:job-step-2', args=[self.object.id])


class JobStepTwoUpdate(OnlyProLoginRequiredMixin, UpdateJobProMixin, UpdateView):
	model = Job
	form_class = JobStepTwoForm
	template_name = 'pro/job-form-step-two.html'

	def get_success_url(self):
		return reverse('pro:job-step-3', args=[self.object.id])

class JobStepTreeUpdate(OnlyProLoginRequiredMixin, UpdateJobProMixin, UpdateView):
	model = Job
	form_class = JobStepTreeForm
	template_name = 'pro/job-form-step-tree.html' 

	def get_initial(self):
		initial = super(JobStepTreeUpdate, self).get_initial()
		initial['tags_field'] = ",".join( self.object.tags.values_list('name', flat=True) ) 
		initial['video_url'] = self.request.user.pro.video_url
		return initial

	def form_valid(self, form):
		self.object  = form.save()
		self.object.tags.clear()
		if form.cleaned_data.get('tags_field'):
			for kw in form.cleaned_data.get('tags_field').split(','):
				try:
					kw_object, created = Tag.objects.get_or_create(name__iexact=kw, defaults={'name': kw})
					self.object.tags.add(kw_object)
				except: 
					kw_object = Tag.objects.filter(name__icontains=kw)
					if kw_object.exists():
						self.object.tags.add(kw_object.first())	
		self.object.save()
		return HttpResponseRedirect( reverse('pro:job-step-4', args=[self.object.id]) )  

class JobStepFourUpdate(OnlyProLoginRequiredMixin, UpdateJobProMixin, UpdateView):
	model = Job
	form_class = JobStepFourForm
	template_name = 'pro/job-form-step-four.html' 

	def get_context_data(self, **kwargs):
		context = super(JobStepFourUpdate, self).get_context_data(**kwargs)
		context['list_questions'] = self.object.questions.order_by('nb')
		return context

	def form_valid(self, form):
		self.object  = form.save()
		job_question = JobQuestion.objects.filter(job = self.object ).delete()
		for i, kw in enumerate(self.request.POST.getlist('qt'), start=1): 
			JobQuestion(question=kw, nb =i, job = self.object).save()
		return HttpResponseRedirect( reverse('pro:job-step-5', args=[self.object.id]) )  

class JobStepFiveUpdate(OnlyProLoginRequiredMixin, UpdateJobProMixin, UpdateView):
	model = Job
	fields = ['active']
	template_name = 'pro/job-form-step-five.html' 

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.complet == True and self.object.active == True and self.object.paid == True and self.object.is_valid():
			notification(2, None, self.request.user.pro, self.object)
			return HttpResponseRedirect( reverse('pro:offres') )  
		return super(JobStepFiveUpdate, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(JobStepFiveUpdate, self).get_context_data(**kwargs)

		job = self.get_object()
		if job.contracts.filter(id=3).exists() and job.contracts.count() == 1:
			context['stage'] = True
			price = 5880
		else:
			price = 11880

		if job.contracts.filter(id=9).exists() and job.contracts.count() == 1:
			context['stage'] = True
			price = 5880

		p = Paiement(price, 1, self.request.user.id, self.get_object().id, normal_return="http://www.pitchmyjob.com/pro/paiement-offre", cancel_return="http://www.pitchmyjob.com/pro/paiement-offre")
		code = p.call_request()
		context['pay'] = code[3]



		return context

	def form_valid(self, form):
		self.object  = form.save()
		#if self.request.user.pro.credit_job > 0 or (self.get_object().contracts.filter(id=3).exists() and self.get_object().contracts.count() == 1):
		if self.request.user.pro.credit_job > 0 :
			notification(3, None, self.request.user.pro, self.object)
			self.object.date_posted = datetime.datetime.now()
			self.object.complet = True
			self.object.active = True
			self.object.paid = True
			self.object.save()
			if self.request.user.pro.credit_job > 0:
				pro = self.request.user.pro
				pro.credit_job = pro.credit_job - 1
				pro.save()
		return HttpResponseRedirect( reverse('pro:offres') )  


class ProfilUpdate(OnlyProLoginRequiredMixin, UpdateView):
	model = Pro
	form_class = ProfilForm
	template_name = 'pro/profil.html'

	def get_object(self, queryset=None):
		return self.request.user.pro

	def form_valid(self, form):
		self.object  = form.save()
		job_question = JobQuestion.objects.filter(pro = self.object ).delete()
		for i, kw in enumerate(self.request.POST.getlist('qt'), start=1): 
			JobQuestion(question=kw, nb =i, pro = self.object).save()
		return HttpResponseRedirect( reverse('pro:profil') )  


class JobCandidaturesView(OnlyProLoginRequiredMixin, TokenMixin, DetailView):
	model = Job
	template_name = 'pro/list-candidature.html'

	def get_context_data(self, **kwargs):
		context = super(JobCandidaturesView, self).get_context_data(**kwargs)
		return context

	def get_object(self, queryset=None):
		job = get_object_or_404(Job, pk = self.kwargs.get(self.pk_url_kwarg, None), pro = self.request.user.pro )
		return job 

class JobReponseCandidatureView(OnlyProLoginRequiredMixin, DetailView):
	model = Candidature
	template_name = 'pro/list-reponse-candidature.html'

	def get_object(self, queryset=None):
		job = get_object_or_404(Job, pk = self.kwargs.get(self.slug_url_kwarg, None), pro = self.request.user.pro )
		candidature = get_object_or_404(Candidature, pk= self.kwargs.get(self.pk_url_kwarg, None), job = job )
		return candidature


class C2vThequeList(OnlyProLoginRequiredMixin, BaseSearchC2vThequeFormMixin, PaginationMixin, ListView):
	model = Member
	template_name = 'pro/c2vtheque.html'
	paginate_by = 25 

	def get_queryset(self):
		member = Member.objects.all()
		if self.request.method == 'GET' :
			if self.request.GET.get('sa') :
				member = member.filter(activity_area = self.request.GET.get('sa') )
			if self.request.GET.get('c') :
				member = member.filter(contracts = self.request.GET.get('c') )
			if self.request.GET.get('e') :
				member = member.filter(study = self.request.GET.get('e') )
			if self.request.GET.get('exp') :
				member = member.filter(experience__in = self.request.GET.getlist('exp') )
			if self.request.GET.get('d'):
				if self.request.GET.get('d') == "1":
					member = member.filter(availability__isnull = True ) 
				if self.request.GET.get('d') == "0":
					member = member.filter(availability__isnull = False )
			if self.request.GET.get('cn'):
				member = member.filter(last_visit__gte = datetime.datetime.now() - datetime.timedelta(days= int(self.request.GET.get('cn'))) )
			if self.request.GET.get('sd'):
				member = member.filter(salary__gte = self.request.GET.get('sd') )
			if self.request.GET.get('sf'):
				member = member.filter(salary__lte = self.request.GET.get('sf') )
			if self.request.GET.get('s'):
				member = member.filter( Q(cv__cvexperience__title__icontains = self.request.GET.get('s') ) | Q(cv__cvformation__degree__icontains = self.request.GET.get('s') ) | Q(cv__cvformation__school__icontains = self.request.GET.get('s') ) | Q(cv__poste__icontains = self.request.GET.get('s') ) | Q(last_name__icontains = self.request.GET.get('s') ) | Q(first_name__icontains = self.request.GET.get('s') ) | Q(job_wanted__icontains = self.request.GET.get('s') ) | Q(cv__cvskill__name__icontains = self.request.GET.get('s') ) |  Q(cv__description__icontains = self.request.GET.get('s') ) ).distinct()
			if self.request.GET.get('p') :
				if self.request.GET.get('la') :
					member = member.filter(locality = self.request.GET.get('la') )
				if self.request.GET.get('a2') :
					member = member.filter(administrative_area_level_2 = self.request.GET.get('a2') )
				if self.request.GET.get('a1') :
					member = member.filter(administrative_area_level_1 = self.request.GET.get('a1') )
				if self.request.GET.get('ct') :
					member = member.filter(country = self.request.GET.get('ct') ) 
		return member.order_by('-user__date_joined')

class C2vThequeDetail(OnlyProLoginRequiredMixin, DetailView):
	model = Member
	template_name = 'pro/c2vtheque-candidat.html'

	def get_context_data(self, **kwargs):
		member = self.get_object()
		notification(7, member, self.request.user.pro)
		context=super(C2vThequeDetail, self).get_context_data(**kwargs)
		context['next']=Member.objects.all().first()
		context['prev']=Member.objects.all().last()
		next = Member.objects.filter(id__gt=self.get_object().id)
		if next:
			context['next']=next.first()
		prev = Member.objects.filter(id__lt=self.get_object().id).order_by('-id')
		if prev:
			context['prev']=prev.first()
		return context


class MessagesTemplateView(OnlyProLoginRequiredMixin, TemplateView):
	template_name = 'pro/messages.html'

	def get_context_data(self, **kwargs):
		context = super(MessagesTemplateView, self).get_context_data(**kwargs)
		message = Message.objects.filter( Q(sender=self.request.user) | Q(receiver=self.request.user) )
		if message.exists():
			message = message.first()
			context['receiver'] = message.receiver.member if message.group == 2 else message.sender.member
		else :
			context['receiver'] = None
		return context


class MessageTemplateView(OnlyProLoginRequiredMixin, TemplateView):
	template_name = 'pro/messages.html'

	def get_context_data(self, **kwargs):
		context = super(MessageTemplateView, self).get_context_data(**kwargs)
		member = get_object_or_404(Member, id=self.kwargs['pk']) 
		if Message.objects.filter( Q(sender=self.request.user, receiver=member.user) | Q(receiver=self.request.user, sender=member.user) ).exists() is False:
			raise Http404
		context['receiver'] = member
		return context

class FactureListView(OnlyProLoginRequiredMixin, ListView):
	model = Facture
	template_name = 'pro/factures.html'

	def get_queryset(self):
		return self.request.user.facture_set.all()
