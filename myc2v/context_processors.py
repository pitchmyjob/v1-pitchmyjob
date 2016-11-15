from rest_framework.authtoken.models import Token
from notifications.models import Message, Notification
from django.db.models import Q

def token_api(request):
	if request.user.is_authenticated():
		obj, created = Token.objects.get_or_create(user = request.user)
		return {'apitoken' : obj }
	else:
		return {'apitoken' : False }


def nb_msg(request):
	if request.user.is_authenticated():
		count = Message.objects.filter(receiver=request.user).filter(view=0).count()
		notif = Notification.objects.filter(receiver=request.user).filter(view=0).count()
		return {'nb_msg' : count, 'nb_notif' : notif }
	else:
		return {'nb_msg' : 0, 'nb_notif' : 0 }
