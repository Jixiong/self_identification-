import json
import accountmanager
import login
import save_cookie
import log
import environment

ac=accountmanager.loadAccounts('accounts.db')
us=[]

def loadAll():
	for i in ac.getUsers():
		http=save_cookie.loadSession(i[3])
		http.headers.update({'User-Agent':environment.user_agent})
		if i[4]=='':
			ui=''
		else:
			ui=json.loads(i[4])
		us.append({
			'uid':i[0],
			'pwd':i[1],
			'http':http,
			'userinfo':ui,
			'access_key':i[2],
			'ban':i[5],
			'lst_answer':i[6],
			'lst_video':i[7],
			'lst_chk_login':i[8],
			'lst_live_sign':i[9],
			'lst_chk_access_key':i[10],
			'lst_live_silver':i[11],
			'to_ans':'',
			'ans_time':0,
		})

def saveUser(u):
	if u['userinfo']=='':
		t=''
	else:
		t=json.dumps(u['userinfo'])
	ac.setUser(u['uid'],(t,u['ban'],u['lst_answer'],u['lst_video'],u['lst_chk_login'],u['lst_live_sign'],u['lst_chk_access_key'],u['lst_live_silver']))

def saveHttp(i,commit=True):
	ac.setAuth(i['uid'],save_cookie.saveSession(i['http']),i['access_key'],commit)

def checkLevel(u):
	return u['userinfo']['level_info']['current_level']>0

def checkLevelI(u):
	return u['level_info']['current_level']>0
