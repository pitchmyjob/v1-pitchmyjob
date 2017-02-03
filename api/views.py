# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins
from c2v.models import Cv, CvExperience, CvFormation, CvSkill, CvLanguage, CvInterest
from members.models import Video, CandidatureReponse, Member, Candidature, Interest
from pro.models import JobList, Pro, Job
from notifications.models import Message, Notification
from django.db.models import Q, Max
from api.serializers import *
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files import File
import urlparse, urllib2, operator, signal, datetime
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.core.files.temp import NamedTemporaryFile
from django.core.mail import EmailMessage
from c2v.views import generate_pdf, render_to_pdf
from notifications.notifications import notification, async_send_email, async_send_email_attach, alert_message, async_linkedin_cv
from django.template.defaultfilters import slugify
from rest_framework.parsers import JSONParser
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000


class FullDataBaseMember(generics.ListAPIView):
	queryset = Member.objects.annotate(num_exp=Count('tags', distinct=True)).filter(num_exp__lte=1)
	serializer_class = FullDataBaseMemberSerializer
	pagination_class = LargeResultsSetPagination


class JobApiList(APIView):
	def get(self, request, format=None):

		jobs = Job.objects.filter(scraper=False)

		if self.request.query_params.get('s', None) :
			jobs = jobs.filter(job_title__icontains=self.request.query_params.get('s', None))

		serializer = JobSerializer(jobs, many=True)

		return Response(serializer.data)

