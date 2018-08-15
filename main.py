import requests,time,threading,random
import login
from account import *
import answer
import video
import video_fav
import live
import client
import log
import environment
import proxypool

answer_interval=43500
answer_wait_time=600
chk_login_interval=86400
chk_login_retry=3600
chk_access_key_interval=43200
chk_access_key_retry=7200
chk_access_key_interval_global=3
video_interval=40000
video_retry=3600
video_interval_global=3
video_share_retry=3600
video_upd_interval=40000
save_all_interval=3600
proxy_pool_interval=1800
live_sign_interval=40000
live_silver_interval=40000

give_coin_limit=15

lst_video_upd=0
lst_video_global=0
lst_chk_access_key_global=0
video_list=[]
video_list_pos=0
lst_save_all=time.time()
proxy_pool=proxypool.getProxyPool()
lst_proxy_pool=time.time()

loadAll()

exit_tm=time.time()+10800

def autoLogin(u):
	u['http'].cookies=requests.cookies.RequestsCookieJar()
	flag=False
	for i in environment.login_pref:
		if flag:break
		if i=='access_key':
			for j in range(2):
				client.getCookie(u['http'],u['access_key'])
				u['userinfo']=login.userinfo(u['http'])
				if u['userinfo']!='':
					flag=True
					break
				u['access_key']=client.appLogin(u['uid'],u['pwd'])
		if i=='legacy_captcha':
			try:
				if login.login(u['uid'],u['pwd'],u['http'],False):
					u['userinfo']=login.userinfo(u['http'])
					break
			except:pass
		if i=='gt_captcha':
			try:
				if login.login(u['uid'],u['pwd'],u['http'],True):
					u['userinfo']=login.userinfo(u['http'])
					break
			except:pass
	return u['userinfo']!=''

def answer_worker():
	while environment.enable_answer and time.time()<exit_tm:
		flag=False
		tm=time.time()
		for u in us:
			if u['userinfo']=='':continue
			if not checkLevel(u):
				if u['to_ans']!='' and u['ans_time']<tm:
					try:
						answer.run_lb(u['http'],u['to_ans'])
						answer.run_lst(u['http'])
					except:
						log.log('answer part 2 error','Main')
					u['to_ans']=''
					u['lst_chk_login']=0
					flag=True
					break
				if tm-u['lst_answer']>answer_interval:
					log.log('%s low level'%u['uid'],'Main')
					res=False
					try:
						res=answer.run(u['http'],proxy_pool)
					except:
						log.log('answer part 1 error','Main')
					if type(res) is dict:
						if res['lst']:
							answer.run_lst(u['http'])
							u['lst_chk_login']=0
						else:
							u['to_ans']=res['data']
							u['ans_time']=tm+answer_wait_time
					u['lst_answer']=tm
					saveUser(u)
					flag=True
					break
				else:continue
		if flag:
			time.sleep(1)
		else:
			log.log('Answer Worker: nothing to do','Main')
			time.sleep(10)

answer_thread=threading.Thread(target=answer_worker,args=())
answer_thread.setDaemon(True)
answer_thread.start()

