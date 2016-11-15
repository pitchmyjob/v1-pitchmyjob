from os.path import join
import subprocess, os
from django.conf import settings


class Paiement():
	"""Request payment"""
	amount = 0
	user = 0
	job = 0
	path_file = settings.BASE_DIR + "/factures/mercanet/pathfile"
	path_bin = settings.BASE_DIR  + "/factures/mercanet/"
	normal_return_url = "http://www.pitchmyjob.com/pro/testpaiement"
	automatic_response_url = "http://www.pitchmyjob.com/facture/paiement-auto-response"
	cancel_return_url = "http://www.pitchmyjob.com/pro/testpaiement"
	merchant_id = "081138145800017"
	currency_code = "978"
	merchant_country = "fr"
	logo = "logopitch.jpg"

	def __init__(self, amount=None, type=None, user=None, job=None, normal_return=None, cancel_return=None):
		self.amount = amount
		self.user = user
		self.job = job
		self.type = type
		if normal_return:
			self.normal_return_url = normal_return
		if cancel_return :
			self.cancel_return_url = cancel_return

	def call_request(self):
		params = dict()
		params['merchant_id'] = self.merchant_id
		params['merchant_country'] = self.merchant_country
		params['currency_code'] = self.currency_code
		params['amount'] = str(self.amount)
		params['normal_return_url'] = self.normal_return_url
		params['cancel_return_url'] = self.cancel_return_url
		params['automatic_response_url'] = self.automatic_response_url
		params["pathfile"] = self.path_file
		params["order_id"] = self.job
		params["customer_id"] = self.user
		params["data"] = self.type
		params["logo_id2"] = self.logo

		executable = os.path.join(self.path_bin, 'request')

		args = [executable] + ["%s=%s" % p for p in params.iteritems()]
		result = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()

		tab = result[0].split('!')

		return tab


	def response(self, datas):
		params = dict()
		params['message'] = datas
		params["pathfile"] = self.path_file

		executable = os.path.join(self.path_bin, 'response')
		args = [executable] + ["%s=%s" % p for p in params.iteritems()]
		result = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()

		tab = result[0].split('!')

		code_dict = {
            "code": tab[1],
            "error": tab[2],
            "merchant_id": tab[3],
            "merchant_country": tab[4],
            "amount": tab[5],
            "transaction_id": tab[6],
            "payment_means": tab[7],
            "transmission_dat": tab[8],
            "payment_time": tab[9],
            "payment_date": tab[10],
            "response_code": tab[11],
            "payment_certificate": tab[12],
            "authorisation_id": tab[13],
            "currency_code": tab[14],
            "card_number": tab[15],
            "cvv_flag": tab[16],
            "cvv_response_code": tab[17],
            "bank_response_code": tab[18],
            "complementary_code": tab[19],
            "complementary_info": tab[20],
            "return_context": tab[21],
            "caddie": tab[22],
            "receipt_complement": tab[23],
            "merchant_language": tab[24],
            "language": tab[25],
            "customer_id": tab[26],
            "order_id": tab[27],
            "customer_email": tab[28],
            "customer_ip_address": tab[29],
            "capture_day": tab[30],
            "capture_mode": tab[31],
            "data": tab[32]
        }

		return code_dict