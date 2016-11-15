from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .models import Message, Notification

@login_required()
def message(request, pk):
	if request.user.groups.filter(name='member').exists():
		return HttpResponseRedirect( reverse('members:message', args=[pk]) )
	if request.user.groups.filter(name='pro').exists():
		return HttpResponseRedirect( reverse('pro:message', args=[pk]) ) 


@login_required()
def get_notification(request):
	notif=list(request.user.notification_received.order_by('-last_update'))
	request.user.notification_received.update(view=1)
	return render(request, 'notifications/list_notification.html', {'notifications':notif})