def web_task_worker():
	http=requests.Session()
	http.cookies['uid']=environment.server_key
	while environment.enable_web and time.time()<exit_tm:
		try:
			r=http.get(environment.server_url+'task.php?op=get',timeout=5).json()
		except:
			time.sleep(100)
			continue
		log.log(r,'Web')
		for task in r:
			ret={'id':task['id']}
			log.log(task,'Web')
			if task['type']=='answer':
				try:
					http_t=requests.Session()
					u={'uid':task['uid'],'pwd':task['pwd'],'http':http_t}
					u['access_key']=client.appLogin(u['uid'],u['pwd'],requests)
					if autoLogin(u):
						log.log('login OK','Web')
						log.log(u['userinfo'],'Web')
						if not checkLevelI(u['userinfo']):
							answer.web_auto(http_t)
				except int:pass
			elif task['type']=='answer_cookie':
				'to do'
			elif task['type']=='video_fav':
				rem=task['count']
				bu=ac.getVideoUsers('video_fav',task['aid'])
				ids=[i for i in xrange(len(us))]
				random.shuffle(ids)
				try:
					for i in ids:
						if rem==0:break
						u=us[i]
						if u['uid'] in bu or u['userinfo']=='':continue
						if video_fav.addFavAuto(u['http'],task['aid']):
							rem-=1
							ac.addVideoRecord('video_fav',u['uid'],task['aid'])
							log.log('add fav ok','Web')
				except int:pass
				ret['count']=task['count']-rem
			elif task['type']=='video_coin':
				rem=task['count']
				ids=[i for i in xrange(len(us))]
				random.shuffle(ids)
				ids=ids[:100]
				vi=video.getVideoInfo(us[ids[0]]['http'],task['aid'])
				try:
					for i in ids:
						if rem==0:break
						u=us[i]
						if u['userinfo']=='':continue
						if video.giveCoin(u['http'],vi):
							rem-=1
							log.log('give coin ok','Web')
				except int:pass
				ret['count']=task['count']-rem
			elif task['type']=='video_share':
				rem=task['count']
				ids=[i for i in xrange(len(us))]
				random.shuffle(ids)
				vi=video.getVideoInfo(us[ids[0]]['http'],task['aid'])
				try:
					for i in ids:
						if rem==0:break
						u=us[i]
						if time.time()-u['lst_chk_access_key']>chk_access_key_interval:continue
						if client.addShare(u['http'],u['access_key'],vi['aid']):
							rem-=1
							log.log('share ok','Web')
				except:pass
				ret['count']=task['count']-rem
			log.log(ret,'Web')
			ret['op']='ret'
			while True:
				try:
					t=http.get(environment.server_url+'task.php',params=ret)
					t=t.json()
					if t['status']==0:break
					time.sleep(1)
					log.log('Cannot get task','Web')
				except:pass
				time.sleep(0.1)
			#exit()
		time.sleep(10)

web_task_thread=threading.Thread(target=web_task_worker,args=())
web_task_thread.setDaemon(True)
web_task_thread.start()

def live_silver_worker():
	thread_lim=200
	th=[]
	while environment.enable_answer and time.time()<exit_tm:
		tn=[]
		for i in th:
			if i.isAlive():tn.append(i)
		th=tn
		flag=True
		tm=time.time()
		if len(th)<thread_lim:
			for u in us:
				if tm-u['lst_live_silver']>live_silver_interval:
					log.log(u['uid']+' '+str(u['lst_live_silver']))
					log.log(u['uid']+' start live silver','Live Silver')
					u['lst_live_silver']=tm
					t=threading.Thread(target=live.getSilver,args=(u['http'],))
					t.setDaemon(True)
					th.append(t)
					t.start()
					flag=False
					break
		if flag:
			time.sleep(10)
			log.log('Live Silver Worker: nothing to do','Main')
		else:
			time.sleep(1)

if environment.enable_live_silver:
	live_silver_thread=threading.Thread(target=live_silver_worker,args=())
	live_silver_thread.setDaemon(True)
	live_silver_thread.start()

#exit_tm=time.time()-100

def debugUser(uid):
	global us,us_old
	us_old=us
	us=[]
	for i in us_old:
		if i['uid']==uid:
			us.append(i)

#debugUser('17075537124')
#us[0]['lst_chk_login']=0

