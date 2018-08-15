import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from base64 import b64encode
from io import BytesIO
from captcha import getCaptcha
import gtcaptcha
import log
import environment

def getkey(http):
	r=http.get('https://passport.bilibili.com/login?act=getkey',headers={'User-Agent':environment.user_agent})
	return r.json()

def rsaEncrypt(key,text):
	key=RSA.importKey(key)
	cipher=PKCS1_v1_5.new(key)
	return b64encode(cipher.encrypt(text))

def getPwd(pwd,http):
	k=getkey(http)
	return rsaEncrypt(k['key'],(k['hash']+pwd).encode('ascii'))

def login(uid,pwd,http,useGt=False):
	http.cookies=requests.cookies.RequestsCookieJar()
	if useGt:
		retries=2
	else:
		retries=4
	for i in range(retries):
		data={
			'userid':uid,
			'pwd':getPwd(pwd,http),
			'keep':1,
			'cType':2,
		}
		if useGt:
			data['vcType']=2
			gt=gtcaptcha.getBilibiliGt(http,'https://passport.bilibili.com/captcha/gc?cType=2')
			if not gt:return False
			data['challenge']=gt['challenge']
			data['seccode']=gt['validate']
			data['validate']=gt['validate']
		else:
			data['captcha']=getCaptcha(http)
			data['vcType']=1
		r=http.post('https://passport.bilibili.com/ajax/miniLogin/login',data=data,headers={'User-Agent':environment.user_agent})
		r=r.json()
		#print r
		if r['status']==True:return True
		code=r['message']['code']
		if code==-627 or code==-637 or code==-2100:return False
		log.log('Captcha Error')
	return False

def userinfo(http):
	r=http.post('https://account.bilibili.com/home/userInfo',headers={'User-Agent':environment.user_agent})
	r=r.json()
	if r['code']==0:return r['data']
	return ''