class VerificationCvApply(APIView):
	authentication_classes = (TokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	def get(self, request, format=None):
		exp = self.request.user.member.cv.cvexperience_set.count()
		frm = self.request.user.member.cv.cvformation_set.count()
		if exp < 1 or frm < 1:
			return Response({'cv': False})
		else:
			return Response({'cv': True})

class VerificationEmail(APIView):
	def post(self, request, format=None):
		serializer = VerificationEmailSerializer(data=request.data)
		if serializer.is_valid():
			user = User.objects.filter(username=serializer.validated_data.get('email'))
			return Response({'email': user.exists()})

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginRequiredMixin(object):
	authentication_classes = (TokenAuthentication, )
	permission_classes = (IsAuthenticated,) 

class MetierList(generics.ListAPIView):
	queryset = JobList.objects.filter(active=True)
	serializer_class = MetierListSerializer

class CustomListCreateMixin(generics.ListCreateAPIView):
	def perform_create(self, serializer):
		serializer.save( cv = self.request.user.member.cv )

class GroupMessage(LoginRequiredMixin, APIView):

	def post(self, request, format=None):
		serializer = CreateMessageSerializer(data=request.data)
		if serializer.is_valid():	
			if self.request.user.groups.filter(name='member').exists():
				#if Message.objects.filter(sender = , receiver=self.request.user).exists():
				sender=self.request.user.member
				receiver = Pro.objects.get(id=serializer.validated_data.get('receiver'))
				group=1
			if self.request.user.groups.filter(name='pro').exists():
				sender=self.request.user.pro
				receiver = Member.objects.get(id=serializer.validated_data.get('receiver'))
				group=2

			last_message = Message.objects.filter( sender = self.request.user, receiver=receiver.user, date_posted__gte=(datetime.datetime.now() - datetime.timedelta(minutes=5)) )
			alert_message(self.request.user, receiver.user, group, last_message)

			Message( sender = self.request.user, receiver=receiver.user, group=group, message=serializer.validated_data.get('message') ).save()

			#with SocketIO("http://www.pitchmyjob.com", 8080) as socketIO:
				#obj, created = Token.objects.get_or_create(user=receiver.user)
				#socketIO.emit("api_msg", { 'token' : obj.key, 'sender' : sender.id })

			return Response( serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	def get(self, request, format=None):
		if self.request.user.groups.filter(name='member').exists():
			messages = Message.objects.filter( Q(sender=self.request.user) | Q(receiver=self.request.user) ).exclude(sender=self.request.user).distinct('sender')
		if self.request.user.groups.filter(name='pro').exists():
			messages = Message.objects.filter( Q(sender=self.request.user) | Q(receiver=self.request.user) ).exclude(receiver=self.request.user).distinct('receiver')

		serializer = GroupListMessageSerializer(messages, many=True, context={'request': request, 'update' : self.request.query_params.get('update', None) })
		datas = sorted(serializer.data,key=lambda x:x['timestamp'], reverse=True)

		return Response( datas )


class MessagesList(LoginRequiredMixin, generics.ListAPIView):
	serializer_class = MessageListSerializer

	def get_serializer_context(self):
		return {'request': self.request}

	def get_queryset(self):
		if self.request.user.groups.filter(name='member').exists():
			user = get_object_or_404(Pro, id=self.kwargs['pk'])
		if self.request.user.groups.filter(name='pro').exists():
			user = get_object_or_404(Member, id=self.kwargs['pk'])

		message=Message.objects.filter(  Q(sender=self.request.user, receiver=user.user) | Q(receiver=self.request.user, sender=user.user) ).order_by('date_posted')
		self.request.user.message_received.filter(sender=user.user).update(view=1)
		return message

class NotificationList(LoginRequiredMixin, generics.ListAPIView):
	serializer_class = NotificationListSerializer

	def get_queryset(self):
		notif = list(self.request.user.notification_received.all())
		self.request.user.notification_received.update(view=1)
		return notif


class MycvDetail(LoginRequiredMixin, generics.RetrieveUpdateAPIView):
	serializer_class = MycvSerializer

	def get_object(self):
		return self.request.user.member.cv

class MycvExperienceList(LoginRequiredMixin, CustomListCreateMixin):
	serializer_class = ExperienceSerializer

	def get_queryset(self):
		return self.request.user.member.cv.cvexperience_set.all()

class MycvExperienceDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
	serializer_class = ExperienceSerializer

	def get_queryset (self):
		return self.request.user.member.cv.cvexperience_set.all()


class MycvFormationList(LoginRequiredMixin, CustomListCreateMixin):
	serializer_class = FormationSerializer

	def get_queryset(self):
		return self.request.user.member.cv.cvformation_set.all()

class MycvFormationDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
	serializer_class = FormationSerializer

	def get_queryset (self):
		return self.request.user.member.cv.cvformation_set.all()


class MycvSkillList(LoginRequiredMixin, CustomListCreateMixin):
	serializer_class = SkillSerializer

	def get_queryset(self):
		return self.request.user.member.cv.cvskill_set.all()

class MycvSkillDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
	serializer_class = SkillSerializer

	def get_queryset (self):
		return self.request.user.member.cv.cvskill_set.all()


class MycvLanguageList(LoginRequiredMixin, CustomListCreateMixin):
	serializer_class = LanguageSerializer

	def get_queryset(self):
		return self.request.user.member.cv.cvlanguage_set.all()

class MycvLanguageDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
	serializer_class = LanguageSerializer

	def get_queryset (self):
		return self.request.user.member.cv.cvlanguage_set.all()


class MycvInterestList(LoginRequiredMixin, CustomListCreateMixin):
	serializer_class = InterestSerializer

	def get_queryset(self):
		return self.request.user.member.cv.cvinterest_set.all()

class MycvInterestDetail(LoginRequiredMixin, generics.RetrieveUpdateDestroyAPIView):
	serializer_class = InterestSerializer

	def get_queryset (self):
		return self.request.user.member.cv.cvinterest_set.all()

class MediaDetail(LoginRequiredMixin, generics.RetrieveUpdateAPIView):
	serializer_class = MediaSerializer

	def get_object(self):
		return self.request.user.member

class VideoDetail(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = LinkVideoSerializer(data=request.data)
		if serializer.is_valid():		
			if Video.objects.filter(member = self.request.user.member ).exists():
				video = self.request.user.member.video
			else:
				video = Video( member = self.request.user.member )

			video.link_url = serializer.validated_data.get('link_url')
			video.type_video = serializer.validated_data.get('type_video')
			video.video_id = serializer.validated_data.get('video_id')
			video.save()

			return Response( serializer.validated_data.get('video_id') , status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

class VideoRecordDetail(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = VideoRecorDetail(data=request.data)
		if serializer.is_valid():		
			if Video.objects.filter(member = self.request.user.member ).exists():
				video = self.request.user.member.video
			else:
				video = Video( member = self.request.user.member )

			video.embed_url			= serializer.validated_data.get('embed_url')
			video.type_video 		= 1
			video.video_id 			= serializer.validated_data.get('token')

			extension 	= serializer.validated_data.get('extension') if serializer.validated_data.get('extension') else "mp4"
			name 		= str(serializer.validated_data.get('token'))+"."+str(extension)

			#video.file_on_server 	= File(open('/var/www/vhosts/myc2v/media/records/'+name, 'r'))
			video.save()

			return Response( "Ok ! ", status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoRecordEntretien(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = VideoRecordEntretienSerializer(data=request.data)
		if serializer.is_valid():
			candidature = Candidature.objects.get(pk = serializer.validated_data.get('candidature'), member =self.request.user.member )	

			if Video.objects.filter(candidature = candidature ).exists():
				video = Video.objects.get( candidature = candidature)
			else:
				video = Video()

			video.embed_url			= serializer.validated_data.get('embed_url')
			video.type_video 		= 1
			video.video_id 			= serializer.validated_data.get('token')
			video.save()
			candidature.video = video
			candidature.save()

			return Response( "Ok ! ", status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoRecordEntretienTime(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = VideoRecordEntretienTimeSerializer(data=request.data)
		if serializer.is_valid():
			candidature  = Candidature.objects.get(pk = serializer.validated_data.get('candidature'), member =self.request.user.member )
			reponse 	 = CandidatureReponse.objects.get(candidature=candidature, nb=serializer.validated_data.get('nb') )
			reponse.time = serializer.validated_data.get('time')
			reponse.save()

		return Response( "Ok ! ", status=status.HTTP_201_CREATED)


class AudioRecordEntretien(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = AudioSerializer(data=request.data)
		if serializer.is_valid():
			candidature = Candidature.objects.get(pk = serializer.validated_data.get('reponse') )		

			if Audio.objects.filter(candidature = candidature ).exists():
				audio = Audio.objects.get( candidature = candidature)
			else:
				audio = Audio()

			audio.file_on_server	= serializer.validated_data.get('file_on_server')
			audio.save()
			candidature.audio = audio
			candidature.save()

			return Response( "Ok ! ", status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ImportLinkedin(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = ImportLinkedinSerializer(data=request.data)
		if serializer.is_valid():
			url = serializer.validated_data.get('url')
			CvExperience.objects.filter(cv__member_id=self.request.user.member.id ).delete()
			CvFormation.objects.filter(cv__member_id=self.request.user.member.id ).delete()
			CvSkill.objects.filter(cv__member_id=self.request.user.member.id ).delete()
			CvLanguage.objects.filter(cv__member_id=self.request.user.member.id ).delete()
			CvInterest.objects.filter(cv__member_id=self.request.user.member.id ).delete()
			async_linkedin_cv(self.request.user.member.id, url) 
			return Response( {'import' : True }, status=status.HTTP_200_OK)
			
class SendC2VEmail(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = SendC2vEmailSerializer(data=request.data)
		if serializer.is_valid():
			message = serializer.validated_data.get('message')
			email = serializer.validated_data.get('email')
			tite = self.request.user.member.first_name+ " "+self.request.user.member.last_name+u" vous a envoyé son C2V"

			async_send_email_attach(tite, [email], "emails/send_cv.html", {"message":message}, {"name" : "mydoc.pdf", "file": generate_pdf('c2v/themes/pdf-theme-1.html', { 'pagesize':'A4', 'cv': self.request.user.member.cv }), "type": "application/pdf"})
			#async_send_email.delay(tite, [email], "emails/send_cv.html", {"message":message}) 
			return Response( {'ok' }, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DeclineCandidature(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = DeclineCandidatureSerializer(data=request.data)
		if serializer.is_valid():
			message=serializer.validated_data.get('message')
			job=serializer.validated_data.get('job')
			member = Member.objects.get(id = serializer.validated_data.get('member') ) 
			candidature = Candidature.objects.filter(member=member, job=job, job__pro =self.request.user.pro)
			interest = Interest.objects.filter(member=member, job=job)

			if interest.exists():
				interest = interest.first()
				interest.decline = True
				interest.save()

			if candidature.exists():
				candidature = candidature.first()
				candidature.decline = True
				candidature.save()
				
				notification(6, member, None, candidature.job, message)

				return Response( {'ok' }, status=status.HTTP_200_OK)

		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendInvitationAnnonce(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = SendInvitationOffreSerializer(data=request.data)
		if serializer.is_valid():
			message = serializer.validated_data.get('message')
			email = serializer.validated_data.get('email')
			job = serializer.validated_data.get('job')
			tite = self.request.user.pro.company+u" vous invite à postuler pour l'offre "+job

			async_send_email(tite, [email], "emails/send_cv.html", {"message":message})
			return Response( {'ok' }, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SendDemandeEntretien(LoginRequiredMixin, APIView):
	def post(self, request, format=None):
		serializer = SendDemandeEntretienSerializer(data=request.data)
		if serializer.is_valid():
			user = Member.objects.get(id=serializer.validated_data.get('user'))
			job = Job.objects.get(id=serializer.validated_data.get('job'))
			title =  u"%s s'interesse à vous" % job.company

			async_send_email(title, [user.email], "emails/send_invitation_entretien.html", {"id":job.id, "member": user.first_name, "job":job.job_title, "pro":job.company })

			return Response({'ok'}, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#------------------------------ NEW CANDIDATURE -------------------------------

class ValideEntretien(APIView):
	def post(self, request, format=None):
		serializer = ValideEntretienSerializer(data=request.data)
		if serializer.is_valid():

			token = Token.objects.get(key=serializer.validated_data.get('user'))

			candidature = Candidature.objects.get(pk=serializer.validated_data.get('candidature'), member=token.user.member)
			candidature.new = True
			candidature.active = True
			candidature.save()

			notification(1, token.user.member, None, candidature.job)
			notification(5, token.user.member, None, candidature.job)


			if candidature.job.mp:

				if candidature.job.mp_type == "broadbean" or candidature.job.mp_type == "multiposting" :
					ctx = {"questions": candidature.job.questions.all(), "links": candidature.candidaturereponse_set.all()}
					text = "%s %s %s" % (candidature.member.first_name, candidature.member.last_name, candidature.member.email)
					#async_send_email_attach(text, [candidature.job.mp_email], "emails/application_email.html", ctx,{"name": "cv.pdf", "file": generate_pdf('c2v/themes/pdf-theme-1.html',{'pagesize': 'A4','cv': request.user.member.cv}),"type": "application/pdf"})

					if candidature.cv:
						#attachment = open(candidature.cv.url, 'rb')
						cv = candidature.cv.read()
					else :
						cv = generate_pdf('c2v/themes/pdf-theme-1.html',{'pagesize': 'A4','cv': token.user.member.cv})

					async_send_email_attach(text, [candidature.job.mp_email, "tannier.yannis@gmail.com"], "emails/application_email.html", ctx,{"name": "cv.pdf", "file": cv, "type": "application/pdf"})

				if candidature.job.mp_type == "flatchr" :
					import requests

					if not candidature.cv:
						img_temp = NamedTemporaryFile(delete=True)
						img_temp.write( generate_pdf('c2v/themes/pdf-theme-1.html',{'pagesize': 'A4','cv': token.user.member.cv}) )
						img_temp.flush()
						candidature.cv.save("cv.pdf", File(img_temp))


					qt = []
					for question in candidature.job.questions.order_by('nb'):
						qt.append(question.question)

					rp = []
					for reponse in candidature.candidaturereponse_set.order_by('nb'):
						rp.append(reponse.video.path_aws_v2())

					payload = {
						'ref' : candidature.job.mp_flatchr_ref,
						'id' : candidature.job.id,
						'first_name' : token.user.member.first_name,
						'last_name' : token.user.member.last_name,
						'email' : token.user.email,
						'cv' : "https://www.pitchmyjob.com%s" % candidature.cv.url,
						'questions' : qt,
						'answers' : rp
					}
					response = requests.post("http://flatchr.io/vacancy/candidate/pitchmyjob", data=payload)

					return Response(payload)


			return Response("Ok ! ")
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VideoQuestionEntretienParams(LoginRequiredMixin, APIView):
	def get(self, request, format=None):

		candidature = self.request.query_params.get('candidature', None)
		question = self.request.query_params.get('question', None)
		embed_url = self.request.query_params.get('token', None)
		token = self.request.query_params.get('token', None)

		if candidature and question :

			candidature = Candidature.objects.get(pk = candidature, member =self.request.user.member )

			reponse = CandidatureReponse.objects.get(nb = question, candidature=candidature)

			video = Video()

			video.member 			= self.request.user.member
			video.job 				= candidature.job
			video.embed_url			= embed_url
			video.type_video 		= 1
			video.video_id 			= token
			video.save()

			reponse.video = video
			reponse.active=True
			reponse.save()

			return Response( "Ok ! ", status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoQuestionEntretien(APIView):
	def post(self, request, format=None):
		serializer = VideoQuestionSerializer(data=request.data)
		if serializer.is_valid():

			token = Token.objects.get(key=serializer.validated_data.get('user'))

			candidature = Candidature.objects.get(pk = serializer.validated_data.get('candidature'), member = token.user.member )

			reponse = CandidatureReponse.objects.get(nb = serializer.validated_data.get('question'), candidature=candidature)

			video = Video()

			video.member 			= token.user.member
			video.job 				= candidature.job
			video.embed_url			= serializer.validated_data.get('embed_url')
			video.type_video 		= 1
			video.video_id 			= serializer.validated_data.get('token')
			video.save()

			reponse.video = video
			reponse.active=True
			reponse.save()

			return Response( "Ok ! ", status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)