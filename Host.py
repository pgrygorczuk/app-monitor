import datetime
import tests
from TestResult import TestResult

class Host:

	def __init__(self, name, params):
		self.name		= name
		self.url		= params['url']
		self.tests		= params['tests']
		self.verify_ssl = params['verify_ssl']
		self.send_sms	= params['send_sms']
		self.idle_time	= [i.strip() for i in params['idle_time'].split('-')]
		self.trials		= 0
	
	def is_idle_time(self):
		now = datetime.datetime.now()
		start = [int(x) for x in self.idle_time[0].split(':')]
		end	  = [int(x) for x in self.idle_time[1].split(':')]
		return  ( now.hour > start[0] or now.hour == start[0] and now.minute >= start[1] ) or \
				( now.hour < end[0]   or now.hour == end[0]   and now.minute <= end[1]	 )

	def run_test(self, test_name:str='httping') -> TestResult:
		f = getattr(tests, test_name)
		return f(self)

