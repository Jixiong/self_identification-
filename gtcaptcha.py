import requests
import log

gt_user=''
gt_pass=''

def check(http,url,t):
	d={
		'gt':t['gt'],
		'challenge':t['challenge'],
		'referer':url,
		'user':gt_user,
		'pass':gt_pass,
		'return':'json',
		#'model':3
	}
	r=requests.get('http://jiyanapi.c2567.com/shibie',params=d)
	#print r.text
	r=r.json()
	if r['status']=='ok':return r
	return False

def getUrlReferer(url):
	return url[:url.find('/',url.find('//')+2)+1]

def getBilibiliGt(http,url):
	retry_cnt=10
	for i in range(retry_cnt):
		r=http.get(url)
		log.log(r.text)
		try:
			r=r.json()
		except:
			return False
		if r['code']==-3 or r['code']==-1:return False
		gt=check(http,getUrlReferer(url),r['data'])
		if gt:return gt
	return False
