import urllib2, datetime
from bs4 import BeautifulSoup
from notifications.scraper import Scraper
from members.models import Member, Study, Experience
from pro.models import Pro, Job, Contract, JobQuestion, Tag
from django.contrib.auth.models import User, Group
from django.template.defaultfilters import slugify
from pro.multiposteur.multiposteur import Multiposteur
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File

class Flatchr(Multiposteur):
    url="http://xml.flatchr.io/8vq1xlpR24p6zEM0"

    def __init__(self):
        self.parse()

    def parse(self):
        f = urllib2.urlopen(self.url)
        xml = BeautifulSoup(f, 'html.parser')

        for item in xml.find_all('job'):

            current = {}

            # job ----------
            current['description'] = item.find('description').get_text()
            current['title'] = item.find('title').get_text()

            current['referencenumber'] = item.find('referencenumber').get_text()
            current['date'] = item.find('date').get_text()
            current['url'] = item.find('url').get_text()

            current['city'] = item.find('city').get_text()
            current['country'] = item.find('country').get_text()

            current['description'] = item.find('description').get_text()
            current['experience'] = item.find('experience').get_text()

            current['contract_type'] = item.find('contract_type').get_text()
            current['jobtype'] = item.find('jobtype').get_text()

            current['company_logo'] = None

            if item.find('company_logo'):
                current['company_logo'] = item.find('company_logo').get_text()

            # for qt in job.find_all('questions'):
            #current['question'] = item.find('questions').get_text().split("-")

            # pro ----------
            current['company'] = item.find('company').get_text()
            current['recruiter_email'] = item.find('recruiter_email').get_text()
            

            if Job.objects.filter(mp_flatchr_ref=current['referencenumber'], mp_type="flatchr").exists():
                continue
                #Job.objects.filter(mp_flatchr_ref=current['referencenumber'], mp_type="flatchr").delete()

            pro = Pro.objects.get(id=1112)


            job = Job(pro=pro, mp=True, image="pro/default.jpg", mp_type="flatchr", mp_flatchr_ref=current['referencenumber'], is_video=True, active=True, paid=True, complet=True, date_posted=datetime.datetime.now())
            job.description = current['description']
            job.profile = current['experience']
            job.company = current['company']
            job.job_title = current['title']
            
            contract_type = None

            if current['contract_type'] == "Stage":
                contract_type = Contract.objects.get(id=3)

            if current['contract_type'] == "CDD":
                contract_type = Contract.objects.get(id=2)

            if current['contract_type'] == "CDI":
                contract_type = Contract.objects.get(id=1)

            if current['contract_type'] == "Alternance":
                contract_type = Contract.objects.get(id=5)


            job.save()

            if contract_type:
                job.contracts.add(contract_type.id)

            # job.studies.add(education_level)
            # job.experiences.add(work_experience)
            # job.contracts.add(contract_type)

            location = "%s %s" % (current['city'], current['country'])
            geoloc = Scraper()
            job_location = geoloc.get_gps_coordonnate(location)

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

            job_qt = JobQuestion(question="question test 1", nb=1, job=job).save()
            job_qt = JobQuestion(question="question test 2", nb=2, job=job).save()

            if current['company_logo'] :
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(urllib2.urlopen(current['company_logo']).read())
                job.image.save(str(job.id) + ".jpeg", File(img_temp))

                try:
                    import os
                    os.chmod(settings.MEDIA_ROOT + "job/" + str(job.id), 0777)
                    os.chmod(pro.image.path, 0777)
                except:
                    pass


            #i = 1
            #for q in current['question']:
                #job_qt = JobQuestion(question=q, nb=i, job=job)
                # job_qt.save()
                #i = i + 1