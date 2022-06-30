import time, hashlib, datetime, requests
from urllib3.exceptions import MaxRetryError

class TestResult:

	def __init__(self, host_name:str, test_name:str, code:int=0, error:bool=False, message:str=''):
		self.start = time.time()
		self.code = code
		self.error = error
		self.message = message
		self.host_name = host_name
		self.test_name = test_name
		self.values = {}

	def __str__(self):
		return "{} {} {}".format(self.host_name, self.test_name, self.message)

	def set_error(self, message:str):
		self.error = True
		self.message = "{} {} {}".format(self.host_name, self.test_name, message)
		return self

	def get_time(self) -> float:
		return round(time.time()-self.start, 2)

	def upload(self, url:str, key:str) -> bool:
		now = datetime.datetime.now()
		key = hashlib.sha1("{}-{}".format(now.strftime("%y%m%d"), key).encode('utf-8'))
		# PHP: URL/status($klucz, $slug, $status, $opis='')
		url = "{}/{}/{}/{}/{}/{}".format(
			url, key.hexdigest(),	# Connection parameters.
			self.host_name.lower(), # Host id (lowercase)
			self.test_name, 		# Name of a test.
			int(self.error),		# Status: 0=no errors, 1=error, 2=can't process.
			self.message 			# Description, additional parameter (e.g. response time).
		)
		res = 500
		try:
			res = requests.get(url)
		except MaxRetryError as e:
			print("{}: MaxRetryError Exception".format(url))
		return res.status_code
