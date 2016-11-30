# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from doyoubuzz import DoYouBuzz
from django.contrib.auth.models import User, Group
from c2v.models import Cv
from members.models import Member
from django.contrib.auth import authenticate, login, logout
from members.forms import FbConnectPasswordForm
from myc2v.mixins import OnlyMemberLoginRequiredMixin
from django.views.generic.edit import UpdateView
from myc2v import tools
from rauth.service import OAuth2Service
import json, requests
from notifications.notifications import async_linkedin_cv
from linkedin import Linkedin
from facebook import Facebook
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

class SnConnectPassword(OnlyMemberLoginRequiredMixin, UpdateView): 
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


def doyoubuzz_connect(request):
	if request.GET.get('next') :
		request.session['redirect_inscription'] = request.GET.get('next')

	doyoubuzz = DoYouBuzz('sn/doyoubuzz-return')
	doyoubuzz=doyoubuzz.get_request_token()

	request.session['token']=doyoubuzz.token
	request.session['token_secret']=doyoubuzz.token_secret

	return doyoubuzz.get_user_authorization()


def doyoubuzz_return(request):
	if 'token_secret' not in request.session or not request.GET.get('oauth_token') or not request.GET.get('oauth_verifier'):
		return HttpResponseRedirect( "/" )  

	doyoubuzz = DoYouBuzz()

	token_secret = request.session.get('token_secret')
	oauth_token = request.GET.get('oauth_token')
	oauth_verifier = request.GET.get('oauth_verifier')
	token = doyoubuzz.get_access_token(oauth_token, oauth_verifier, token_secret)

	if not token:
		return HttpResponseRedirect( "/" ) 

	result=doyoubuzz.request('http://api.doyoubuzz.com/user', {'format' : 'json'} )

	user = User.objects.filter(username = result['user']['email'])
	if user.exists():
		user = user.first()
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		return tools.redirect(request, 2)

	password="00000"
	user = User.objects.create_user(result['user']['email'], result['user']['email'], password)
	user.backend = 'django.contrib.auth.backends.ModelBackend'

	member = Member(email=result['user']['email'], first_name=result['user']['firstname'], last_name=result['user']['lastname'], user = user, rs_pwd = True, rs_type=2)
	member.save()

	if 'ecole' in request.session:
		member.school = request.session['ecole']
		member.save()

	g = Group.objects.get(name='member') 
	g.user_set.add(user)
	g.save()

	cv = Cv( member = member, email = member.email, first_name = member.first_name, last_name = member.last_name  )
	cv.save()

	doyoubuzz.import_data(result, member, cv)
	login(request, user)

	return HttpResponseRedirect( reverse('members:sn-password') )


def linkedin_connect(request):
	if request.GET.get('next') :
		request.session['redirect_inscription'] = request.GET.get('next')

	linkedin = Linkedin()
	return HttpResponseRedirect( linkedin.get_url() )


def linkedin_return(request):
	if not request.GET.get('code'):
		return HttpResponseRedirect( "/" )

	linkedin = Linkedin()
	res = linkedin.get_user_data(request.GET.get('code'))

	if not res:
		return HttpResponseRedirect( "/" )

	if 'emailAddress' not in res:
		messages.add_message(request, messages.INFO, _(u'Aucun email ne semble être rattaché à votre compte Linkedin. Vous ne pouvez pas vous inscrire avec votre compte Linkedin sur Pitch my job.'))
		return HttpResponseRedirect( "/inscription" )
		
	email=res['emailAddress']
	user = User.objects.filter(username = email)
	if user.exists():
		user = user.first()
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		async_linkedin_cv(user.member.id, res['publicProfileUrl'])
		return tools.redirect(request, 2)


	user = User.objects.create_user(email, email, "cvG456hz")
	user.backend = 'django.contrib.auth.backends.ModelBackend'

	member = Member(email = email, first_name = res['firstName'], last_name = res['lastName'], user = user, rs_pwd = True,  rs_type=1)
	member.save()
	cv = Cv( member = member, email = member.email, first_name = member.first_name, last_name = member.last_name  ).save()
	
	if 'publicProfileUrl' in res:
		try:
			cv.site = res['publicProfileUrl']
			cv.save()
		except Exception:
			pass

	if 'ecole' in request.session:
		member.school = request.session['ecole']
		member.save()

	if 'publicProfileUrl' in res:
		payload = {
			"url" : res['publicProfileUrl'],
			"id" : member.id
		}
		requests.post("http://163.172.28.221:1234/", data=payload, headers={"Content-Type" : "application/json"})
		#async_linkedin_cv(member.id, res['publicProfileUrl'])

	g = Group.objects.get(name='member') 
	g.user_set.add(user)
	g.save()
	
	member.save_on_elasticsearch()

	login(request, user)
	return HttpResponseRedirect( reverse('members:inscription-step-2') )


