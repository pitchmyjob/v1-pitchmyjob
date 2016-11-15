# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse



def redirect(request, mode=1):
	if 'redirect_inscription' in request.session:
		try:
			redirect_inscription = request.session['redirect_inscription']
			del request.session['redirect_inscription']
			return HttpResponseRedirect( redirect_inscription )
		except:
			return HttpResponseRedirect( reverse('c2v:myc2v') )
	else:
		if mode==1:
			return HttpResponseRedirect( reverse('c2v:myc2v') )
		if mode==2:
			return HttpResponseRedirect( reverse('members:list-job') )
