import time, random, hashlib, urllib, requests, hmac, json
from hashlib import sha1
from django.http import HttpResponseRedirect
from django.conf import settings

class DoYouBuzz(object):

	signature_method="HMAC-SHA1"
	request_token_path="oauth/requestToken"
	authorize_path="oauth/authorize"
	access_token_path="oauth/accessToken";

	base_url = "https://www.pitchmyjob.com/"
	#callback_url = 'return-doyoubuzz'

	site_api="http://www.doyoubuzz.com/fr/"

	shared_key="aupsiwmO3YRNTUxE1zIV"
	shared_secret="TWwkaRDC0eMfl7KLvZGqVE3NO"

	token=""
	token_secret=""

	access_token=""
	token_secret=""

	def __init__(self, callback=None):
		self.callback_url=callback

	def get_request_token(self):

		prot={
			"oauth_consumer_key"       : self.shared_key,
			"oauth_signature_method"   : self.signature_method,
			"oauth_timestamp"          : int(time.time()),
			"oauth_nonce"              : hashlib.sha1(str(time.time())+str(random.randint(1, 1000000))).hexdigest(),
			"oauth_callback"           : str(self.base_url)+str(self.callback_url)
		}

		url=self.site_api+self.request_token_path
		prot['oauth_signature']=self.sign_request("GET", url, prot, '')
		requests=self.http_get(url, prot)

		final=self._get_dict_token(requests.text)

		self.token=final['oauth_token']
		self.token_secret=final['oauth_token_secret']

		return self

	def get_user_authorization(self):
		url_redirect = self.site_api+self.authorize_path+"?oauth_token="+self.token+"&oauth_callback="+self.base_url+self.callback_url
		return HttpResponseRedirect( url_redirect ) 


	def get_access_token(self, request_token, oauth_verifier, token_secret):
		prot = {
			"oauth_verifier"           : oauth_verifier,
			"oauth_consumer_key"       : self.shared_key,
			"oauth_signature_method"   : self.signature_method,
			"oauth_nonce"              : hashlib.sha1(str(time.time())+str(random.randint(1, 1000000))).hexdigest(),
			"oauth_timestamp"          : int(time.time()),
			"oauth_version"            : "1.0",
			"oauth_token"              : request_token,
		}

		url=self.site_api+self.access_token_path
		prot['oauth_signature']=self.sign_request("GET", url, prot, token_secret)

		requests=self.http_get(url, prot)
		tokens=self._get_dict_token(requests.text)

		if 'oauth_token' not in tokens:
			return False

		self.access_token = tokens['oauth_token']
		self.token_secret = tokens['oauth_token_secret']

		return True


	def request(self, url, params, oauth_token=None, token_secret=None, method = "GET"):
		if not oauth_token:
			oauth_token=self.access_token
		if not token_secret:
			token_secret=self.token_secret

		prot = {
			"oauth_consumer_key"       : self.shared_key,
			"oauth_token"              : oauth_token,
			"oauth_signature_method"   : self.signature_method,
			"oauth_timestamp"          : int(time.time()),
			"oauth_nonce"              : hashlib.sha1(str(time.time())+str(random.randint(1, 1000000))).hexdigest()
		}

		prot = prot.copy()
		prot.update(params)

		prot['oauth_signature']=self.sign_request(method, url, prot, token_secret)

		if method=="GET":
			result=self.http_get(url, prot)

		return json.loads(result.text)


	def http_get(self, url, prot):
		protheader=self._build_protocol_string(prot)
		prot = sorted(prot.items())
		url=url+"?"+urllib.urlencode(prot)
		header=[]
		header.append("Expect:")
		header.append("Authorization: OAuth realm=\"\", "+protheader)
		request = requests.get(url, headers={"Authorization" : " OAuth realm=\"\", "+protheader})
		return request

	def _build_protocol_string(self, prot):
		arr = []
		for k, p in prot.iteritems():
			string=str(k)+"="+str(p)
			arr.append(string)
		return ", ".join(arr)


	def sign_request(self, method, url, params, token_secret):
		url=urllib.quote(url, safe='')
		params = sorted(params.items())
		params = urllib.urlencode(params)
		params = urllib.quote(params, safe='')
		base_string=method+"&"+url+"&"+params
		key=self.shared_secret+"&"+str(token_secret)
		string=hmac.new(key, base_string, sha1)
		string=string.digest().encode("base64").rstrip('\n')
		return string

	def _get_dict_token(self, tab):
		if tab:
			requests=tab.split('&')
			final ={}
			for r in requests:
				a = r.split('=')
				if len(a) > 1 :
					final[a[0]]=a[1]

			return final
		return None


	def import_data(self, result, member, cv):
		from django.core.files.temp import NamedTemporaryFile
		from django.core.files import File
		import urllib2, os, datetime
		from c2v.models import Cv, CvExperience, CvFormation, CvSkill, CvLanguage, CvInterest

		try:
			if 'avatars' in result['user']:
				lien=result['user']['avatars']['big']
				img_temp = NamedTemporaryFile(delete=True)
				img_temp.write(urllib2.urlopen(lien).read())
				img_temp.flush()
				member.image.save(str(member.id)+".jpg", File(img_temp))

			try:
				os.chmod(settings.MEDIA_ROOT+"c2v/"+str(member.id),0777)
				os.chmod(member.image.path,0777)
			except:
				pass
		except:
			pass
			
		if 'resumes' not in result['user']:
			return False
			if 'resume' not in result['user']['resumes']:
				return False

		id_cv = result['user']['resumes']['resume'][0]['id']
		datas=self.request('http://api.doyoubuzz.com/cv/'+str(id_cv), {'format' : 'json'} )
		url="http://www.doyoubuzz.com"

		if 'resume' in datas:
			resume=datas['resume']
			cv.site=resume['url']
			cv.poste=resume['title']
			if 'userInformation' in resume:
				user_information = resume['userInformation']
				if 'birthdate' in user_information:
					try:
						birthdate = datetime.datetime.strptime(user_information['birthdate'], "%Y-%m-%d").date()
						cv.birthday=birthdate
						member.birthday=birthdate
					except:
						pass

				u_city = ""
				u_zip = ""

				if 'city' in user_information :
					if user_information['city']:
						u_city = user_information['city']
	

				if 'zipcode' in user_information :
					if user_information['zipcode']:
						u_zip = user_information['zipcode']

				cv.city=str(u_city)+" "+str(u_zip)
			
			if 'contacts' in resume:
				if 'contact' in resume['contacts']:
					for contact in resume['contacts']['contact']:
						if contact['type'] == "phone":
							member.phone=contact['value']
							cv.phone=contact['value']
						if contact['type'] == "mobile":
							member.phone=contact['value']
							cv.phone=contact['value']

			member.save()
			cv.save()

			if 'experiences' in resume:
				if 'experience' in resume['experiences']:
					exps = resume['experiences']['experience']
					for exp in exps:
						
						cvExp = CvExperience(cv=cv, company=exp['company'], title=exp['title'])
						if exp['end']:
							try:
								df=datetime.datetime.strptime(exp['end'], '%Y-%m-%d')
								cvExp.date_end=df
							except:
								pass

						try:
							dd = datetime.datetime.strptime(exp['start'], '%Y-%m-%d')
							cvExp.date_start=dd
						except:
							pass

						cvExp.save()

						if exp['logo']:
							img_temp = NamedTemporaryFile(delete=True)
							img_temp.write(urllib2.urlopen(url+exp['logo']).read())
							img_temp.flush()
							cvExp.image.save(str(cvExp.id)+".jpg", File(img_temp))

			if 'educations' in resume:
				if 'education' in resume['educations']:
					educs = resume['educations']['education']
					for educ in educs:
						cvEduc = CvFormation(cv=cv, school=educ['school'], degree=educ['degree'], description=educ['description'])

						if educ['start']:
							try:
								cvEduc.date_start=datetime.datetime.strptime(educ['start'], '%Y-%m-%d')
							except:
								pass

						if educ['end']:
							try:
								cvEduc.date_end=datetime.datetime.strptime(educ['end'], '%Y-%m-%d')
							except:
								pass

						cvEduc.save()

			if 'skills' in resume:
				if 'skill' in resume['skills']:
					for skill in resume['skills']['skill']:
						for libelle in skill['children']['skill']:

							if skill['title'].lower() in ("langue", "langue", "language", "langage"):
								cvSkill = CvLanguage(cv=cv, name=libelle['title'])
							else:
								cvSkill = CvSkill(cv=cv, name=libelle['title'])

							if libelle['level']:
								level = int(libelle['level'] / 20)
								if level == 0:
									level=1
								cvSkill.level=level

							cvSkill.save()

			if 'interests' in resume:
				if 'interest' in resume['interests']:
					for interests in resume['interests']['interest']:
						for libelle in interests['children']['interest']:
							if libelle['title']:
								CvInterest(cv=cv, name=libelle['title']).save()
