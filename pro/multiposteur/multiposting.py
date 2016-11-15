import urllib2
from bs4 import BeautifulSoup
from notifications.scraper import Scraper
from members.models import Member, Study, Experience
from pro.models import Pro, Job, Contract, JobQuestion
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify


class Multiposting(object):
    url="http://jobs.contactrh.com/get/MfnjeC4itVFf8dJq"
    #url="http://www.pitchmyjob.com:1010/static/MfnjeC4itVFf8dJq.xml"

    def __init__(self):
        self.parse()

    def parse(self):
        f = urllib2.urlopen("http://jobs.contactrh.com/get/MfnjeC4itVFf8dJq")
        xml = BeautifulSoup(f, 'html.parser')

        for item in xml.find_all('job'):

            current = {}

            # job ----------
            current['description'] = item.find('company_description').get_text()
            current['title'] = item.find('title').get_text()
            current['reference'] = item.find('reference').get_text()
            current['job_description'] = item.find('job_description').get_text()
            current['profile_description'] = item.find('profile_description').get_text()
            current['education_level'] = int(item.find('education_level').get('id'))
            current['work_experience'] = int(item.find('work_experience').get('id'))
            current['contract_type'] = int(item.find('contract_type').get('id'))
            current['function'] = item.find('function').get('id')
            current['sub_function'] = item.find('sub_function').get('id')

            current['sector'] = item.find('sector').get('id')
            current['sub_sector'] = item.find('sub_sector').get('id')
            current['id'] = item.find('id').get_text()

            current['location_country'] = item.find('country').get_text()
            current['location_name'] = item.find('name').get_text()
            current['location_postal_code'] = item.find('postal_code').get_text()

            # for qt in job.find_all('questions'):
            current['question'] = item.find('questions').get_text().split("-")

            # pro ----------
            current['company_description'] = item.find('company_description').get_text()
            current['company_name'] = item.find('company_name').get_text()
            current['application_email'] = item.find('application_email').get_text()
            current['id_client'] = item.find('id_client').get_text()

            if Job.objects.filter(mp_multiposting_id=current['id'], mp_type="multiposting").exists():
                print "pass"
                continue

            pro = Pro.objects.filter(mp_multiposting_id=current['id_client'], mp_type="multiposting")
            if pro.exists():
                pro = pro.first()
            else:
                username = slugify(current['company_name'])
                # user = User.objects.create_user(username, None, "cvG456hz")
                # user.save()

                pro = Pro(mp=True, mp_type="multiposting", mp_multiposting_id=current['id_client'], company=current['company_name'], description=current['company_description'])
                # pro.user=user
                # pro.save()

            job = Job(pro=pro, mp=True, mp_type="multiposting", mp_multiposting_id=current['id'], mp_multiposting_ref=current['reference'], mp_email=current['application_email'])
            job.description = current['job_description']
            job.profile = current['profile_description']
            job.company = current['company_name']
            job.job_title = current['title']

            if current['education_level'] == 1:
                education_level = Study.objects.get(id=5)  # No diploma

            if current['education_level'] in (2, 3, 10):
                education_level = Study.objects.get(id=6)  # CAP BEP

            if current['education_level'] in (5, 4):
                education_level = Study.objects.get(id=8)  # Bac

            if current['education_level'] == 6:
                education_level = Study.objects.get(id=9)  # BTS

            if current['education_level'] == 7:
                education_level = Study.objects.get(id=10)  # Bachelor

            if current['education_level'] == 8:
                education_level = Study.objects.get(id=12)  # Master 2

            if current['education_level'] == 9:
                education_level = Study.objects.get(id=13)  # Master 2

            if current['work_experience'] in (1, 2, 3):
                work_experience = Experience.objects.filter(id=2)

            if current['work_experience'] in (4, 5, 6):
                work_experience = Experience.objects.filter(id=3)

            if current['work_experience'] in (7, 8, 9, 10):
                work_experience = Experience.objects.filter(id=1)

            if current['contract_type'] in (1, 6):
                contract_type = Contract.objects.filter(id=1)

            if current['contract_type'] == 2:
                contract_type = Contract.objects.filter(id=2)

            if current['contract_type'] in (3, 8):
                contract_type = Contract.objects.filter(id=3)

            if current['contract_type'] == 4:
                contract_type = Contract.objects.filter(id=4)

            if current['contract_type'] == 5:
                contract_type = Contract.objects.filter(id=6)

            if current['contract_type'] == 7:
                contract_type = Contract.objects.filter(id=5)

            if current['contract_type'] == 9:
                contract_type = Contract.objects.filter(id=2)

            # job.save()

            # job.studies.add(education_level)
            # job.experiences.add(work_experience)
            # job.contracts.add(contract_type)

            geoloc = Scraper()
            job_location = geoloc.get_gps_coordonnate(current['location_name'])

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

            print job.longitude
            print contract_type
            print work_experience

            # job.save()

            i = 1
            for q in current['question']:
                job_qt = JobQuestion(question=q, nb=i, job=job)
                # job_qt.save()
                i = i + 1