def facebook_connect(request):
	if request.GET.get('next') :
		request.session['redirect_inscription'] = request.GET.get('next')

	fb = Facebook()
	return HttpResponseRedirect( fb.get_url() )


def facebook_return(request):
	if not request.GET.get('code'):
		return HttpResponseRedirect( "/" )

	fb = Facebook()
	res = fb.get_user_data(request.GET.get('code')) 

	if not res:
		return HttpResponseRedirect( "/" )

	if 'email' not in res:
		messages.add_message(request, messages.INFO, _(u'Aucun email n\'est rattaché à votre compte Facebook. De ce fait, vous ne pouvez pas vous inscrire avec votre compte Facebook sur Pitch my job.'))
		return HttpResponseRedirect( "/login" )

	user = User.objects.filter(username = res['email'])
	if user.exists():
		user = user.first()
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		return tools.redirect(request, 2)

	user = User.objects.create_user(res['email'], res['email'], "00000000")
	user.backend = 'django.contrib.auth.backends.ModelBackend'

	member = Member(email = res['email'], first_name = res['first_name'], last_name = res['last_name'], user = user, rs_pwd = True, rs_type=3)
	member.save()
	cv = Cv( member = member, email = member.email, first_name = member.first_name, last_name = member.last_name  ).save()
	g = Group.objects.get(name='member') 
	g.user_set.add(user)
	g.save()

	if 'picture' in res:
		fb.save_picture(member, res['picture']['data']['url'])

	login(request, user)
	return HttpResponseRedirect( reverse('members:sn-password') )


def viadeo_connect(request):
	from viadeo import Viadeo

	v = Viadeo()

	return HttpResponseRedirect( v.get_url() )

def viadeo_return(request):
	from viadeo import Viadeo

	v = Viadeo()
	v.set_code(request.GET.get('code'))


	f_user = v.get_full_user()

	email = f_user['data']['email']
	u = User.objects.filter(email=email)

	if u.exists():
		user = u.first()
		user.backend = 'django.contrib.auth.backends.ModelBackend'
		login(request, user)
		v.import_datas(user.member, user.member.cv)
		return tools.redirect(request, 2)

	password = "cvG456hz"
	user = User.objects.create_user(email, email, password)
	user.backend = 'django.contrib.auth.backends.ModelBackend'

	member = Member(email=user.email, first_name=f_user['data']['firstName'],last_name=f_user['data']['lastName'], user=user, rs_pwd=True, rs_type=4)
	member.save()

	if 'ecole' in request.session:
		member.school = request.session['ecole']
		member.save()

	g = Group.objects.get(name='member')
	g.user_set.add(user)
	g.save()

	cv = Cv(member=member, email=member.email, first_name=member.first_name, last_name=member.last_name)
	cv.save()

	v.import_datas(member, cv)

	login(request, user)

	return HttpResponseRedirect(reverse('members:inscription-step-2'))
