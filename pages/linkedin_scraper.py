#-*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import mechanize

from bs4 import BeautifulSoup


class LinkedInScraper(object):
    """ Allow to parse public LinkedIn profile and retrieve data """
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
    headers = [
            ('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:46.0) Gecko/20100101 Firefox/46.0'),
            ('Accept-Language', 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3'),
        ]

    def __init__(self, url):
        # Initializing fake browser to bypass LinkedIn security
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        browser.addheaders = self.headers
        browser.open(self._encode_url(url))

        # Initializing BeautifulSoup object to parse the HTML response
        self.bs = BeautifulSoup(browser.response().read(), 'html.parser')

        # Getting data
        self.parse()

    def parse(self):
        """ Parse LinkedIn profile """
        self.parse_user()
        self.parse_summary()
        self.parse_experiences()
        self.parse_education()
        self.parse_skills()
        self.parse_languages()

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
            self.data['summary'] = bs_summary.get_text()

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
                    'location':None,
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
                    experience['description'] = bs_experience_description.get_text()

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
                    'logo' : None,
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
                    school['description'] = bs_school_description.get_text()

                if bs_school_logo:
                    school['logo'] = bs_school_logo.find('img').get('data-delayed-url')

                self.data['education'].append(school)

    def parse_skills(self):
        """ Parse skills """
        self.data['skills'] = []

        bs_skills = self.bs.find(id='skills')
        if bs_skills:
            for bs_skill in bs_skills.find_all(class_='skill'):
                if not bs.skill.find(class_='wrap'):
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

                if bs_language_proficiency:
                    language['proficiency'] = self._parse_proficiency(bs_language_proficiency.get_text())

                self.data['languages'].append(language)

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