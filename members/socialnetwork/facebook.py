from rauth.service import OAuth2Service
import json, requests, urllib2, os, datetime
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File


class Facebook(object):

	callback="https://www.pitchmyjob.com/sn/facebook-return"

	def __init__(self):
		self.facebook = OAuth2Service(
			client_id='1521513254812652',
			client_secret='70a2811f04a3f48d3d7270abeaf31521',
			name='facebook',
			authorize_url='https://graph.facebook.com/oauth/authorize',
			access_token_url='https://graph.facebook.com/oauth/access_token',
			base_url='https://graph.facebook.com/'
		)

	def get_url(self):
		params = {'scope': 'user_birthday, user_location, user_about_me, user_status, email, public_profile',
			'response_type': 'code',
			'redirect_uri': self.callback
		}

		url = self.facebook.get_authorize_url(**params)

		return url


	def get_user_data(self, code):
		data={'grant_type': 'authorization_code', 'code':code, 'redirect_uri' : self.callback}

		token = self.facebook.get_access_token(data={'code': code, 'redirect_uri': self.callback})

		if not token:
			return False

		request = requests.get("https://graph.facebook.com/v2.6/me?fields=email%2Cbirthday%2Cfirst_name%2Clast_name%2Cage_range%2Cpicture.type(large)&access_token="+token)

		res = json.loads(request.text) 

		return res


	def save_picture(self, member, lien):
		img_temp = NamedTemporaryFile(delete=True)
		img_temp.write(urllib2.urlopen(lien).read())
		img_temp.flush()
		member.image.save(str(member.id)+".jpg", File(img_temp))

		try:
			os.chmod(settings.MEDIA_ROOT+"c2v/"+str(member.id),0777)
			os.chmod(member.image.path,0777)
		except:
			pass