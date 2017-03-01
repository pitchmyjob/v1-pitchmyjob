# -*- coding: utf-8 -*-
from rest_framework import serializers
from c2v.models import Cv, CvExperience, CvFormation, CvSkill, CvLanguage, CvInterest
from members.models import Member, Video, Audio
from pro.models import JobList, Job, Pro
from django.db.models import Q
from notifications.models import Message, Notification
import base64, urlparse, re
from django.core.files.base import ContentFile
from django.utils.dateformat import format


class FullDataProSerializer(serializers.ModelSerializer):
	class Meta:
		model = Pro
		fields = '__all__'


class FullJobSerialier(serializers.ModelSerializer):
	class Meta:
		model = Job
		fields = '__all__'
		depth = 1


class CvInterestSerializer(serializers.ModelSerializer):
	class Meta:
		model = CvInterest
		fields = '__all__'

class CvLanguageSerializer(serializers.ModelSerializer):
	class Meta:
		model = CvLanguage
		fields = '__all__'

class CvSkillSerializer(serializers.ModelSerializer):
	class Meta:
		model = CvSkill
		fields = '__all__'

class CvExperienceSerializer(serializers.ModelSerializer):
	class Meta:
		model = CvExperience
		fields = '__all__'

class CvFormationSerializer(serializers.ModelSerializer):
	class Meta:
		model = CvFormation
		fields = '__all__'

class CvSerialize(serializers.ModelSerializer):
	cvskill_set = CvSkillSerializer(many=True)
	cvlanguage_set = CvLanguageSerializer(many=True)
	cvinterest_set = CvInterestSerializer(many=True)
	cvexperience_set = CvExperienceSerializer(many=True)
	cvformation_set = CvFormationSerializer(many=True)

	class Meta:
		model = Cv
		fields = '__all__'

class FullDataBaseMemberSerializer(serializers.ModelSerializer):
	cv = CvSerialize()

	class Meta:
		model = Member
		exclude = ('user', )
		depth=1


class JobSerializer(serializers.ModelSerializer):

	class Meta:
		model = Job
		fields = ('company', 'job_title', 'description')

class Base64ImageField(serializers.ImageField):
	def to_internal_value(self, data):
		if isinstance(data, basestring) and data.startswith('data:image'):
			# base64 encoded image - decode
			format, imgstr = data.split(';base64,')  # format ~= data:image/X,
			ext = format.split('/')[-1]  # guess file extension

			data = ContentFile(base64.b64decode(imgstr), name='myc2v-experience.' + ext)

		return super(Base64ImageField, self).to_internal_value(data)


class Base64AudioField(serializers.FileField):
	def to_internal_value(self, data):
		if isinstance(data, basestring) :
			# base64 encoded image - decode
			#format, imgstr = data.split(';base64,')  # format ~= data:image/X,
			#ext = format.split('/')[-1]  # guess file extension

			data = ContentFile(base64.b64decode(data), name='entretien.wav')

		return super(Base64AudioField, self).to_internal_value(data)

class MetierListSerializer(serializers.ModelSerializer):
	val = serializers.SerializerMethodField()

	def get_val(self, obj):
		return obj.name

	class Meta:
		model = JobList
		fields = ('val', )

class MycvSerializer(serializers.ModelSerializer):
	birthday 	= serializers.DateField(required = False, format = "%d/%m/%Y", input_formats = ['%d/%m/%Y'], error_messages={'invalid': 'invalid'} )

	class Meta:
		model = Cv
		fields = ('first_name', 'last_name', 'email', 'birthday', 'city', 'country', 'description', 'phone', 'site', 'poste')


class AudioSerializer(serializers.ModelSerializer):
	file_on_server  = Base64AudioField(required = True)
	reponse 		= serializers.IntegerField(required=True)
	class Meta:
		model = Audio
		fields = ('file_on_server', 'reponse')

class ExperienceSerializer(serializers.ModelSerializer):
	company 		= serializers.CharField(required = True)
	title 			= serializers.CharField(required = True)
	date_start 		= serializers.DateField(required = True, format = "%m/%Y", input_formats = ['%m/%Y'], error_messages={'required':'required', 'invalid': 'invalid'} )
	date_end 		= serializers.DateField(required = False, format = "%m/%Y", input_formats = ['%m/%Y'], error_messages={'invalid': 'invalid'}  )
	image 			= Base64ImageField(required = False)

	class Meta:
		model = CvExperience
		fields = ('id', 'company', 'title', 'location', 'date_start', 'date_end', 'description', 'image')

