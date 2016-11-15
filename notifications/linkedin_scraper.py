#-*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.mail import send_mail
import random
import re
import urllib2
import requests, json

from bs4 import BeautifulSoup
from bs4.element import Tag


class LinkedInScraper(object):
    """ Allow to parse public LinkedIn profile and retrieve data """
    bs=""
    data = {}
    dash = '\u2013'
    proficiency = [
            'Notions', 'Compétence professionnelle limitée', 'Compétence professionnelle',
            'Capacité professionnelle complète', 'Bilingue ou langue natale'
        ]
    months = [
            'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
            'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
        ]
    break_line_replace = '\n'

    def __init__(self, url=None, pk=None):
        # Initializing fake browser to bypass LinkedIn security

        if url and pk :
            script = ['http://163.172.28.221:1010/']
            status = 000
            error = 0

            rand = random.randint(0, 1)
            url_scrip = "http://163.172.28.221:1010/"

            try:
                #r = requests.post(
                #    url=url_scrip,
                #    data={'url': url}
                #)
                #result = json.loads(r.text)
                #status = int(result['status'])
                #text = result['text']

                headers = {
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'accept-encoding': 'gzip, deflate, sdch',
                    'accept-language': 'fr-FR,fr;q=0.8,en-US;q=0.6,en;q=0.4',
                    'cache-control': 'max-age=0',
                    'cookie': 'bcookie="v=2&846f2946-b624-42d5-8057-2f9b02d74609"; visit="v=1&M"; VID=V_2015_12_22_16_2725; __utma=23068709.527562309.1447081330.1455139452.1455139452.1; __utmv=23068709.user; _ga=GA1.2.527562309.1447081330; _chartbeat2=uRTH1DQd9_ADN-lz8.1454966640093.1468872141326.0000000000101001; bscookie="v=1&2016091417181308945c43-ad49-4f36-87d1-7a8a2f09b2bdAQH9BvsQmAtviTr0hJ45a-24HvcnTghE"; wutan=nBLFB1dS8RkkjqdQnNVvZDBVGbVpWbXYzHJeUGgUs0k=; _leo_profile=""; li_at=AQEDAQ6IWLEBD1qoAAABV9NW-dsAAAFYQ8kuyk4AjJn6BaUqViRR9gt5Ggrk-DAiYH7HejGeA8hUQFdivr7d_w_sye0ic2AkjQpMCspKSHn703HYTo_8Mq8bvp4kFu6tU9VVsHvd9b8xzbrl83xnNO3Z; liap=true; sl="v=1&7itfH"; JSESSIONID="ajax:7624205693307475458"; oz_props_fetch_size1_243816625=2; share_setting=PUBLIC; sdsc=1%3A1SZM1shxDNbLt36wZwCgPgvN58iw%3D; lidc="b=VB25:g=748:u=77:i=1478603305:t=1478682944:s=AQHXCJAx_Nz86zsEdki_YtnzuYr2H4cC"; RT=s=1478603878125&r=https%3A%2F%2Fwww.linkedin.com%2Fin%2Frutaremutyte; _lipt=0_b3SvrmYfvRva3BledZduGwg7Bx-_tmWyTQD9mGF8x-TW3zxW6lkJPMNhu5ojAVSDbOA7f3kgx8OBXy_6kbI71wZ4rj7XDT3iLbxOK6bmlnq09Jt1kx6pQeOSqXGDoSGvNOgTBqsddUf1Wl1LpG8vVH7RORcn6JjqqCucZ9cIUvTyfqMmgC9eyINP7iBy1Nz5yyt3WzHQFj_YFJaszaFjtEhkgUkO33-5xXNdgB76Qiz9O1lpn54CpdQsp5T4cMuoLUCMnlGP8n29w0MLqySB7x5hKzgthTaCJ_N4QbapYa2p_5gSw8vAs-uRzKCSF1vsCj0HUtLl2xnVeDT0RHHYdzbiag-g5MkTrgsF7q4tFCJ; lang="v=2&lang=fr-fr"',
                    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
                    'upgrade-insecure-requests': 1,
                    'Connection': 'keep-alive'
                }

                r = requests.request("GET", url, headers=headers)

                status = int(r.status_code)
                text = r.text

            except Exception:
                status=500
                body = 'Erreur sur script N°%s %s ' % (str(rand), url_scrip)
                send_mail('Linkedin error server', body, 'no-reply@pitchmyjob.com', ['no-reply@pitchmyjob.com'], fail_silently=True)
                error = error + 1


            if status != 200:
                message = "url linkedin : %s" % (url)
                send_mail('Erreur sur script N°%s %s ' % (str(rand), url_scrip), message, 'no-reply@pitchmyjob.com', ['no-reply@pitchmyjob.com'], fail_silently=True)
            else:
                self.bs=BeautifulSoup(text, 'html.parser')
                self.parse()
            error = error + 1

            if error == 10:
                body = "lien : %s / ID : %s\nimport manuel : https://www.pitchmyjob.com/cv/linkedin " % (url, str(pk))
                send_mail('Linkedin FATAL ERROR', body, 'no-reply@pitchmyjob.com', ['no-reply@pitchmyjob.com'],fail_silently=True)

        # Getting data

    def set_html(self, html):
        self.bs = BeautifulSoup(html, 'html.parser')

    def parse(self):
        """ Parse LinkedIn profile """
        self.parse_user()
        self.parse_summary()
        self.parse_experiences()
        self.parse_education()
        self.parse_skills()
        self.parse_languages()
        self.parse_interests()

    def parse_user(self):
        """ Parse user """
        self.data['user'] = {
            'name': None,
            'title': None,
            'address': None,
        }

        bs_topcard = self.bs.find(id='top-card')

        if bs_topcard:
            bs_name = bs_topcard.find(class_='full-name')
            if bs_name:
                self.data['user']['name'] = bs_name.get_text()

            bs_title = bs_topcard.find(class_='title')
            if bs_title:
                self.data['user']['title'] = bs_title.get_text()

            bs_demographics = bs_topcard.find(id='demographics')
            if bs_demographics:
                bs_address = bs_topcard.find(class_='locality')
                if bs_address:
                    self.data['user']['address'] = bs_address.get_text()
            bs_image = bs_topcard.find(class_='profile-picture')
            if bs_image:
                bs_image = bs_image.find('img')
                self.data['user']['img'] = bs_image['src']

    def parse_summary(self):
        """ Parse summary """
        self.data['summary'] = None

        bs_summary = self.bs.find(id='background-summary')
        if bs_summary:
            bs_summary = bs_summary.find(class_='summary').find('p')
            #self.data['summary'] = self._get_text_with_break_lines(bs_summary)

    def parse_experiences(self):
        """ Parse experiences """
        self.data['experiences'] = []

        bs_experiences = self.bs.find(id='background-experience-container')
        if bs_experiences:
            for bs_experience in bs_experiences.find_all(class_='section-item'):
                experience = {
                    'title': None,
                    'company': None,
                    'company_logo': None,
                    'date_range': None,
                    'description': None,
                    'location':None,
                }

                bs_experience_title = bs_experience.find('h4')
                bs_experience_company = bs_experience.find_all('h5')
                bs_experience_company_logo = bs_experience.find(class_='experience-logo')
                bs_experience_date_range = bs_experience.find(class_='experience-date-locale')
                bs_experience_description = bs_experience.find(class_='description')
                bs_experience_location = bs_experience.find(class_='locality')

                if bs_experience_title:
                    experience['title'] = bs_experience_title.get_text()

                if bs_experience_company:
                    if len(bs_experience_company) > 1 :
                        exp = bs_experience_company[1]
                    else:
                        exp = bs_experience_company[0]
                    experience['company'] = exp.get_text()

                if bs_experience_company_logo:
                    if bs_experience_company_logo.find('img') :
                        experience['company_logo'] = bs_experience_company_logo.find('img')['src']

                if bs_experience_date_range:
                    experience['date_range'] = self._parse_date_range(bs_experience_date_range.get_text())

                if bs_experience_description:
                    experience['description'] = self._get_text_with_break_lines(bs_experience_description)

                if bs_experience_location:
                    experience['location'] = bs_experience_location.get_text()

                self.data['experiences'].append(experience)

    def parse_education(self):
        """ Parse education """
        self.data['education'] = []

        bs_education = self.bs.find(id='background-education-container')
        if bs_education:
            for bs_school in bs_education.find_all(class_='section-item'):
                school = {
                    'school': None,
                    'diploma': None,
                    'date_range': None,
                    'description': None,
                    'logo' : None,
                } 

                bs_school_school = bs_school.find(class_='summary')
                bs_school_diploma = bs_school.find(class_='degree')
                bs_school_date_range = bs_school.find(class_='education-date')
                bs_school_description = bs_school.find(class_='description')
                bs_school_logo = bs_school.find(class_='new-miniprofile-container')

                if bs_school_school:
                    school['school'] = bs_school_school.get_text()

                if bs_school_diploma:
                    school['diploma'] = bs_school_diploma.get_text()

                if bs_school_date_range:
                    school['date_range'] = self._parse_date_range(bs_school_date_range.get_text())

                if bs_school_description:
                    bs_school_description = bs_school_description.find('p')
                    school['description'] = self._get_text_with_break_lines(bs_school_description)

                if bs_school_logo:
                    if bs_school_logo.find('img'):
                        school['logo'] = bs_school_logo.find('img')['src']

                self.data['education'].append(school)

    def parse_skills(self):
        """ Parse skills """
        self.data['skills'] = []

        bs_skills = self.bs.find(id='background-skills-container')
        if bs_skills:
            for bs_skill in bs_skills.find_all(class_='endorse-item-name'):
                self.data['skills'].append(bs_skill.get_text())

    def parse_languages(self):
        """ Parse languages """
        self.data['languages'] = []

        bs_languages = self.bs.find(id='background-languages-container')
        if bs_languages:
            for bs_language in bs_languages.find_all(class_='section-item'):
                language = {
                    'name': None,
                    'proficiency': None,
                }

                bs_language_name = bs_language.find('h4')
                bs_language_proficiency = bs_language.find(class_='languages-proficiency')

                if bs_language_name:
                    language['name'] = bs_language_name.get_text()

                if bs_language_proficiency and bs_language_proficiency.get_text():
                    language['proficiency'] = self._parse_proficiency(bs_language_proficiency.get_text())

                self.data['languages'].append(language)

    def parse_interests(self):
        """ Parse interests """
        self.data['interests'] = []

        bs_interests = self.bs.find(class_='interests-listing')
        if bs_interests:
            for bs_skill in bs_interests.find_all('li'):
                self.data['interests'].append(bs_skill.get_text())

    def _get_text_with_break_lines(self, bs_tag):
        text = ''
        for tag in bs_tag.recursiveChildGenerator():
            if isinstance(tag, Tag) and tag.name in ('br'):
                text += self.break_line_replace
            else:
                text += tag
        return text

    def _parse_proficiency(self, proficiency):
        """ Return the language level """
        proficiency = self.proficiency.index(proficiency)
        return None if proficiency == -1 else proficiency

    def _parse_date_range(self, date_range):
        """ Return the start and end date well formatted and handle the current option """
        if date_range.find(self.dash) != -1:
            current = date_range.find('Aujourd') != -1
            dates = date_range.split(self.dash)

            return {
                'start': self._parse_date(dates[0]),
                'end': False if current else self._parse_date(dates[1]),
                'current': current,
            }
        else:
            return {
                'start': False,
                'end': self._parse_date(date_range),
                'current': False,
            }

    def _parse_date(self, date):
        """ Return the date according to the number of elements """
        parenthesis_position = date.find('(')
        if parenthesis_position != -1:
            date = date[:parenthesis_position]

        date = date.strip().split(' ')

        if len(date) >= 2:
            return {
                'month': self.months.index(date[0].strip()) + 1,
                'year': date[1].strip(),
            }
        elif len(date) == 1:
            return {
                'year': date[0].strip(),
            }

    def _encode_url(self, url):
        if url.find('https://') != -1:
            url = url[8:]
        elif url.find('http://') != -1:
            url = url[7:]
        return 'https://%s' % urllib2.quote(url.encode('utf-8'))







