from django.utils.timezone import now
from members.models import Member
from django.http import HttpResponseRedirect, HttpResponsePermanentRedirect
from django.core.urlresolvers import reverse
import re
from plugin.mdetect import UAgentInfo

class SetLastVisitMiddleware(object):

    def process_response(self, request, response):
        url = request.get_full_path()
        return response
        if not request.is_secure():
            return HttpResponsePermanentRedirect( "https://www.pitchmyjob.com"+url )

        if 'pitchmyjob.fr' in request.META['HTTP_HOST']:
            return HttpResponsePermanentRedirect( "https://www.pitchmyjob.com/" )

        if 'pitchmyjob.com' == request.META['HTTP_HOST']:
            return HttpResponsePermanentRedirect( "https://www.pitchmyjob.com"+url )

        #if hasattr(request, 'user') :
        #if request.user.is_authenticated():
        # Update last visit time after request finished processing.
        #if request.user.groups.filter(name='member').exists():
        #Member.objects.filter(user=request.user).update(last_visit=now())

        return response

class MobileDetectionMiddleware(object):
    """
    Useful middleware to detect if the user is
    on a mobile device.
    """
    def process_request(self, request):
        is_mobile = False
        is_tablet = False
        is_phone = False

        user_agent = request.META.get("HTTP_USER_AGENT")
        http_accept = request.META.get("HTTP_ACCEPT")
        if user_agent and http_accept:
            agent = UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
            is_tablet = agent.detectTierTablet()
            is_phone = agent.detectTierIphone()
            is_mobile = is_tablet or is_phone or agent.detectMobileQuick()

            request.is_mobile = is_mobile
            request.is_tablet = is_tablet
            request.is_phone = is_phone