class FormationSerializer(serializers.ModelSerializer):
	school 			= serializers.CharField(required = True)
	degree 			= serializers.CharField(required = True)
	date_start 		= serializers.DateField(required = True, format = "%Y", input_formats = ['%Y'], error_messages={'required':'required', 'invalid': 'invalid'}  )
	date_end 		= serializers.DateField(required = False, format = "%Y", input_formats = ['%Y'], error_messages={'invalid': 'invalid'}  )
	image 			= Base64ImageField(required = False)

	class Meta: 
		model = CvFormation
		fields = ('id', 'school', 'degree', 'discipline', 'date_start', 'date_end', 'description', 'image')


class SkillSerializer(serializers.ModelSerializer):
	name 			= serializers.CharField(required = True)
	level 			= serializers.ChoiceField(choices={0,1,2,3,4,5}, required = True)

	class Meta:
		model = CvSkill
		fields = ('id', 'name', 'level')


class LanguageSerializer(serializers.ModelSerializer):
	name 			= serializers.CharField(required = True)
	level 			= serializers.ChoiceField(choices={0,1,2,3,4,5}, required = True)

	class Meta:
		model = CvLanguage
		fields = ('id', 'name', 'level')

class InterestSerializer(serializers.ModelSerializer):
	name 			= serializers.CharField(required = True)

	class Meta:
		model = CvInterest
		fields = ('id', 'name')


class MediaSerializer(serializers.ModelSerializer):
	image 	= Base64ImageField()
	class Meta:
		model = Member
		fields = ('image', )

class LinkVideoSerializer(serializers.ModelSerializer):
	link_url 	= serializers.URLField(required = True)
	type_video 	= serializers.IntegerField(required=False)
	video_id 	= serializers.CharField(required=False)

	def validate(self, datas):
		parsed = urlparse.urlparse( datas['link_url'] )
		if "youtube" in datas['link_url']  :
			datas['type_video'] = 2
			datas['video_id'] = urlparse.parse_qs(parsed.query)['v'][0]
			return datas
		elif "dailymotion" in datas['link_url']  :
			datas['type_video'] = 3
			datas['video_id'] = re.search('video\/([a-zA-Z0-9]+)_',  datas['link_url'] ).group(1)
			return datas
		elif "vimeo" in datas['link_url']  :
			datas['type_video'] = 4
			datas['video_id'] = parsed[2][1:]
			return datas
		raise serializers.ValidationError("L'url doit etre un lien Youtube, Dailymotion ou Viemo uniquement.") 


	class Meta:
		model = Video
		fields = ('link_url', 'type_video', 'video_id')

class VideoRecorDetail(serializers.Serializer):
	token 			= serializers.CharField(required=True) 
	embed_url		= serializers.CharField(required=True) 
	extension		= serializers.CharField(required=False) 

class VideoRecordEntretienSerializer(serializers.Serializer):
	token 			= serializers.CharField(required=True) 
	embed_url		= serializers.CharField(required=True) 
	extension		= serializers.CharField(required=False)
	candidature 	= serializers.IntegerField(required=True)

class VideoRecordEntretienTimeSerializer(serializers.Serializer):
	time			= serializers.IntegerField(required=True)
	candidature 	= serializers.IntegerField(required=True)
	nb 		 	 	= serializers.IntegerField(required=True)


class FbConnectSerializer(serializers.Serializer):
	first_name 		= serializers.CharField(required=True) 
	last_name 		= serializers.CharField(required=True) 
	url 			= serializers.CharField(required=False) 
	email 			= serializers.CharField(required=True) 
	birthday		= serializers.DateField(required = True, format = "%m/%d/%Y", input_formats = ['%m/%d/%Y'] )

class LinkedinConnectSerializer(serializers.Serializer):
	firstName 		 = serializers.CharField(required=True) 
	lastName 		 = serializers.CharField(required=True) 
	publicProfileUrl = serializers.CharField(required=False) 
	emailAddress 	 = serializers.CharField(required=True) 
	#birthday		 = serializers.DateField(required = False, format = "%m/%d/%Y", input_formats = ['%m/%d/%Y'] )

class ImportLinkedinSerializer(serializers.Serializer):
	url  = serializers.CharField(required=True) 

class SendC2vEmailSerializer(serializers.Serializer):
	email 			= serializers.EmailField(required=True) 
	message		    = serializers.CharField(required=True) 

class SendInvitationOffreSerializer(serializers.Serializer):
	email 			= serializers.CharField(required=True) 
	message		    = serializers.CharField(required=True) 
	job		    	= serializers.CharField(required=True)

class SendDemandeEntretienSerializer(serializers.Serializer):
	user 			= serializers.CharField(required=True)
	job		    	= serializers.CharField(required=True)

class DeclineCandidatureSerializer(serializers.Serializer):
	member 			= serializers.IntegerField(required=True) 
	job 			= serializers.IntegerField(required=True) 
	message		    = serializers.CharField(required=True)


