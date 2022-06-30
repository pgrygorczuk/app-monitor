import pickle, time, requests, os, yaml


class SMS:

	DUMP_FILENAME = 'sms-history.pic'
	API = { 'url': '', 'key': '' }
	INTERVAL = 3600

	def __init__(self, api_url:str='', api_key:str='', interval:int=3600):
		self.history = {}
		self.load()
		SMS.API['url'] = api_url
		SMS.API['key'] = api_key
		SMS.INTERVAL = interval

	def save(self):
		with open(SMS.DUMP_FILENAME, 'wb') as f:
			pickle.dump(self.history, f)

	def load(self):
		if os.path.exists(SMS.DUMP_FILENAME):
			with open(SMS.DUMP_FILENAME, 'rb') as f:
				self.history.update( pickle.load(f) )

	def __send_request(self, to:str, message:str) -> bool:
		r = requests.put( SMS.API['url'],
			params  = {'to': to, 'message': message},
			headers = {'x-api-key': SMS.API['key']} )
		return r.status_code == 200

	def send(self, numbers:list, message:str, check_history:bool=True) -> bool:
		result = True
		for num in numbers:
			msgid = (num, message)
			if check_history and msgid in self.history:
				# Message in history, check time.
				if self.history[msgid] + SMS.INTERVAL < time.time():
					self.history[msgid] = time.time()
					result = result and self.__send_request(to=num, message=message)
			else:
				# No message in history, save time and send.
				self.history[msgid] = time.time()
				result = result and self.__send_request(to=num, message=message)
				if result:
					print("Message '{}...' sent to '{}'".format(message[0:50], num))
				else:
					print("Message '{}...' NOT sent to '{}'".format(message[0:50], num))
		self.save()
		return result
