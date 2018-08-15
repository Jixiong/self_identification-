import requests,io,time,threading,random
from PIL import Image
import ocr
import answer_match
import gtcaptcha
import log
import environment

def getImage(url):
	r=requests.get(url)
	f=io.BytesIO(r.content)
	return Image.open(f)

def clearWhite(im):
	w,h=im.size
	oldw=w;oldh=h
	while w>0:
		w-=1;flag=True
		for i in range(h):
			if im.getpixel((w,i))<220:
				flag=False
		if not flag:break
	w=min(w+5,oldw)
	while h>0:
		h-=1;flag=True
		for i in range(w):
			if im.getpixel((i,h))<220:
				flag=False
		if not flag:break
	h=min(h+5,oldh)
	return im.crop((0,0,w,h))

def getQImgs(q):
	im=getImage(q['ans_img'])
	res={}
	res['qs']=clearWhite(im.crop((0,0,600,q['qs_h'])))
	res['ans1']=clearWhite(im.crop((0,q['ans0_y'],600,q['ans0_y']+q['ans0_h'])))
	res['ans2']=clearWhite(im.crop((0,q['ans1_y'],600,q['ans1_y']+q['ans1_h'])))
	res['ans3']=clearWhite(im.crop((0,q['ans2_y'],600,q['ans2_y']+q['ans2_h'])))
	res['ans4']=clearWhite(im.crop((0,q['ans3_y'],600,q['ans3_y']+q['ans3_h'])))
	return res

lock=threading.RLock()

def ocrWorker(res,id,img,pool):
	global proxy_pool
	t=ocr.ocrImage(img,pool)
	lock.acquire()
	res[id]=t
	lock.release()

ids_pub=''
answer_cnt=0

def answerWorker(i,p,pool):
	global ids_pub,answer_cnt
	t=getQImgs(i)
	txtq=[0 for j in range(5)]
	th=[]
	th.append(threading.Thread(target=ocrWorker,args=(txtq,0,t['qs'],pool)))
	th.append(threading.Thread(target=ocrWorker,args=(txtq,1,t['ans1'],pool)))
	th.append(threading.Thread(target=ocrWorker,args=(txtq,2,t['ans2'],pool)))
	th.append(threading.Thread(target=ocrWorker,args=(txtq,3,t['ans3'],pool)))
	th.append(threading.Thread(target=ocrWorker,args=(txtq,4,t['ans4'],pool)))
	for j in th:
		j.setDaemon(True)
		j.start()
	while True:
		flag=True
		for j in th:
			if j.isAlive():
				flag=False
		if flag:break
		time.sleep(0.1)
	log.log('ocr OK')
	ans=answer_match.getBestAns(txtq)
	if ans==0:ans=random.randint(1,4)
	
	lock.acquire()
	if ids_pub!='':ids_pub+=','
	ids_pub+=str(i['qs_id'])
	p['ans_hash_%d'%i['qs_id']]=i['ans%d_hash'%ans]
	answer_cnt+=1
	debug_str=str(answer_cnt)+' '
	lock.release()
	for j in txtq:
		debug_str+=j+' '
	debug_str+='   ans='+str(ans)
	log.log(debug_str)

def run(http,pool):
	global ids_pub,answer_cnt
	r=http.get('https://account.bilibili.com/answer/getBaseQ',headers={'User-Agent':environment.user_agent})
	r=r.json()
	if r.has_key('location') and r['location']=='/answer/answer_check.html':
		return {'lst':True}
	#print r
	if r.has_key('data'):
		que=r['data']['questionList']
		baseAns={}
		for i in que:
			baseAns[i['qs_id']]=1
		while True:
			t={}
			ids=''
			for i in que:
				t['ans_hash_%d'%i['qs_id']]=i['ans%d_hash'%baseAns[i['qs_id']]]
				if ids!='':ids+=','
				ids+=str(i['qs_id'])
			t['qs_ids']=ids
			r=http.post('https://account.bilibili.com/answer/goPromotion',data=t,headers={'User-Agent':environment.user_agent})
			r=r.json()
			#print r
			if r['code']==0:
				break
			for i in r['message']:
				baseAns[i]+=1
	r=http.get('https://account.bilibili.com/answer/extraQst',headers={'User-Agent':environment.user_agent})
	r=r.json()
	#print r
	if r.has_key('data'):
		que=r['data']['questionList']
		baseAns={}
		for i in que:
			baseAns[i['qs_id']]=1
		while True:
			t={}
			ids=''
			for i in que:
				t['ans_hash_%d'%i['qs_id']]=i['ans%d_hash'%baseAns[i['qs_id']]]
				if ids!='':ids+=','
				ids+=str(i['qs_id'])
			t['qs_ids']=ids
			r=http.post('https://account.bilibili.com/answer/extraQst/check',data=t,headers={'User-Agent':environment.user_agent})
			r=r.json()
			print r
			if r['code']==0:
				break
			for i in r['message']:
				baseAns[i]+=1
	#return False
	r=http.get('https://account.bilibili.com/answer/getProType',headers={'User-Agent':environment.user_agent})
	r=r.json()
	#print r
	if r['code']!=0:return False
	r=http.get('https://account.bilibili.com/answer/getQstByType?type_ids=9,12,13',headers={'User-Agent':environment.user_agent})
	#print r.text
	r=r.json()['data']
	ids=''
	p={}
	th=[]
	for i in r:
		th.append(threading.Thread(target=answerWorker,args=(i,p,pool)))
	ids_pub=''
	answer_cnt=0
	for i in th:
		i.setDaemon(True)
		i.start()
	while True:
		flag=True
		for i in th:
			if i.isAlive():
				flag=False
		if flag:break
		time.sleep(0.5)
	p['qs_ids']=ids_pub
	log.log(p)
	#for i in range(1,13):
	#	log.log('sleep 10s %i/12'%i)
	#	time.sleep(10)
	return {'lst':False,'data':p}

def run_lb(http,p):
	r=http.post('https://account.bilibili.com/answer/checkPAns',data=p,headers={'User-Agent':environment.user_agent})
	log.log(r.text)

def run_lst(http):
	gt=gtcaptcha.getBilibiliGt(http,'https://account.bilibili.com/ajax/answer/GetGtCaptcha')
	if not gt:return False
	t={
		'geetest_challenge':gt['challenge'],
		'geetest_seccode':gt['validate'],
		'geetest_validate':gt['validate'],
		'captcha_type':'gt'
	}
	log.log(t)
	r=http.get('https://account.bilibili.com/answer/checkGtCaptcha',params=t,headers={'User-Agent':environment.user_agent})
	log.log('gtcaptcha:')
	log.log(r.text)
	try:
		r=r.json()
		return r['code']==0
	except:
		return False

def web_auto(http,pool=None):
	try:
		res=run(http,pool)
		#print res
		if type(res) is dict:
			if not res['lst']:
				for i in range(15):
					log.log('Sleep 10s, %d/15'%i,'Web')
					time.sleep(10)
				run_lb(http,res['data'])
			return run_lst(http)
		else:
			return False
	except int:
		return False
