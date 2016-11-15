from django.shortcuts import render, get_object_or_404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from myc2v.mixins import OnlyMemberLoginRequiredMixin, MyC2VLoginRequiredMixin
from rest_framework.authtoken.models import Token
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from members.forms import VideoForm, AudioForm
from members.models import Video, Member
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from members.forms import LoginForm
import cStringIO as StringIO
from xhtml2pdf import pisa
from django.template.loader import get_template, render_to_string
from django.template import Context
from django.http import HttpResponse
from cgi import escape
from django.template.defaultfilters import slugify


class Myc2vView(MyC2VLoginRequiredMixin, TemplateView):
	template_name = 'c2v/myc2v.html'

	def get(self, request, *args, **kwargs):
		mb = request.user.member
		name = slugify( request.user.member.first_name+"-"+request.user.member.last_name )
		return HttpResponseRedirect( reverse('c2v:c2v_view', args=[mb.id, name]) )

	def get_context_data(self, **kwargs):
		#return HttpResponseRedirect( reverse('members:list-job') )
		context = super(Myc2vView, self).get_context_data(**kwargs)
		obj, created = Token.objects.get_or_create(user = self.request.user)
		context['key'] = obj
		return context


def C2vView(request, pk=None, slug=None):
	if request.user.groups.filter(name='member').exists() and request.user.is_authenticated():
		obj, created = Token.objects.get_or_create(user = request.user)
		return render(request, 'c2v/myc2v.html', { 'key' : obj})
	else:
		member = get_object_or_404(Member, pk=pk)
		cv = member.cv
		return render(request, 'c2v/c2v.html', { 'cv' : cv, 'modif' : False })
 

def Myc2vLoginView(request):
	form = LoginForm(request.POST or None)
	if form.is_valid():
		user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
		if user is not None:
			if user.groups.filter(name='member').exists():
				login(request, user)
				return HttpResponseRedirect( request.GET.get('next', '/') )
			else:
				form.add_error(None, 'Veuillez vous connecter avec un compte Membre.')
		else:
			form.add_error(None, 'L\'email et le mot de passe ne correspondent pas.')

	context = {"form":form}
	return render(request, 'c2v/myc2v-login.html', context)

@login_required()
def theme(request):
	if request.method == "POST":
		modif = False
		if request.POST.get('id_member'):
			member = Member.objects.get(id = request.POST.get('id_member'))
			cv = member.cv
		else :
			cv = request.user.member.cv
	else:
		modif = True
		cv = request.user.member.cv

	return render(request, 'c2v/themes/theme-1.html', { 'cv' : cv, 'modif' : modif })


def webcam(request):
	return render(request, 'c2v/webcam.html')


def generate_pdf(template_src, context_dict):
	template = get_template(template_src)
	context = Context(context_dict)
	html  = template.render(context)
	result = StringIO.StringIO()
	pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("UTF-8")), result, encoding='UTF-8')
	if not pdf.err:
		return result.getvalue()

	return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))

def render_to_pdf(template_src, context_dict, name):
	
	response = HttpResponse( generate_pdf(template_src, context_dict), content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="'+name+'.pdf"'
	return response
	#return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


def download(request):
	name = slugify( request.user.member.first_name+"-"+request.user.member.last_name )
	return render_to_pdf('c2v/themes/pdf-theme-1.html', { 'pagesize':'A4', 'cv': request.user.member.cv }, "cv-"+str(name) )

def audio(request):
	return render(request, 'c2v/audio.html' )

@csrf_exempt
def upload_audio(request):
	if request.method == "POST":
		form = AudioForm(request.POST, request.FILES)
		if form.is_valid():
			audio = form.save()
	return render(request, 'c2v/audio.html')


def ManualImportLinkedin(request):
	from notifications.linkedin_scraper import LinkedInScraperOLD
	from notifications.notifications import script_import_linkedin

	if request.method == "POST":
		ld=LinkedInScraperOLD()
		ld.set_html(request.POST.get('html'))
		ld.parse()

		script_import_linkedin(ld, request.POST.get('id'))

		return HttpResponse( ld.data )

	return render(request, 'c2v/linkedin-import.html')