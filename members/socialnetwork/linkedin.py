from rauth.service import OAuth2Service
import json, requests
import time, random, hashlib, urllib2

class Linkedin(object):

	callback="https://www.pitchmyjob.com/sn/linkedin-return"

	def __init__(self):
		self.linkedin = OAuth2Service(
			name='linkedin',
			client_id='77heghkyjgqwby',
			client_secret='TNReXiAvutCILXmD',
			access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
			authorize_url='https://www.linkedin.com/uas/oauth2/authorization'
		)

	def get_url(self):
		params = { 'response_type' : 'code', 'redirect_uri' : self.callback, 'state' : hashlib.sha1(str(time.time())+str(random.randint(1, 1000000))).hexdigest(), 'scope' : 'r_basicprofile,r_emailaddress'}
		url = self.linkedin.get_authorize_url(**params)
		return url


	def get_user_data(self, code):
		data={'grant_type': 'authorization_code', 'code':code, 'redirect_uri' : self.callback}

		result = self.linkedin.get_raw_access_token(data=data)
		token=json.loads(result.text)

		if 'access_token' not in token:
			return False

		#request = requests.get("https://api.linkedin.com/v1/people/~:(public-profile-url,emailAddress,first-name,last-name,date-of-birth)?format=json", headers={"Authorization" : " Bearer %s" % token['access_token']})
		#res = json.loads(request.text)

		hder = " Bearer %s" % token['access_token']

		req = urllib2.Request("https://api.linkedin.com/v1/people/~:(public-profile-url,emailAddress,first-name,last-name,date-of-birth)?format=json")
		req.add_header('Authorization', hder)
		resp = urllib2.urlopen(req)
		content = resp.read()

		return json.loads(content)

		#return res

