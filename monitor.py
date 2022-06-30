#!/home/uwb-monitor/env/bin/python

import time, datetime, yaml, traceback, pathlib, sys
# from ssl import SSLError, SSLCertVerificationError
from Host import Host
from SMS import SMS

TRIALS  = 3
REFRESH_TIME  = 300

config_update_time = 0
config = {}
hosts = {}
sms = None

def get_now() -> str:
	return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def prnt(message:str):
	print("{}>{}".format(get_now(), message))

def is_config_updated() -> bool:
	f_name = pathlib.Path('config.yaml')
	m_timestamp = f_name.stat().st_mtime
	return config_update_time < m_timestamp

def load_config() -> dict:
	global TRIALS, REFRESH_TIME, config_update_time, hosts, sms
	config = None
	with open('config.yaml', 'r') as f:
		config = yaml.load(f.read(), Loader=yaml.Loader)
	TRIALS		 = config['trials']
	REFRESH_TIME = config['refresh_time']
	config_update_time = time.time()
	for host in config['hosts']:
		hosts[host] = Host(host, config['hosts'][host])
	sms = SMS(
		api_url  = config['sms_api'],
		api_key  = config['sms_api_key'],
		interval = config['sms_interval'])
	return config

def main_loop():
	global config, hosts, sms
	if sms is None or is_config_updated():
		config = load_config()
		prnt("Configuration loaded.")
	for host in hosts.values():
		if host.is_idle_time():
			host.trials = 0
			continue
		for test in host.tests:
			result = host.run_test(test_name = test) # code, error, message
			prnt("{} {}: {} ({}s)".format(test, host.name, result.code, result.get_time()))
			status_code = result.upload(url=config['log_api'], key=config['log_api_key'])
			if status_code != 200:
				prnt("Can't upload result ({})".format(status_code))
			if result.error:
				host.trials += 1
				prnt("{} ({}/{})".format(result.message, host.trials, TRIALS))
				if host.trials >= TRIALS:
					host.trials = 0
					if host.send_sms:
						# Send a text message.
						sms.send(
							numbers = host.send_sms,
							message = result.message )
	if REFRESH_TIME > 0:
		prnt("Waiting {} s.".format(REFRESH_TIME))
		time.sleep(REFRESH_TIME)


if __name__ == '__main__':

	if len(sys.argv) > 1 and sys.argv[1] == 'test':
		config = load_config()
		prnt("Sending message to {}.".format(config['default_number']))
		sms.send(
			numbers = [config['default_number']],
			message = 'SMS tools testing message.',
			check_history = False )
		exit()
	
	while True:
		try:
			main_loop()
		except KeyboardInterrupt as e:
			break
		except Exception as e:
			prnt("Exception {}:\n{}".format(e, traceback.format_exc()))
			break
		if REFRESH_TIME <= 0:
			break
