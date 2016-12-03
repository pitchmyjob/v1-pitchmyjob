# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView, BaseUpdateView
from django.views.generic import ListView, DetailView, FormView
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from members.forms import OldInscriptionForm, ApplyForm, ApplyFormCv, InscriptionForm, InscriptionStepTwoForm, LoginForm, BaseSearchFormMixin, CandidatureStepThreeForm, ReponseForm, MyAccountForm, ChangePasswordForm, FbConnectPasswordForm, CandidatureStepTwoForm
from myc2v.mixins import OnlyMemberLoginRequiredMixin, UpdateMemberMixin, TokenMixin
from .models import Member, Candidature, CandidatureReponse, Interest, Tips
from pro.models import Job, Tag, SearchJob, SeenJob
from notifications.models import Message
from django.conf import settings
from c2v.models import Cv, CvSkill
from pro.models import Pro, ActivityArea
from django.db.models import Q, Count
from django.core.mail import send_mail
from django.contrib import messages
from notifications.notifications import async_send_email, notification, async_send_email_attach
import subprocess, datetime
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from pure_pagination.mixins import PaginationMixin
from myc2v import tools
from c2v.views import generate_pdf

def home(request):
	return HttpResponse("site en maintenance, on revient dans 10 min ;)")
	#async_send_email.delay("test sujet", ["tannier.yannis@gmail.com"], "emails/test.html", {} )
	context = {"ecole" : ecole, "jobs" : Job.objects.filter(active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by("-date_created")[:7], "alljobs" : Job.objects.filter(active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB) )[:20]}
	return render(request, 'home-member.html', context)

def logout_view(request):
    logout(request)
    return HttpResponseRedirect( "/" )


def login_view_refonte(request):
	form = LoginForm(request.POST or None)
	if form.is_valid():
		user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
		if user is not None and user.is_active == True:
			if user.groups.filter(name='member').exists():
				login(request, user)
				if request.GET.get('next'):
					return HttpResponseRedirect(request.GET.get('next', '/'))
				else:
					return HttpResponseRedirect(reverse('members:list-job'))
			else:
				login(request, user)
				if request.GET.get('next') :
					return HttpResponseRedirect( request.GET.get('next', '/') )
				else :
					return HttpResponseRedirect( reverse('pro:offres')  )
				#form.add_error(None, 'Veuillez vous connecter avec un compte Membre.')
		else:
			form.add_error(None, _(u'L\'email et le mot de passe ne correspondent pas.'))

	context = {"form":form }
	return render(request, 'members/login-refonte.html', context)

def login_view(request):
	form = LoginForm(request.POST or None)
	if form.is_valid():
		user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
		if user is not None and user.is_active == True:
			if user.groups.filter(name='member').exists():
				login(request, user)
				return HttpResponseRedirect( request.GET.get('next', '/') )
			else:
				login(request, user)
				if request.GET.get('next') :
					return HttpResponseRedirect( request.GET.get('next', '/') )
				else :
					return HttpResponseRedirect( reverse('pro:offres')  )
				#form.add_error(None, 'Veuillez vous connecter avec un compte Membre.')
		else:
			form.add_error(None, _(u'L\'email et le mot de passe ne correspondent pas.'))

	context = {"form":form }
	return render(request, 'members/login.html', context)

def invitation(request):
	return HttpResponseRedirect( reverse('members:home') )

@login_required()
def disable_account(request):
	if not request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect( reverse('members:login') )

	request.user.is_active=False
	request.user.save()
	logout(request)
	return HttpResponseRedirect( "/" )

class HomeInscriptionCreate(CreateView):
	model = Member
	form_class = InscriptionForm
	template_name = 'home-member-2.html'

	def get_context_data(self, **kwargs):
		context = super(HomeInscriptionCreate, self).get_context_data(**kwargs)
		if self.request.GET.get('e'):
			self.request.session['ecole'] = self.request.GET.get('e')
		return context

	def form_valid(self, form):
		self.object = form.save(commit=False)
		user = User.objects.create_user(self.object.email, self.object.email, form.cleaned_data.get('mdp'))
		user.groups.add(Group.objects.get(name='member'))
		user.save()
		self.object.user = user
		self.object.save()
		cv = Cv(member=self.object, email=self.object.email, first_name=self.object.first_name,
				last_name=self.object.last_name).save()

		if 'ecole' in self.request.session:
			self.object.school = self.request.session['ecole']
			self.object.save()

		login(self.request, authenticate(username=self.object.email, password=form.cleaned_data.get('mdp')))
		if self.request.GET.get('next'):
			self.request.session['redirect_inscription'] = self.request.GET.get('next')
		return HttpResponseRedirect(reverse('members:inscription-step-2'))

