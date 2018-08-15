import json,time,urllib,random
import log
import environment

def getVideoInfo(http,aid):
	try:
		url='https://www.bilibili.com/video/av%d/'%aid
		log.log(url)
		r=http.get(url,headers={'User-Agent':environment.user_agent}).text
		s='"cid='
		cid=int(r[r.find(s)+len(s):r.find('&',r.find(s))])
		p1=r.find('<title>')+7;p2=r.find('</title>',p1)
		title=r[p1:p2]
		r=http.get('https://interface.bilibili.com/player?id=cid:'+str(cid)+'&aid='+str(aid),headers={'User-Agent':environment.user_agent}).text
		p1=r.find('<duration>')+10;p2=r.find('</duration>',p1)
		lt=r[p1:p2]
		le=0
		while True:
			pos=lt.find(':')
			if pos==-1:pos=len(lt)
			le=le*60+int(lt[:pos])
			if pos==len(lt):break
			lt=lt[pos+1:]
		return {
			'aid':aid,
			'cid':cid,
			'url':url,
			'len':le,
			'title':title,
		}
	except:
		return False

def getVideoList(http):
	res=[]
	if environment.init_video_list:
		r=http.get('https://www.bilibili.com/index/recommend.json',headers={'User-Agent':environment.user_agent}).json()
		for i in r['list']:
			res.append(i['aid'])
		#r=http.get('https://www.bilibili.com/',headers={'User-Agent':environment.user_agent}).text
		#s='"recommendData":'
		#r=r[r.find(s)+len(s):r.find('</script>',r.find(s))-1]
		#for i in json.loads(r):
		#	res.append(int(i['aid']))
		r=http.get('https://api.bilibili.com/x/web-interface/dynamic/index',headers={'User-Agent':environment.user_agent}).json()
		for i in r['data']:
			for j in r['data'][i]:
				res.append(j['aid'])
	random.shuffle(res)
	res2=[]
	for i in res:
		log.log('getVideoInfo:%d'%i)
		t=getVideoInfo(http,i)
		if t:res2.append(t)
		time.sleep(1)
		#if len(res2)>40:break
	#print res,len(res)
	return res2

def watchVideo(http,vi,proxy=None):
	if proxy!=None:
		p={
			'http':str(proxy),
			'https:':str(proxy),
		}
	else:p=None
	t={
		'aid':vi['aid'],
		'cid':vi['cid'],
		'mid':http.cookies['DedeUserID'],
		'csrf':http.cookies['bili_jct'],
		'played_time':vi['len'],
		'realtime':vi['len'],
		'start_ts':int(time.time())-233,
		'type':3,
		'dt':2,
		'play_type':0,
	}
	#print t
	r=http.post('https://api.bilibili.com/x/report/web/heartbeat',data=t,proxies=p,headers={'User-Agent':environment.user_agent,'Referer':vi['url'],'Origin':'https://www.bilibili.com','Accept': 'application/json, text/javascript, */*; q=0.01','Accept-Language': 'zh-CN,zh;q=0.9'},verify=False)
	#print r.text

def giveCoin(http,vi):
	t={
		'mid':http.cookies['DedeUserID'],
		'fts':int(time.time())-20,
		'url:':urllib.quote_plus(vi['url']),
		'proid':1,
		'ptype':1,
		'optype':2,
		'clickid':'',
		'showid':1,
		'pagetype':'',
		'coincount':'',
		'defaultcoin':0,
		'result':'',
	}
	t['_']=int(time.time()*1000)
	r=http.get('https://data.bilibili.com/v/web/web_givecoin',params=t,headers={'User-Agent':environment.user_agent})
	#print r.text,t
	p={
		'aid':vi['aid'],
		'rating':100,
		'player':1,
		'multiply':1,
		'csrf':http.cookies['bili_jct'],
	}
	r=http.post('https://www.bilibili.com/plus/comment.php',data=p,headers={'Referer':vi['url'],'User-Agent':environment.user_agent})
	#print '|',r.text,p
	if r.text!='OK':return False
	t['optype']=3
	t['showid']=''
	t['defaultcoin']=''
	t['result']=1
	t['_']=int(time.time()*1000)
	r=http.get('https://data.bilibili.com/v/web/web_givecoin',params=t,headers={'User-Agent':environment.user_agent})
	#print r.text,t
	t['optype']=2
	t['showid']=4
	t['result']=''
	t['_']=int(time.time()*1000)
	r=http.get('https://data.bilibili.com/v/web/web_givecoin',params=t,headers={'User-Agent':environment.user_agent})
	#print r.text,t
	t['optype']=4
	t['showid']=''
	t['_']=int(time.time()*1000)
	r=http.get('https://data.bilibili.com/v/web/web_givecoin',params=t,headers={'User-Agent':environment.user_agent})
	#print r.text,t
	return True