sleep_cnt=0
while environment.enable_main and time.time()<exit_tm:
	sleep_time=0
	tm=time.time()
	if tm-lst_proxy_pool>proxy_pool_interval:
		proxy_pool=proxypool.getProxyPool()
		lst_proxy_pool=tm
	if tm-lst_save_all>save_all_interval:
		log.log('Save all','Main')
		for i in us:
			saveHttp(i,False)
		ac.commit()
		lst_save_all=tm
		log.log('Save all ok','Main')
	user_cnt=0
	lv2_cnt=0
	wfa_cnt=0
	ad_cnt=0
	for u in us:
		if u['userinfo']!='':
			user_cnt+=1
			if checkLevel(u):
				lv2_cnt+=1
				if tm-lst_video_upd<=video_upd_interval and tm-u['lst_video']<=video_interval and tm-u['lst_live_sign']<=live_sign_interval:
					ad_cnt+=1
		if u['to_ans']!='':wfa_cnt+=1
	if sleep_cnt%10==0:
		log.log('User cnt:%d, Level2 cnt:%d, Wait for ans cnt:%d, All done cnt:%d'%(user_cnt,lv2_cnt,wfa_cnt,ad_cnt),'Main')
	for u in us:
		#print u
		if u['ban']:continue
		if tm-u['lst_chk_access_key']>chk_access_key_interval and tm-lst_chk_access_key_global>chk_access_key_interval_global:
			log.log('chk access key for %s'%u['uid'],'Main')
			if client.chkAccessKey(u['access_key']):
				log.log('access key is ok','Main')
				u['lst_chk_access_key']=tm
			else:
				t=client.appLogin(u['uid'],u['pwd'])
				if t:
					u['access_key']=t
					log.log('access_key: %s'%t,'Main')
					log.log('client login ok','Main')
					u['lst_chk_access_key']=tm
				else:
					u['lst_chk_access_key']=tm+chk_access_key_retry-chk_access_key_interval
					log.log('client access key failed, retry ad %.0lf (tm=%.0lf)'%(u['lst_chk_access_key']+chk_access_key_interval,tm),'Main')
			lst_chk_access_key_global=tm
			saveUser(u)
			saveHttp(u)
			sleep_time=0.1
			break
		if tm-u['lst_chk_login']>chk_login_interval:
			log.log('get userinfo for %s'%u['uid'],'Main')
			try:
				u['userinfo']=login.userinfo(u['http'])
				u['lst_chk_login']=tm
			except:
				u['lst_chk_login']=tm+chk_login_retry-chk_login_interval
				log.log('get userinfo failed, retry at %.0lf (tm=%.0lf)'%(u['lst_chk_login']+chk_login_interval,tm),'Main')
			saveUser(u)
			log.log(u['userinfo'],'Main')
			sleep_time=0.1
			break
		if u['userinfo']=='':
			log.log('%s not logged'%u['uid'],'Main')
			try:
				if autoLogin(u):
					u['userinfo']=login.userinfo(u['http'])
					log.log('%s login ok'%u['uid'],'Main')
					log.log(u['userinfo'],'Main')
				else:
					u['ban']=1
					log.log('%s banned'%u['uid'],'Main')
			except:
				log.log('login failed','Main')
				u['lst_chk_login']=0
			saveHttp(u)
			saveUser(u)
			sleep_time=0.1
			break
		if not checkLevel(u):continue
		if tm-lst_video_upd>video_upd_interval:
			#continue
			try:
				video_list=video.getVideoList(u['http'])
				video_list_pos=0
				log.log('video list:'+str(video_list),'Main')
				lst_video_upd=tm
			except:
				log.log('get video list error','Main')
			sleep_time=0.5
			break
		if tm-u['lst_video']>video_interval and tm-lst_video_global>video_interval_global:
			log.log('%s try to watch video'%u['uid'],'Main')
			try:
				v=video_list[video_list_pos%len(video_list)]
				video_list_pos+=1
				log.log('video:aid=%d cid=%d'%(v['aid'],v['cid']),'Main')
				video.watchVideo(u['http'],v)
				if u['userinfo']['coins']>give_coin_limit:
					video.giveCoin(u['http'],v)
				client.addShare(u['http'],u['access_key'],v['aid'])
				u['lst_video']=tm
				u['lst_chk_login']=0
			except Exception,e:
				u['lst_video']=tm+video_retry-video_interval
				log.log('watch video error, retry at %.0lf (tm=%.0lf)'%(u['lst_video']+video_interval,tm),'Main')
				log.log(e)
			lst_video_global=tm
			saveUser(u)
			sleep_time=0.1
			break
		if tm-u['lst_live_sign']>live_sign_interval:
			log.log('%s live sign'%u['uid'],'Main')
			tf=False
			try:
				st=live.sign(u['http'])
				if st!=0:tf=True
				if st==1:
					u['access_key']=''
					u['http'].cookies=requests.cookies.RequestsCookieJar()
					u['lst_chk_access_key']=0
					u['lst_chk_login']=tm-chk_login_interval-chk_login_retry
					tf=True
			except:
				tf=True
			if not tf:
				log.log('%s live sign ok'%u['uid'],'Main')
			else:
				log.log('%s live sign failed'%u['uid'],'Main')
			u['lst_live_sign']=tm
			saveUser(u)
			sleep_time=0.1
			break
	if sleep_time==0:
		sleep_time=1
		if sleep_cnt%10==0:
			log.log('Nothing to do. Sleep 1s','Main')
		sleep_cnt+=1
	else:
		sleep_cnt=0
	time.sleep(sleep_time)

while answer_thread.isAlive() or web_task_thread.isAlive():
	time.sleep(20)
	#log.log('prepare to exit','Main')
