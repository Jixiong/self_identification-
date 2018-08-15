import requests
import json
import base64
from io import BytesIO
import log
import environment

def ca(im):
	url=''
	img_b64=base64.b64encode(im)
	payload={
		'img':img_b64,
		'token':'',
	}
	headers={
		'Content-Type':'application/x-www-form-urlencoded'
	}
	res=requests.post(url,data=payload,headers=headers)

	vcode=res.text
	return vcode

def getCaptcha(http):
	url='https://passport.bilibili.com/captcha'
	res=http.get(url,headers={'User-Agent':environment.user_agent})
	#print res.content
	#raw=BytesIO(res.content)
	#im=Image.open(raw)
	#im.show()
	code=ca(res.content)
	#print code
	return code