class CreateMessageSerializer(serializers.Serializer): 
	receiver 		= serializers.IntegerField(required=True)
	message 		= serializers.CharField(required=True, max_length=5000)

class VerificationEmailSerializer(serializers.Serializer):
	email 		= serializers.CharField(required=True)

class GroupListMessageSerializer(serializers.ModelSerializer):
	message = serializers.SerializerMethodField()
	view = serializers.SerializerMethodField()
	date_posted = serializers.SerializerMethodField()
	timestamp = serializers.SerializerMethodField()
	user 	= serializers.SerializerMethodField()

	def message_objet(self, user1, user2):
		return Message.objects.filter( Q(sender=user1, receiver=user2) | Q(receiver=user1, sender=user2) ).order_by('-date_posted')

	def get_message(self, obj):
		message = self.message_objet(obj.sender, obj.receiver)
		return message.first().message[0:50]+" .."

	def get_view(self, obj):
		message = self.message_objet(obj.sender, obj.receiver)
		msg = message.first().view
		if self.context['update']:
			message.update(view = 1) 
		return msg

	def get_date_posted(self, obj):
		message = self.message_objet(obj.sender, obj.receiver)
		return message.first().date_posted.strftime("%d %b %Y %H:%M:%S")

	def get_timestamp(self, obj):
		message = self.message_objet(obj.sender, obj.receiver)
		datetime = message.first().date_posted
		return  format(datetime, u'U')

	def get_user(self, obj):
		if self.context['request'].user.groups.filter(name='member').exists():
			return {'name' : obj.sender.pro.company, 'image' : obj.sender.pro.image['logo50'].url, 'id' : obj.sender.pro.id }
		if self.context['request'].user.groups.filter(name='pro').exists():
			return {'name' : obj.receiver.member.first_name+" "+obj.receiver.member.last_name, 'image' : obj.receiver.member.image['profil50'].url, 'id' : obj.receiver.member.id }


	class Meta:
		model = Message
		fields = ('sender', 'receiver', 'message', 'date_posted', 'group', 'view', 'timestamp', 'user')	


class MessageListSerializer(serializers.ModelSerializer):
	date_posted = serializers.DateTimeField( format = "%d %b %Y %H:%M:%S")
	user 	= serializers.SerializerMethodField()

	def get_user(self, obj):
		current = 1 if self.context['request'].user.id == obj.sender.id else 0
		if obj.group == 2:
			return {'name' : obj.sender.pro.company, 'image' : obj.sender.pro.image['logo50'].url, 'current': current, 'id' : obj.sender.pro.id }
		if obj.group == 1:
			return {'name' : obj.sender.member.first_name+" "+obj.sender.member.last_name, 'image' : obj.sender.member.image['profil50'].url, 'current': current, 'id' : obj.sender.member.id }

	class Meta:
		model = Message
		fields = ('id', 'receiver', 'sender', 'message', 'date_posted', 'user', 'group')


class NotificationListSerializer(serializers.ModelSerializer):
	type_notif 	= serializers.SerializerMethodField()
	user 	    = serializers.SerializerMethodField()
	last_update = serializers.DateTimeField( format = "%d %b %Y %H:%M:%S")

	def get_type_notif(self, obj):
		if obj.type_notif == 7:
			return u"%s a visité votre profil" % obj.sender.pro.company
		if obj.type_notif == 5:
			return u"Nouvelle candidature de %s" % obj.sender.member.first_name
		return obj.type_notif

	def get_user(self, obj):
		if obj.sender.groups.filter(name='member').exists():
			return {'name' : obj.sender.member.first_name+" "+obj.sender.member.last_name, 'image' : obj.sender.member.image['profil50'].url, 'id' : obj.sender.member.id }
		if obj.sender.groups.filter(name='pro').exists():
			return {'name' : obj.sender.pro.company, 'image' : obj.sender.pro.image['logo50'].url, 'id' : obj.sender.pro.id }


	class Meta:
		model = Notification
		fields = ('id', 'receiver', 'sender', 'type_notif', 'group', 'last_update', 'user', 'view')


#--------------------- NEW CANDIDATURE -------------------------

class ValideEntretienSerializer(serializers.Serializer):
	candidature = serializers.IntegerField(required=True)
	user = serializers.CharField(required=True)

class VideoQuestionSerializer(serializers.Serializer):
	token 			= serializers.CharField(required=True)
	embed_url		= serializers.CharField(required=True)
	candidature 	= serializers.IntegerField(required=True)
	question	 	= serializers.IntegerField(required=True)
	user	 	 = serializers.CharField(required=True)