class LinkedInScraperOLD(object):
    """ Allow to parse public LinkedIn profile and retrieve data """
    bs = ""
    data = {}
    dash = '\u2013'
    proficiency = [
        'Notions', 'Compétence professionnelle limitée', 'Compétence professionnelle',
        'Capacité professionnelle complète', 'Bilingue ou langue natale'
    ]
    months = [
        'janvier', 'février', 'mars', 'avril', 'mai', 'juin',
        'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre',
    ]
    break_line_replace = '\n'

    def __init__(self, url=None, pk=None):
        # Initializing fake browser to bypass LinkedIn security

        if url and pk:
            script = ['http://163.172.28.221:1010/', 'http://163.172.145.207']
            status = 000
            error = 0

            while status != 200:
                rand = random.randint(0, 1)
                url_scrip = script[rand]
                # url_scrip = "http://163.172.28.221:1010"

                try:
                    r = requests.post(
                        url=url_scrip,
                        data={'url': url}
                    )
                    result = json.loads(r.text)
                    status = int(result['status'])
                    text = result['text']
                except Exception:
                    status = 500
                    body = 'Erreur sur script N°%s %s ' % (str(rand), url_scrip)
                    # send_mail('Linkedin error server', body, 'no-reply@pitchmyjob.com', ['no-reply@pitchmyjob.com'], fail_silently=True)

                if status != 200:
                    message = "url linkedin : %s" % (url)
                    # send_mail('Erreur sur script N°%s %s ' % (str(rand), url_scrip), message, 'no-reply@pitchmyjob.com', ['no-reply@pitchmyjob.com'], fail_silently=True)
                else:
                    self.bs = BeautifulSoup(text, 'html.parser')
                    self.parse()
                error = error + 1

                if error == 10:
                    body = "lien : %s / ID : %s\nimport manuel : https://www.pitchmyjob.com/cv/linkedin " % (
                    url, str(pk))
                    # send_mail('Linkedin FATAL ERROR', body, 'no-reply@pitchmyjob.com', ['no-reply@pitchmyjob.com'],fail_silently=True)

                    break

                    # Getting data

    def set_html(self, html):
        self.bs = BeautifulSoup(html, 'html.parser')

    def parse(self):
        """ Parse LinkedIn profile """
        self.parse_user()
        self.parse_summary()
        self.parse_experiences()
        self.parse_education()
        self.parse_skills()
        self.parse_languages()
        self.parse_interests()

    def parse_user(self):
        """ Parse user """
        self.data['user'] = {
            'name': None,
            'title': None,
            'address': None,
        }

        bs_topcard = self.bs.find(id='topcard')

        if bs_topcard:
            bs_name = bs_topcard.find(id='name')
            if bs_name:
                self.data['user']['name'] = bs_name.get_text()

            bs_title = bs_topcard.find(class_='headline title')
            if bs_title:
                self.data['user']['title'] = bs_title.get_text()

            bs_demographics = bs_topcard.find(id='demographics')
            if bs_demographics:
                bs_address = bs_topcard.find(class_='locality')
                if bs_address:
                    self.data['user']['address'] = bs_address.get_text()
            bs_image = bs_topcard.find(class_='photo')
            if bs_image:
                self.data['user']['img'] = bs_image.attrs['data-delayed-url']

    def parse_summary(self):
        """ Parse summary """
        self.data['summary'] = None

        bs_summary = self.bs.find(id='summary')
        if bs_summary:
            bs_summary = bs_summary.find(class_='description').find('p')
            self.data['summary'] = self._get_text_with_break_lines(bs_summary)

    def parse_experiences(self):
        """ Parse experiences """
        self.data['experiences'] = []

        bs_experiences = self.bs.find(id='experience')
        if bs_experiences:
            for bs_experience in bs_experiences.find_all(class_='position'):
                experience = {
                    'title': None,
                    'company': None,
                    'company_logo': None,
                    'date_range': None,
                    'description': None,
                    'location': None,
                }

                bs_experience_title = bs_experience.find(class_='item-title')
                bs_experience_company = bs_experience.find(class_='item-subtitle')
                bs_experience_company_logo = bs_experience.find(class_='logo')
                bs_experience_date_range = bs_experience.find(class_='date-range')
                bs_experience_description = bs_experience.find(class_='description')
                bs_experience_location = bs_experience.find(class_='location')

                if bs_experience_title:
                    experience['title'] = bs_experience_title.get_text()

                if bs_experience_company:
                    experience['company'] = bs_experience_company.get_text()

                if bs_experience_company_logo:
                    experience['company_logo'] = bs_experience_company_logo.find('img').get('data-delayed-url')

                if bs_experience_date_range:
                    experience['date_range'] = self._parse_date_range(bs_experience_date_range.get_text())

                if bs_experience_description:
                    experience['description'] = self._get_text_with_break_lines(bs_experience_description)

                if bs_experience_location:
                    experience['location'] = bs_experience_location.get_text()

                self.data['experiences'].append(experience)

    def parse_education(self):
        """ Parse education """
        self.data['education'] = []

        bs_education = self.bs.find(id='education')
        if bs_education:
            for bs_school in bs_education.find_all(class_='school'):
                school = {
                    'school': None,
                    'diploma': None,
                    'date_range': None,
                    'description': None,
                    'logo': None,
                }

                bs_school_school = bs_school.find(class_='item-title')
                bs_school_diploma = bs_school.find(class_='item-subtitle')
                bs_school_date_range = bs_school.find(class_='date-range')
                bs_school_description = bs_school.find(class_='description')
                bs_school_logo = bs_school.find(class_='logo')

                if bs_school_school:
                    school['school'] = bs_school_school.get_text()

                if bs_school_diploma:
                    school['diploma'] = bs_school_diploma.get_text()

                if bs_school_date_range:
                    school['date_range'] = self._parse_date_range(bs_school_date_range.get_text())

                if bs_school_description:
                    bs_school_description = bs_school_description.find('p')
                    school['description'] = self._get_text_with_break_lines(bs_school_description)

                if bs_school_logo:
                    school['logo'] = bs_school_logo.find('img').get('data-delayed-url')

                self.data['education'].append(school)

    def parse_skills(self):
        """ Parse skills """
        self.data['skills'] = []

        bs_skills = self.bs.find(id='skills')
        if bs_skills:
            for bs_skill in bs_skills.find_all(class_='skill'):
                self.data['skills'].append(bs_skill.get_text())

    def parse_languages(self):
        """ Parse languages """
        self.data['languages'] = []

        bs_languages = self.bs.find(id='languages')
        if bs_languages:
            for bs_language in bs_languages.find_all(class_='language'):
                language = {
                    'name': None,
                    'proficiency': None,
                }

                bs_language_name = bs_language.find(class_='name')
                bs_language_proficiency = bs_language.find(class_='proficiency')

                if bs_language_name:
                    language['name'] = bs_language_name.get_text()

                if bs_language_proficiency and bs_language_proficiency.get_text():
                    language['proficiency'] = self._parse_proficiency(bs_language_proficiency.get_text())

                self.data['languages'].append(language)

    def parse_interests(self):
        """ Parse interests """
        self.data['interests'] = []

        bs_interests = self.bs.find(id='interests')
        if bs_interests:
            for bs_skill in bs_interests.find_all(class_='interest'):
                self.data['interests'].append(bs_skill.get_text())

    def _get_text_with_break_lines(self, bs_tag):
        text = ''
        for tag in bs_tag.recursiveChildGenerator():
            if isinstance(tag, Tag) and tag.name in ('br'):
                text += self.break_line_replace
            else:
                text += tag
        return text

    def _parse_proficiency(self, proficiency):
        """ Return the language level """
        proficiency = self.proficiency.index(proficiency)
        return None if proficiency == -1 else proficiency

    def _parse_date_range(self, date_range):
        """ Return the start and end date well formatted and handle the current option """
        if date_range.find(self.dash) != -1:
            current = date_range.find('Aujourd') != -1
            dates = date_range.split(self.dash)

            return {
                'start': self._parse_date(dates[0]),
                'end': False if current else self._parse_date(dates[1]),
                'current': current,
            }
        else:
            return {
                'start': False,
                'end': self._parse_date(date_range),
                'current': False,
            }

    def _parse_date(self, date):
        """ Return the date according to the number of elements """
        parenthesis_position = date.find('(')
        if parenthesis_position != -1:
            date = date[:parenthesis_position]

        date = date.strip().split(' ')

        if len(date) >= 2:
            return {
                'month': self.months.index(date[0].strip()) + 1,
                'year': date[1].strip(),
            }
        elif len(date) == 1:
            return {
                'year': date[0].strip(),
            }

    def _encode_url(self, url):
        if url.find('https://') != -1:
            url = url[8:]
        elif url.find('http://') != -1:
            url = url[7:]
        return 'https://%s' % urllib2.quote(url.encode('utf-8'))


# Sample
# mr = LinkedInScraper('https://www.linkedin.com/in/christophe-lim-75655689')
# print mr.data


"""
How data are saved

# Data
{
    'user': {
        'name': None,
        'title': None,
        'address': None,
    },
    'summary': None,
    'experiences': [],
    'education': [],
    'skills': [],
    'languages': [],
}


# Experience
{
    'title': None,
    'company': None,
    'company_logo': None,
    'date_range': {
        'start': {
            'month': None,
            'year': None,
        },
        'end': {
            'month': None,
            'year': None,
        },
        'current': None,
    },
    'description': None,
}


# School
{
    'school': None,
    'diploma': None,
    'date_range': {
        'start': {
            'year': None,
        },
        'end': {
            'year': None,
        },
        'current': None,
    },
    'description': None,
}


# Language
{
    'name': None,
    'proficiency': None,  # 0 - 4
}
"""