import requests, time
from TestResult import TestResult


def httping(host) -> TestResult:
	result = TestResult(host_name=host.name, test_name='httping')
	start = time.time()
	res = None

	try:
		res = requests.get(host.url, verify=host.verify_ssl)
		result.code = res.status_code
	except Exception as e:
		return result.set_error(e)

	if result.code != 200:
		return result.set_error("Error {}".format(result.code))
	else:
		result.message = "{} s.".format( round(time.time()-start, 2) )
	return result


def example(host) -> TestResult:
	result = TestResult(host_name=host.name, test_name='example')
	# Do a test here.
	return result

