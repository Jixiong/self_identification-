import requests,requests.utils,pickle,io

def saveSession(session):
	f=io.BytesIO()
	pickle.dump(requests.utils.dict_from_cookiejar(session.cookies),f)
	return f.getvalue()

def loadSession(cookies):
	cookies=requests.utils.cookiejar_from_dict(pickle.load(io.BytesIO(cookies.encode('ascii'))))
	res=requests.Session()
	res.cookies=cookies
	return res