import requests, json, urllib2, os, datetime
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from c2v.models import Cv, CvExperience, CvFormation, CvSkill, CvLanguage, CvInterest


class Viadeo():

    client_id       = "2f3af038b75b07a280e24f89255cda4a"
    client_secret   = "01c2b729a04485cd3cb86afd84cd781dc6dfb769"
    redirect_uri    = "https://www.pitchmyjob.com/sn/viadeo-return"
    datas           = []

    def get_url(self):
        return "https://partners.viadeo.com/oauth/authorize?client_id=%s&redirect_uri=%s&response_type=code&scope=api" % (self.client_id, self.redirect_uri)

    def set_code(self, code):
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
            "code": code,
            "scope": "api"
        }
        r = requests.post(
            url="https://partners.viadeo.com/oauth/token",
            data=payload
        )
        res = json.loads(r.text)
        self.access_token = res['access_token']

    def get_full_user(self):
        self.user = self.http_requests("https://partners.viadeo.com/api/member/account/userinfo")
        return self.user

    def get_account(self):
        return self.http_requests("https://partners.viadeo.com/api/member/profile/full")

    def http_requests(self, url):
        print ("-----------------------------------------")
        print ("-----------------------------------------")
        print ("-----------------------------------------")
        print( self.access_token )
        r = requests.get(
            url=url,
            headers={
                "Accept": "application/json",
                "Authorization": " Bearer %s" % self.access_token
            }
        )
        return json.loads(r.text)

    def get_city(self):
        if 'geoLocalisation' in self.user['data']:
            geo = self.user['data']['geoLocalisation']
            url = "http://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&sensor=true" % (geo['lat'], geo['lon'])
            r = requests.get(url=url)
            datas = json.loads(r.text)

            if datas['status'] == "OK":
                results = datas['results'][0]
                gps = {'lat': results['geometry']['location']['lat']}
                gps['lng'] = results['geometry']['location']['lng']
                gps['address'] = results['formatted_address']

                for data in results['address_components']:
                    gps[data['types'][0]] = data['long_name']

                return gps
            return None
        else:
            return None

    def language(self, lang):
        if "spa":
            return "Espagnol"
        if "eng":
            return "Anglais"
        return lang

    def import_datas(self, member, cv):
        a = self.get_account()

        CvExperience.objects.filter(cv=cv).delete()
        CvFormation.objects.filter(cv=cv).delete()
        CvInterest.objects.filter(cv=cv).delete()
        CvLanguage.objects.filter(cv=cv).delete()
        CvSkill.objects.filter(cv=cv).delete()
        
        data = a['data']

        userinfo = self.user if self.user else self.get_full_user()

        if 'avatarUrl' in userinfo['data']:
            lien = userinfo['data']['avatarUrl'].replace('https', 'http')
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urllib2.urlopen(lien).read())
            img_temp.flush()
            member.image.save(str(member.id) + ".jpg", File(img_temp))

            try:
                os.chmod(settings.MEDIA_ROOT + "c2v/" + str(member.id), 0777)
                os.chmod(member.image.path, 0777)
            except:
                pass


        if 'headline' in data :
            cv.poste = data['headline']

        if 'profileUrl' in data:
            cv.site = data['profileUrl']

        gps = self.get_city()
        if gps :
            cv.city = gps['locality']
            cv.country = gps['country']

        cv.save()

        if 'positions' in data :
            for position in data['positions'] :
                cvExp = CvExperience(cv=cv, company=position['companyName'], title=position['positionTitle'], description=position['description'])
                try:
                    date_start = datetime.datetime.strptime(position['startDate'], "%m/%Y")
                    cvExp.date_start = date_start
                except:
                    try:
                        date_start = datetime.datetime.strptime(position['startDate'][-4:], "%Y")
                        cvExp.date_start = date_start
                    except:
                        pass

                try:
                    date_end = datetime.datetime.strptime(position['endDate'], "%m/%Y")
                    cvExp.date_end = date_end
                except:
                    try:
                        date_end = datetime.datetime.strptime(position['endDate'][-4:], "%Y")
                        cvExp.date_end = date_end
                    except:
                        pass
                cvExp.save()

        if 'educations' in data :
            for education in data['educations']:
                cvEduc = CvFormation(cv=cv, school=education['schoolName'], degree=education['diplomaTitle'])
                try:
                    date_start = datetime.datetime.strptime(str(education['startYear']), "%Y")
                    cvEduc.date_start = date_start
                except:
                    pass

                try:
                    date_end = datetime.datetime.strptime(str(education['endYear']), "%Y")
                    cvEduc.date_end = date_end
                except:
                    pass
                cvEduc.save()

        if 'skills' in data :
            for skill in data['skills']:
                cvSkill = CvSkill(cv=cv, name=skill['skill'])
                cvSkill.save()
                try :
                    cvSkill.level = skill['level']
                    cvSkill.save()
                except:
                    pass

        if 'spokenLanguages' in data :
            for lang in data['spokenLanguages']:
                cvLang = CvLanguage(cv=cv, name=lang['language'])
                cvLang.save()
                try:
                    cvLang.level = lang['level']
                    cvLang.save()
                except:
                    pass

        if 'hobbies' in data:
            for hobbie in data['hobbies']:
                CvInterest(cv=cv, name=hobbie).save()

        member.save_on_elasticsearch()