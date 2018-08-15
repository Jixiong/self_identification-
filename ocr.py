import requests,io,time
from base64 import b64encode
from PIL import Image
import log
import environment

retry_time=5

def getOcrText(o):
	if o['errno']!=0:return False
	r=''
	for i in o['data']['words_result']:
		r+=i['words']
	return r

def _ocrImage(img,pool=None):
	f=io.BytesIO()
	img.save(f,'png')
	img='data:image/png;base64,'+b64encode(f.getvalue())
	if pool==None:
		p=None
	else:
		p=pool.get()
		if p=='':
			p=None
		else:
			p={'http':p,'https':p}
	h={'User-Agent':environment.user_agent,'X-Requested-With':'XMLHttpRequest','Origin':'https://cloud.baidu.com','Referer':'https://cloud.baidu.com/product/ocr/general'}
	r=requests.post('https://cloud.baidu.com/aidemo',data={'type':'commontext','image':img,'imageurl':''},headers=h,proxies=p,timeout=10)
	return r.json()

def ocrImage(img,pool=None):
	cnt=0
	while cnt<10:
		try:
			t=getOcrText(_ocrImage(img,pool))
			#print '/'+t+'/'
			if t!=False:return t
			log.log('demo api exceeded or error, sleep %ds'%retry_time)
			time.sleep(retry_time)
		except:
			cnt+=1
	return ''