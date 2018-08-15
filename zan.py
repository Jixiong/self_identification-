import json,time,urllib,random
import log

def addZan(http,conf,count):
	if count==1:
		url='https://api.bilibili.com/x/v2/reply/action'
	else:
		url='https://api.bilibili.com/x/v2/reply/hate'
	data={
		'action':1,
		'csrf':http.cookies['bili_jct'],
	}
	data.update(conf.copy())
	r=http.post(url,data=data,headers={'User-Agent':environment.user_agent})
	print r.text
	r=r.json()
	return r['code']==0