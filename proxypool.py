import requests,threading,time,random
import log
import environment

p_fin=[]
lock=threading.RLock()

class ProxyPool:
	def __init__(self,p):
		self.p=p
		self.p.append('')
		self.p=list(set(self.p))
		self.cur=0
		self.lock=threading.RLock()
	def get(self):
		self.lock.acquire()
		self.cur+=1
		res=self.p[self.cur%len(self.p)]
		self.lock.release()
		return res

'''
def checkproxy(p):
	global p_fin
	log.log('checkproxy: '+p)
	t={
		'http':str(p),
		'https:':str(p),
	}
	try:
		r=requests.Session().get('http://ip2.mcfx.us:2333',proxies=t,timeout=environment.proxy_timeout)
	except:
		return
	if r.text.find('ngrok')!=-1:
		log.log(p+' ok')
		lock.acquire()
		p_fin.append(p)
		lock.release()

def getProxyPool():
	global p_fin
	try:
		p=[]
		for i in p_fin:
			p.append(i)
		log.log('init proxy pool')
		if environment.init_proxy:
			for i in range(1,4):
				if environment.use_origin_proxy_site:
					log.log('Use origin proxy site')
					time.sleep(1)
					r=requests.get('http://www.xicidaili.com/nt/%d'%i,headers={'User-Agent':environment.user_agent}).text
				else:
					r=requests.get('http://ip2.mcfx.us:2333/tmp.html').text
				s='<td>'
				while r.find('Cn')!=-1:
					r=r[r.find('Cn'):]
					r=r[r.find(s)+len(s):]
					x=r[:r.find('<')]
					r=r[r.find(s)+len(s):]
					y=r[:r.find('<')]
					p.append('http://'+x+':'+y)
		p=list(set(p))
		th=[]
		for i in p:
			th.append(threading.Thread(target=checkproxy,args=(i,)))
		p_fin=[]
		for i in th:
			i.setDaemon(True)
			i.start()
		while True:
			flag=True
			for i in th:
				if i.isAlive():
					flag=False
			if flag:break
			time.sleep(0.1)
		return ProxyPool(p_fin)
	except:return ProxyPool([])
'''

def getProxyPool():
	r=requests.get(environment.proxy_site).json()
	t=[]
	for i in r:
		if i[2]>3:
			t.append(i[0]+':'+str(i[1]))
	random.shuffle(t)
	return ProxyPool(t)

#print getProxyPool().get()
