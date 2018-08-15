import hashlib,urllib,requests
import login
import log
import environment

def getSign(params):
	params['appkey']=environment.app_key
	#print urllib.urlencode(params)
	t=[]
	for i in params:
		t.append((str(i),urllib.quote_plus(str(params[i]))))
	t.sort()
	p=''
	for i in t:
		if p!='':p+='&'
		a,b=i
		p+=a+'='+b
	#log.log('params: %s'%p,'Client')
	a=hashlib.md5(p+environment.app_secret).hexdigest()
	log.log('sign: %s'%a,'Client')
	params['sign']=a

def appLogin(uid,pwd):
	http=requests.Session()
	try:
		t={
			'userid':uid,
			'pwd':login.getPwd(pwd,http),
		}
		getSign(t)
		#print t
		r=http.get('https://account.bilibili.com/api/login/v2',params=t)
		#print r.text
		r=r.json()
		if r['code']==0:return r['access_key']
	except:pass
	return False

def getCookie(http,access_key):
	try:
		t={'access_key':access_key}
		http.cookies=requests.cookies.RequestsCookieJar()
		getSign(t)
		r=http.get('https://account.bilibili.com/api/login/sso',params=t,allow_redirects=False)
		log.log(http.cookies,'Client')
	except:pass

def addShare(http,access_key,aid):
	try:
		t={'access_key':access_key}
		getSign(t)
		r=http.post('http://api.bilibili.com/x/share/add?'+urllib.urlencode(t),data={'aid':aid})
		r=r.json()
		return r['code']==0
	except:return False

def chkAccessKey(access_key):
	http=requests.Session()
	try:
		t={'access_key':access_key}
		r=http.get('http://api.bilibili.cn/myinfo',params=t)
		log.log(r.text,'Client')
		r=r.json()
		if r.has_key('code'):
			return False
		return True
	except:return False