class InscriptionCreate(CreateView): #class a delete
	model = Member
	form_class = OldInscriptionForm
	template_name = 'members/inscription.html'

	def get(self, request, *args, **kwargs):
		#if 'code' not in request.session :
			#return HttpResponseRedirect( reverse('members:invitation') )
		return super(InscriptionCreate, self).get(request, *args, **kwargs)

	def form_valid(self, form):
		self.object  = form.save( commit=False )
		user = User.objects.create_user(self.object.email, self.object.email, form.cleaned_data.get('password'))
		user.groups.add( Group.objects.get(name='member')  )
		user.save()
		self.object.user = user
		self.object.save()
		cv = Cv(phone=self.object.phone, member = self.object, email = self.object.email, first_name = self.object.first_name, last_name = self.object.last_name, birthday=self.object.birthday  ).save()
		login(self.request, authenticate(username=self.object.email, password=form.cleaned_data.get('password')))
		if self.request.GET.get('next') :
			self.request.session['redirect_inscription'] = self.request.GET.get('next')
		return HttpResponseRedirect( reverse('members:inscription-step-2') )

class InscriptionStepTwoUpdate(OnlyMemberLoginRequiredMixin, UpdateView): 
	model = Member
	form_class = InscriptionStepTwoForm
	template_name = 'members/inscription-step-two.html'

	def get_initial(self):
		initial = super(InscriptionStepTwoUpdate, self).get_initial()
		if self.object.tags.count() > 0:
			initial['tags_field'] = ",".join( self.object.tags.values_list('name', flat=True) )
		else:
			tags = CvSkill.objects.filter(cv=self.request.user.member.cv)
			if tags.exists():
				initial['tags_field'] = ",".join(tags.values_list('name', flat=True))
		return initial

	def get_object(self, queryset=None):
		return self.request.user.member

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
		self.object.save_on_elasticsearch()

		return tools.redirect(self.request)

class JobListEntreprise(BaseSearchFormMixin, ListView):
	model = Job
	template_name = 'members/list-job.html'

	def get_context_data(self, **kwargs):
		context = super(JobListEntreprise, self).get_context_data(**kwargs)
		context['list_pro'] = Pro.objects.filter(job__active=True).order_by("job__date_created")[:4]
		context['cano'] = True
		return context

	def get_queryset(self):
			return Job.objects.filter(active=True, paid=True, date_posted__gte=timezone.now().date() - datetime.timedelta(days=settings.DAYS_JOB) ).filter(pro =  self.kwargs.get('pk'))

