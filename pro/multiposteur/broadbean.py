import urllib2, datetime
from bs4 import BeautifulSoup
from notifications.scraper import Scraper
from members.models import Member, Study, Experience
from pro.models import Pro, Job, Contract, JobQuestion, Tag
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import slugify
from pro.multiposteur.multiposteur import Multiposteur

class Broadbean(Multiposteur):
    #url="http://batch.dev.aws.adcourier.com/services/?q=U2FsdGVkX1_0BeLfTykYFY--aP05wqxKGndCQdnASrGtXWoDaCplotrx_t-Kx-qu"
    url="https://batchaws.adcourier.com/services/?q=U2FsdGVkX1809hvEWNpqXCopzm4bhYS5BpRR7NP8ivxppRmvpq9TvudvoZCBGtFK"

    def __init__(self):
        self.parse()

    def parse(self):

        f = urllib2.urlopen(self.url)
        xml = BeautifulSoup(f, 'html.parser')

        for item in xml.find_all('job'):

            command = item.find('command').get_text()

            if command == "add" or command=="edit":
                user = User.objects.filter(username=item.find('username').get_text())
                if user.exists():
                    user = user.first()
                    pro = user.pro
                else:
                    user = User.objects.create_user(item.find('username').get_text(),password=item.find('password').get_text())
                    user.groups.add(Group.objects.get(name='pro'))
                    user.save()
                    pro = Pro(user=user, mp=True, mp_type="broadbean")
                    if item.find('company_name').get_text():
                        pro.company = item.find('company_name').get_text()
                    if item.find('company_description').get_text():
                        pro.description = item.find('company_description').get_text()
                    if item.find('company_first_name').get_text():
                        pro.first_name = item.find('company_first_name').get_text()
                    if item.find('company_last_name').get_text():
                        pro.last_name = item.find('company_last_name').get_text()
                    if item.find('company_email').get_text():
                        pro.email = item.find('company_email').get_text()
                    if item.find('company_web_site').get_text():
                        pro.web_site = item.find('company_web_site').get_text()
                    if item.find('company_employees').get_text():
                        pro.employes = self.get_employees(item.find('company_employees').get_text())
                    if item.find('company_facebook').get_text():
                        pro.link_facebook = item.find('company_facebook').get_text()
                    if item.find('company_twitter').get_text():
                        pro.link_twitter = item.find('company_twitter').get_text()
                    if item.find('company_youtube').get_text():
                        pro.link_youtube = item.find('company_youtube').get_text()

                    pro.save()

                if not Job.objects.filter(mp_broadbean_id=item.find('job_id').get_text()).exists() :
                    job = Job(pro=pro, mp=True, mp_type="broadbean", is_video=True, active=True, complet=True, paid=True, date_posted=datetime.datetime.now(), image=pro.image)

                    if item.find('application_email').get_text():
                        job.mp_email = item.find('application_email').get_text()

                    if item.find('job_reference').get_text():
                        job.mp_broadbean_ref = item.find('job_reference').get_text()
                    if item.find('job_title').get_text():
                        job.job_title = item.find('job_title').get_text()

                    if item.find('job_company').get_text():
                        job.company = item.find('job_company').get_text()
                    else:
                        job.company = pro.company

                    # if item.find('job_time').get_text():
                    # if item.find('job_time').get_text() == "1":

                    if item.find('job_id').get_text():
                        job.mp_broadbean_id = item.find('job_id').get_text()

                    if item.find('job_description').get_text():
                        job.description = item.find('job_description').get_text()

                    if item.find('job_location').get_text():
                        geoloc = Scraper()
                        job_location = geoloc.get_gps_coordonnate(item.find('job_location').get_text())

                        if job_location:
                            if 'country' in job_location:
                                job.country = job_location['country']
                            if 'administrative_area_level_1' in job_location:
                                job.administrative_area_level_1 = job_location['administrative_area_level_1']
                            if 'administrative_area_level_2' in job_location:
                                job.administrative_area_level_2 = job_location['administrative_area_level_2']
                            if 'locality' in job_location:
                                job.locality = job_location['locality']
                            if 'postal_code' in job_location:
                                job.cp = job_location['postal_code']
                            if 'route' in job_location:
                                job.route = job_location['route']
                            if 'street_number' in job_location:
                                job.street_number = job_location['street_number']
                            if 'lat' in job_location:
                                job.latitude = job_location['lat']
                            if 'lng' in job_location:
                                job.longitude = job_location['lng']
                            if 'address' in job_location:
                                job.job_location = job_location['address']

                    job.save()

                    job.contract_time.add(1)

                    if item.find('job_contract').get_text():
                        if item.find('job_contract').get_text() == "Permanent":
                            job.contracts.add(1)

                    if item.find('job_study').get_text():
                        # study = Study.objects.get(id=study)
                        # study = Study.objects.get(id=1)
                        job.studies.add(item.find('job_study').get_text())

                    if item.find('job_experience').get_text():
                        # experience = Experience.objects.filter(id=item.find('job_experience').get_text())
                        job.experiences.add(item.find('job_experience').get_text())

                    if item.find('job_skills').get_text():
                        for kw in item.find('job_skills').get_text().split(','):
                            try:
                                kw_object, created = Tag.objects.get_or_create(name__iexact=kw, defaults={'name': kw})
                                job.tags.add(kw_object)
                            except:
                                kw_object = Tag.objects.filter(name__icontains=kw)
                                if kw_object.exists():
                                    job.tags.add(kw_object.first())

                    for q in item.find_all('question'):
                        job_qt = JobQuestion(question=q.find('text').get_text(), nb=q.find('nb').get_text(), job=job)
                        job_qt.save()