import time,urllib,random
from PIL import Image
from io import BytesIO
import live_captcha
import log
import environment

def sign(http):
	r=http.get('https://api.live.bilibili.com/sign/doSign')
	#print r.text
	r=r.json()
	if r['code']==0:return 0
	if r['code']==-101:return 1
	if r['code']==-500:return 0
	return 2

def wait(tm,it):
	al=0
	while al<tm:
		time.sleep(it)
		al+=it
		#log.log('Sleep %d/%d'%(al,tm),'Live_wait')

def getSilver(http):
	while True:
		r=http.get('http://api.live.bilibili.com/lottery/v1/SilverBox/getCurrentTask')
		log.log(r.text)
		r=r.json()
		#if r['code']==-10017:break
		if r['code']!=0:break
		wait(r['data']['minute']*60,30)
		ts=r['data']['time_start']
		te=r['data']['time_end']
		code=False
		while True:
			r=http.get('http://api.live.bilibili.com/lottery/v1/SilverBox/getCaptcha')
			img=Image.open(BytesIO(r.content))
			code=live_captcha.get(img)
			if code!=False:break
			log.log('live captcha error','Live')
			time.sleep(5)
		r=http.get('http://api.live.bilibili.com/lottery/v1/SilverBox/getAward',params={'time_start':ts,'end_time':te,'captcha':code})
		log.log(r.text)

def getRoomInfo(http,rid):
	r=http.get('https://api.live.bilibili.com/room/v1/Room/room_init',params={'id':rid}).json()
	if r['code']!=0:return False
	return r['data']

def getBagList(http):
	r=http.get('https://api.live.bilibili.com/gift/v2/gift/bag_list').json()
	if r['code']!=0:return False
	return r['data']['list']

def sendBag(http,ri,bag,cnt):
	data={
		'uid':http.cookies['DedeUserID'],
		'gift_id':bag['gift_id'],
		'ruid':ri['uid'],
		'gift_num':min(cnt,bag['gift_num']),
		'bag_id':bag['bag_id'],
		'platform':'pc',
		'biz_code':'live',
		'biz_id':ri['room_id'],
		'rnd':int(time.time()),
		'storm_beat_id':0,
		'metadata':'',
		'token':'',
		'csrf_token':http.cookies['bili_jct'],
	}
	r=http.post('https://api.live.bilibili.com/gift/v2/live/bag_send',data=data)
	#log.log(r.text,'Live')
	r=r.json()
	return r['code']==0

def sendGift(http,ri,gid,cnt):
	data={
		'uid':http.cookies['DedeUserID'],
		'gift_id':gid,
		'ruid':ri['uid'],
		'gift_num':cnt,
		'coin_type':'silver',
		'bag_id':0,
		'platform':'pc',
		'biz_code':'live',
		'biz_id':ri['room_id'],
		'rnd':int(time.time()),
		'storm_beat_id':0,
		'metadata':'',
		'token':'',
		'csrf_token':http.cookies['bili_jct'],
	}
	r=http.post('https://api.live.bilibili.com/gift/v2/gift/send',data=data)
	#log.log(r.text,'Live')
	r=r.json()
	return r['code']==0

def genStr(len):
	return ''.join(['0123456789ABCDEF'[random.randint(0,15)] for i in range(len)])

def genGUID():
	return genStr(8)+'-'+genStr(4)+'-'+genStr(4)+'-'+genStr(4)+'-'+genStr(12)

def getPlayUrl(http,rid):
	r=http.get('https://api.live.bilibili.com/api/playurl?player=1&cid=%d&quality=0&platform=flash&otype=json'%rid)
	print r.text
	return r.json()['durl'][0]['url']

def fakeWatch(http,ri,rid):
	tm=int(time.time()*1000)
	data=['https://live.bilibili.com/neptune/'+str(rid),http.cookies['DedeUserID'],environment.user_agent,'','','web','','','live',str(tm)]
	url='https://data.bilibili.com/log/web?000091'+str(tm)
	for i in data:url+='|'+urllib.quote_plus(i)
	print url
	http.get(url,headers={'User-Agent':environment.user_agent,'X-Requested-With':'ShockwaveFlash/27.0.0.183'})
	uuid=genGUID()
	playurl=getPlayUrl(http,ri['room_id'])
	otm=time.time()
	#for i in range(20):
	while True:
		time.sleep(10)
		#["fid","fver","roomid","loadtime","buffertimes","result","mid","playurl","delta_ts","guid","error_code"]
		data=['2.1.4-49bd888a',str(ri['room_id']),'','','346',http.cookies['DedeUserID'],playurl,str(int(time.time()-otm)),uuid,'']
		tm=int(time.time()*1000)
		url='https://data.bilibili.com/log/web?000077'+str(tm)+'PlayerEX'
		for i in data:url+='|'+urllib.quote_plus(i)
		print url
		http.get(url,headers={'User-Agent':environment.user_agent,'X-Requested-With':'ShockwaveFlash/27.0.0.183'})

def genGUIDh5():
	return ''.join(['0123456789qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGJKLZXCVBNM'[random.randint(0,62)] for i in range(8)])

