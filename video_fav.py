import random
import environment

randstr=lambda x:''.join([unichr(random.randint(0,25)+ord('a'))for i in range(x)])

def getFolders(http):
	r=http.get('https://api.bilibili.com/x/v2/fav/folder',headers={'User-Agent':environment.user_agent})
	r=r.json()
	if r['code']!=0:return False
	res=[]
	for i in r['data']:
		if i['state']!=0 and i['cur_count']<i['max_count']:
			res.append(i['fid'])
	return res

def addFolder(http,name=randstr(15)):
	t={'name':name,'public':1,'csrf':http.cookies['bili_jct']}
	r=http.post('https://api.bilibili.com/x/v2/fav/folder/add',data=t,headers={'User-Agent':environment.user_agent})
	r=r.json()
	if r['code']!=0:return False
	return r['data']['fid']

def addFav(http,aid,fid):
	t={'aid':aid,'fid':fid,'csrf':http.cookies['bili_jct']}
	r=http.post('https://api.bilibili.com/x/v2/fav/video/add',t,headers={'User-Agent':environment.user_agent})
	r=r.json()
	return r['code']==0

def delFav(http,aid,fid):
	t={'aid':aid,'fid':fid,'csrf':http.cookies['bili_jct']}
	r=http.post('https://api.bilibili.com/x/v2/fav/video/del',t,headers={'User-Agent':environment.user_agent})
	r=r.json()
	return r['code']==0

def addFavAuto(http,aid):
	t=getFolders(http)
	if t:
		t=t[0]
	else:
		t=addFolder(http)
	return addFav(http,aid,t)
