from django.contrib import admin
from .models import Message, Notification

class MessageAdmin(admin.ModelAdmin):
	list_display = ('id', 'receiver', 'sender', 'message', 'date_posted')

class NotificationAdmin(admin.ModelAdmin):
	list_display = ('id', 'receiver', 'sender', 'type_notif', 'group', 'last_update')

admin.site.register(Message, MessageAdmin)
admin.site.register(Notification, NotificationAdmin)