class JobList(BaseSearchFormMixin, PaginationMixin, ListView):
	model = Job
	template_name = 'members/list-job.html'
	paginate_by = 20

	def get_context_data(self, **kwargs):
		context = super(JobList, self).get_context_data(**kwargs)
		context['list_pro'] = Pro.objects.filter(job__active=True).distinct()[:4]
		context['count'] = self.get_queryset().count()
		context['search'] = self.search

		if self.search: 
			if self.request.GET.get('search').strip():
				if self.request.user.is_authenticated() and self.request.user.groups.filter(name='member').exists():
					search=self.request.GET.get('search').strip()
					SearchJob.objects.create(member=self.request.user.member, search=search.lower())
				else:
					search=self.request.GET.get('search').strip()
					SearchJob.objects.create(search=search.lower())

		if self.request.GET:
			self.request.session['redirect_back']=self.request.GET.urlencode()
		else:
			self.request.session['redirect_back']=None

		return context

	def get_queryset(self):
		self.search=False

		if self.request.method == 'GET':
			job = Job.objects.all()
			if self.request.GET.get('activity_area') :
				if int(self.request.GET.get('activity_area')) != 40:
					job = job.filter(activity_area_id = self.request.GET.get('activity_area') )
					self.search=True
			if self.request.GET.get('contracts') :
				job = job.filter(contracts__in = self.request.GET.getlist('contracts') )
				self.search=True
			if self.request.GET.get('experiences') :
				job = job.filter(experiences__in = self.request.GET.getlist('experiences') )
				self.search=True		
			if self.request.GET.get('contract_time') :
				job = job.filter(contract_time__in = self.request.GET.getlist('contract_time') )
				self.search=True
			if self.request.GET.get('study') :
				job = job.filter(studies = self.request.GET.get('study') )
				self.search=True
			if self.request.GET.get('place') :
				if self.request.GET.get('locality') :
					job = job.filter(locality = self.request.GET.get('locality') )
				if self.request.GET.get('administrative_area_level_2') :
					job = job.filter(administrative_area_level_2 = self.request.GET.get('administrative_area_level_2') )
				if self.request.GET.get('administrative_area_level_1') :
					job = job.filter(administrative_area_level_1 = self.request.GET.get('administrative_area_level_1') )
				if self.request.GET.get('country') :
					job = job.filter(country = self.request.GET.get('country') )
				self.search=True
			if self.request.GET.get('search'):
				self.search=True
				job = job.filter( Q(mission__icontains = self.request.GET.get('search')) | Q(job_title__icontains = self.request.GET.get('search')) | Q(company__icontains = self.request.GET.get('search')) | Q(tags__name__icontains = self.request.GET.get('search')) | Q(description__icontains = self.request.GET.get('search'))  ).distinct()

			if self.search:
				return job.filter(active=True, paid=True, date_posted__gte=timezone.now().date() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by('scraper', '-date_posted')
			else:
				return job.filter(active=True, paid=True, date_posted__gte=timezone.now().date() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by('-date_posted')
		else:
			return Job.objects.filter(active=True, paid=True, date_posted__gte=timezone.now().date() - datetime.timedelta(days=settings.DAYS_JOB) ).order_by('-date_posted')

class JobDetail(DetailView):
	model = Job
	template_name = 'members/detail-job.html'

	def get(self, request, *args, **kwargs):
		if not self.get_object():
			return HttpResponseRedirect( reverse('members:list-job') )
		job = self.get_object()
		job.view = job.view + 1
		job.save()

		if self.request.user.is_authenticated() and self.request.user.groups.filter(name='member').exists():
			SeenJob.objects.create(member=self.request.user.member, job=job)

		return super(JobDetail, self).get(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(JobDetail, self).get_context_data(**kwargs)
		context['rdm'] = [1,2,3]
		if self.request.user.is_authenticated() and self.request.user.groups.filter(name='member').exists():
			context['interest'] = Interest.objects.filter(job=self.object, member=self.request.user.member).exists()
			context['candidate'] = Candidature.objects.filter( job = self.get_object(), member = self.request.user.member, active = True ).exists()

		if "redirect_back" in self.request.session:
			try:
				context['redirect_back']=self.request.session['redirect_back']
				del self.request.session['redirect_back']
			except:
				context['redirect_back']=None
		else:
			context['redirect_back']=None
		return context

	def get_object(self, queryset=None):
		job = Job.objects.filter(pk=self.kwargs.get(self.pk_url_kwarg, None), active=True, paid=True, date_posted__gte=timezone.now().date() - datetime.timedelta(days=settings.DAYS_JOB) )
		if not job.exists():
			return None
		return job.first()

	def create_candidature(self, request):
		candidature, created = Candidature.objects.get_or_create(job=self.get_object(), member=request.user.member)

		if created:
			candidature.mode = 1
			candidature.save()
			for qt in self.get_object().questions.all():
				rp = CandidatureReponse(candidature=candidature, nb=qt.nb)
				rp.save()

		return candidature

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if request.POST.get('interest'):
			if self.request.user.is_authenticated() and self.request.user.groups.filter(name='member').exists():
				if not Interest.objects.filter(job=self.object, member=request.user.member).exists():
					Interest.objects.create(job=self.object, member=request.user.member)
					msg = u'L\'entreprise %s a été mis au courant de l\'intérêt porter à cette offre. Nous t\'invitons à passer l\'entretien afin de prouver ta motivation.' % self.object.company
					messages.add_message(self.request, messages.INFO, _(msg))
					ctx={
						"job":self.object.job_title,
						"member": self.object.pro.first_name,
						"id":self.object.id
					}
					async_send_email("Nouveau candidat interessé par votre offre", [self.object.pro.email], "emails/email_interet.html", ctx)
			else:
				#return HttpResponseRedirect(reverse('members:login'))
				messages.add_message(self.request, messages.INFO, _(u'Connexion requise.'))

		if request.POST.get('goEntretien'):
			candidature = self.create_candidature(request)

			if request.FILES.get('cv'):
				candidature.cv = request.FILES.get('cv')
				candidature.save()
				request.user.member.cv_pdf = candidature.cv
				request.user.member.save()
			else:
				if not request.POST.get('my_cv'):
					candidature.cv = request.user.member.cv_pdf
					candidature.save()

			ctx = {
				"job": self.object.job_title,
				"member": self.object.pro.first_name,
				"id": self.object.id
			}
			async_send_email("Nouveau candidat interessé par votre offre", [self.object.pro.email], "emails/email_interet.html", ctx)

			return HttpResponseRedirect(reverse('members:candidature-1', args=[self.object.id]))

		if request.POST.get('apply'):
			form = ApplyForm(request.POST, request.FILES)
			if form.is_valid():
				user = User.objects.create_user(form.cleaned_data.get('email'), form.cleaned_data.get('email'),
												form.cleaned_data.get('mdp'))
				user.groups.add(Group.objects.get(name='member'))
				user.save()

				member = Member(user=user, first_name=form.cleaned_data.get('first_name'),
								last_name=form.cleaned_data.get('last_name'), email=form.cleaned_data.get('email'))
				member.save()
				member.image = form.cleaned_data.get('photo')
				member.cv_pdf = form.cleaned_data.get('cv')
				member.save()
				cv = Cv(member=member, email=member.email, first_name=member.first_name,
						last_name=member.last_name).save()

				login(self.request, authenticate(username=user.email, password=form.cleaned_data.get('mdp')))

				candidature = self.create_candidature(request)
				candidature.cv = member.cv_pdf
				candidature.save()

				return HttpResponseRedirect(reverse('members:candidature-1', args=[self.object.id]))



		return HttpResponseRedirect(reverse('members:detail-job', args=[self.object.id]))

class ProList(BaseSearchFormMixin, PaginationMixin, ListView):
	model = Pro
	template_name = 'members/list-pro.html'
	paginate_by = 12

	def get_queryset(self):
		if self.request.method == 'GET' :
			pro = Pro.objects.all()
			if self.request.GET.get('activity_area') :
				pro = pro.filter(activity_area_id = self.request.GET.get('activity_area') )
			if self.request.GET.get('place') :
				if self.request.GET.get('locality') :
					pro = pro.filter(locality = self.request.GET.get('locality') )
				if self.request.GET.get('administrative_area_level_2') :
					pro = pro.filter(administrative_area_level_2 = self.request.GET.get('administrative_area_level_2') )
				if self.request.GET.get('administrative_area_level_1') :
					pro = pro.filter(administrative_area_level_1 = self.request.GET.get('administrative_area_level_1') )
				if self.request.GET.get('country') :
					pro = pro.filter(country = self.request.GET.get('country') )
			if self.request.GET.get('search') :
				pro = pro.filter( company__icontains = self.request.GET.get('search')  )
			return sorted(pro.filter(scraper=False), key=lambda p: p.count_job(), reverse=True)
		else:
			return sorted(pro.filter(scraper=False), key=lambda p: p.count_job(), reverse=True)

class ProDetail(DetailView):
	model = Pro
	template_name = 'members/detail-pro.html'

	def get_context_data(self, **kwargs):
		context = super(ProDetail, self).get_context_data(**kwargs)
		pro = Pro.objects.get(id=self.kwargs.get(self.pk_url_kwarg, None))
		pro.view = pro.view + 1
		pro.save()
		context['jobs'] = pro.job_set.filter(active=True, paid=True, date_posted__gte=timezone.now().date() - datetime.timedelta(days=settings.DAYS_JOB) )
		return context

@login_required()
def refonte_candidature(request, pk):
	if not request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect(reverse('members:login'))

	job = get_object_or_404(Job, pk=pk)
	candidature = get_object_or_404(Candidature, job = job, member = request.user.member)
	tips = Tips.objects.order_by('?')

	if not Interest.objects.filter(job=job, member=request.user.member).exists():
		Interest.objects.create(job=job, member=request.user.member)

	if request.is_mobile :
		return render(request, 'members/candidature-mobile.html', {"questions" : job.questions.all(), "candidature" : candidature})
	else:
		return render(request, 'members/candidature.html', {"questions": job.questions.all(), "candidature": candidature, 'tips': tips})



class CandidatureStepOne(OnlyMemberLoginRequiredMixin, DetailView):
	model = Job
	template_name = 'members/candidature-1.html'

	def get_context_data(self, **kwargs):
		context = super(CandidatureStepOne, self).get_context_data(**kwargs)
		context['candidate'] = Candidature.objects.filter( job = self.get_object(), member = self.request.user.member, active = True ).exists()
		return context

@login_required()
def CandidatureStepTwo(request, pk):
	if not request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect( reverse('members:login') )

	job = get_object_or_404(Job, pk=pk)
	
	form = CandidatureStepTwoForm()

	#if candidature.active == True:
		#return HttpResponseRedirect( reverse('members:detail-candidature', args=[job.id]) )

	if request.method == "POST" :
		try:
			candidature, created = Candidature.objects.get_or_create(job=job, member=request.user.member)
		except: 
			candidature = Candidature.objects.filter(job=job, member=request.user.member)
			if candidature.exists():
				candidature = candidature.first()
	
		candidature.cv = None
		form = CandidatureStepTwoForm(request.POST, request.FILES, instance=candidature)
		if form.is_valid(): 
			form.save()
		else:
			return render(request, 'members/candidature-2.html', {'object' : job, 'form' : form})

		if not candidature.cv :
			exp = request.user.member.cv.cvexperience_set.count()
			frm = request.user.member.cv.cvformation_set.count()
			if exp < 1 or frm < 1 :
				form.add_error(None, 'Veuillez remplir un minimmum c2v.')
				return render(request, 'members/candidature-2.html', {'object' : job, 'form' : form})
		#if not created:
			#return HttpResponseRedirect( reverse('members:candidature-3', args=[job.id, candidature.id]) )

		cr = CandidatureReponse.objects.filter( candidature = candidature )	
		if cr.exists():
			cr.delete()

		for qt in job.questions.all():
			rp = CandidatureReponse( candidature = candidature, nb = qt.nb ) 
			rp.save()

		return HttpResponseRedirect( reverse('members:candidature-3', args=[job.id, candidature.id]) )

	return render(request, 'members/candidature-2.html', {'object' : job, 'form' : form})


@login_required()
def CandidatureStepThree(request, job, cd):
	if not request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect( reverse('members:login') )

	candidature = get_object_or_404(Candidature, job = job, pk = cd, member = request.user.member)

	col = 0
	if candidature.job.is_video:
		col = col + 1
	if candidature.job.is_audio:
		col = col + 1
	if candidature.job.is_text:
		col = col + 1

	if col == 1:
		col = 12
	if col == 2:
		col = 6
	if col == 3:
		col = 4	


	if candidature.active == True:
		return HttpResponseRedirect( reverse('members:detail-candidature', args=[candidature.job.id]) )

	form = CandidatureStepThreeForm(instance=candidature)

	if request.method =='POST':
		form = CandidatureStepThreeForm(request.POST, instance=candidature)
		if form.is_valid():
			candidature.member = request.user.member
			candidature.job = get_object_or_404(Job, pk = job)
			candidature.mode = form.cleaned_data['mode']
			candidature.save()
			qt = CandidatureReponse.objects.get(candidature = candidature, nb = 1)
			if candidature.mode == 1 or candidature.mode == 2:
				return HttpResponseRedirect( reverse('members:candidature-4-video', args=[job, candidature.id] ) )
			else:
				return HttpResponseRedirect( reverse('members:candidature-4', args=[job, candidature.id, qt.nb] ) )

	return render(request, 'members/candidature-3.html', {'form' : form, 'object' : candidature.job, 'col':col })

@login_required()
def CandidatureStepFour(request, job, cd, nb):
	if not request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect( reverse('members:login') )
	form = None
	candidature = get_object_or_404(Candidature, pk = cd, member = request.user.member )

	if candidature.active == True:
		return HttpResponseRedirect( reverse('members:detail-candidature', args=[candidature.job.id]) )

	qt = get_object_or_404(CandidatureReponse, nb = nb, candidature = candidature )

	questions = candidature.job.questions.all()
	question = candidature.job.questions.filter(nb = nb).first()
	back = reverse('members:candidature-3', args=[job, cd]) if int(nb) == 1 else reverse('members:candidature-4', args=[job, cd, int(nb)-1])
	next = reverse('members:candidature-5', args=[job, cd]) if int(nb) == questions.count() else reverse('members:candidature-4', args=[job, cd, int(nb)+1])
	
	if candidature.mode == 3 :
		form = ReponseForm(request.POST or None, instance = qt)
		if form.is_valid():
			qt.text = form.cleaned_data['text']
			qt.save()
			return HttpResponseRedirect( next )
	if candidature.mode == 1 or candidature.mode == 2 :
		obj, created = Token.objects.get_or_create(user = request.user)
		form = obj

	return render(request, 'members/candidature-4.html', {'form' : form, 'question' : question ,'questions' : questions, 'nb' : int(nb), 'candidature': candidature, 'back' : back, 'next' :next, 'reponse' : qt })

@login_required()
def CandidatureStepFourVideo(request, job, cd):
	if not request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect( reverse('members:login') )
	form = None
	candidature = get_object_or_404(Candidature, pk = cd, member = request.user.member )

	if candidature.active == True:
		return HttpResponseRedirect( reverse('members:detail-candidature', args=[candidature.job.id]) )

	back = reverse('members:candidature-3', args=[job, cd])
	next = reverse('members:candidature-5', args=[job, cd])

	questions = candidature.job.questions.all()

	obj, created = Token.objects.get_or_create(user = request.user)
	form = obj
	if candidature.mode == 1:
		return render(request, 'members/candidature-4-video.html', {'form' : form, 'questions' : questions,  'candidature': candidature, 'back' : back, 'next' : next })
	if candidature.mode == 2:
		return render(request, 'members/candidature-4-audio.html', {'form' : form, 'questions' : questions,  'candidature': candidature, 'back' : back, 'next' : next })

@login_required()
def CandidatureStepFive(request, job, cd):
	if not request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect( reverse('members:login') )

	candidature = get_object_or_404(Candidature, pk = cd, member = request.user.member, job = job )
	
	if candidature.active is False:
		notification(1, request.user.member, None, candidature.job)
		notification(5, request.user.member, None, candidature.job)

		if candidature.job.mp:
			ctx = {"questions": candidature.job.questions.all(), "link": candidature.video.path_aws()}
			text = "%s %s %s" % ( candidature.member.first_name, candidature.member.last_name, candidature.member.email )
			async_send_email_attach(text, [candidature.job.mp_email], "emails/application_email.html",ctx, {"name": "cv.pdf", "file": generate_pdf('c2v/themes/pdf-theme-1.html',{'pagesize': 'A4','cv': request.user.member.cv}),"type": "application/pdf"})

	candidature.active=True
	candidature.save() 

	return render(request, 'members/candidature-5.html', {'candidature' : candidature})


class CandidatureDetail(OnlyMemberLoginRequiredMixin, DetailView):
	model = Candidature
	template_name = 'members/ma-candidature.html'

	def get_object(self, queryset=None):
		return get_object_or_404(Candidature, job= self.kwargs.get(self.pk_url_kwarg, None), member = self.request.user.member)


class MyCandidatureJob(OnlyMemberLoginRequiredMixin, ListView):
	model = Candidature
	template_name = 'members/mes-candidatures-offre.html'

	def get_queryset(self):
		return self.request.user.member.candidature_set.filter(active=True)

class MyCandidatureInterestJob(OnlyMemberLoginRequiredMixin, ListView):
	model = Candidature
	template_name = 'members/mes-candidatures-offre-interet.html'

	def get_queryset(self):
		return self.request.user.member.interest_set.all()


class MyAccountUpdate(OnlyMemberLoginRequiredMixin, UpdateMemberMixin, UpdateView): 
	model = Member
	fields = ['first_name', 'last_name', 'birthday']
	template_name = 'members/my-account.html'

	def get_success_url(self):
		return reverse('members:my-account')

class MyAccountInformationUpdate(OnlyMemberLoginRequiredMixin, UpdateMemberMixin, UpdateView): 
	model = Member
	form_class = InscriptionStepTwoForm
	template_name = 'members/my-account-information.html'

	def get_initial(self):
		initial = super(MyAccountInformationUpdate, self).get_initial()
		initial['tags_field'] = ",".join( self.object.tags.values_list('name', flat=True) )
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

		return HttpResponseRedirect( reverse('members:my-account-information') )

class MyAccountPasswordUpdate(OnlyMemberLoginRequiredMixin, FormView): 
	form_class = ChangePasswordForm
	template_name = 'members/my-account-password.html'

	def get_form_kwargs(self):
		kwargs = super(MyAccountPasswordUpdate, self).get_form_kwargs()
		kwargs.update({'user': self.request.user})
		return kwargs

	def form_valid(self, form):
		self.request.user.set_password( form.cleaned_data.get('password') )
		self.request.user.save()
		messages.add_message(self.request, messages.INFO, _(u'Votre mot de passe a bien été modifié.'))
		return HttpResponseRedirect( reverse('members:my-account-password') )


class FbConnectPassword(OnlyMemberLoginRequiredMixin, UpdateView): 
	form_class = FbConnectPasswordForm
	model = Member
	template_name = 'members/fbconnect-password.html'

	def get_object(self, queryset=None):
		if self.request.user.member.rs_pwd:
			return self.request.user.member
		raise Http404

	def form_valid(self, form):
		user = self.request.user
		user.set_password(form.cleaned_data.get('password'))
		user.member.rs_pwd = False
		user.member.save()
		user.save()
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(self.request, user)
		self.request.session['code'] = "code"
		return HttpResponseRedirect( reverse('members:inscription-step-2') )


class MessagesTemplateView(OnlyMemberLoginRequiredMixin, TemplateView):
	template_name = 'members/messages.html'

	def get_context_data(self, **kwargs):
		context = super(MessagesTemplateView, self).get_context_data(**kwargs)
		message = Message.objects.filter( Q(sender=self.request.user) | Q(receiver=self.request.user) )
		if message.exists():
			message = message.first()
			context['receiver'] = message.sender.pro if message.group == 2 else message.receiver.pro
		else :
			context['receiver'] = None
		return context

class MessageTemplateView(OnlyMemberLoginRequiredMixin, TemplateView):
	template_name = 'members/messages.html'

	def get_context_data(self, **kwargs):
		context = super(MessageTemplateView, self).get_context_data(**kwargs)
		pro = get_object_or_404(Pro, id=self.kwargs['pk']) 
		if self.request.user.message_received.filter(sender=pro.user).exists() is False:
			raise Http404
		context['receiver'] = pro
		return context

class SuggestedJobList(OnlyMemberLoginRequiredMixin, PaginationMixin, ListView):
	model = Job
	template_name = 'members/list-job-suggested.html'
	paginate_by = 5

	def get_queryset(self):
		member = self.request.user.member
		tags = member.tags.values_list('name', flat=True)
		job = Job.objects.filter(active=True, paid=True, date_posted__gte=timezone.now() - datetime.timedelta(days=settings.DAYS_JOB) )

		if len(tags) > 0:
			job_search=Q(job_title__icontains=tags[0])
			for tag in tags:
				job_search = job_search | Q(job_title__icontains=tag)

			job = job.filter(job_search)

		if member.locality :
			job = job.filter(locality = member.locality)
		if member.administrative_area_level_2:
			job = job.filter(administrative_area_level_2 = member.administrative_area_level_2 )
		if member.administrative_area_level_1 :
			job = job.filter(administrative_area_level_1 = member.administrative_area_level_1 )
		if member.country :
			job = job.filter(country = member.country )

		if member.contracts:
			contrats=member.contracts.values_list('id', flat=True)
			job = job.filter(contracts__in = contrats )

		return job.order_by('?')

def test(request):
	from socketIO_client import SocketIO

	with SocketIO("http://myc2v.com", 8080) as socketIO:
		socketIO.emit("api_msg", { 'token' : "e4402119da7e1b67fbd3c5352b7afaba3508f529"})

	return HttpResponse( "ok" )