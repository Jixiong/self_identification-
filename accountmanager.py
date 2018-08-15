import sqlite3,pickle,io,threading

def nullCookie():
	f=io.BytesIO()
	pickle.dump({},f)
	return f.getvalue()

class __Accounts:
	def __init__(self,_conn,_cur):
		self.conn=_conn
		self.cur=self.conn.cursor()
		self.cur.execute(('create table if not exists accounts('
		'uid varchar(255),'
		'pwd varchar(255),'
		'access_key text default \'\','
		'cookie text,'
		'userinfo text default \'\','
		'ban integer default 0,'
		'lst_answer integer default 0,'
		'lst_video integer default 0,'
		'lst_chk_login integer default 0,'
		'lst_live_sign integer default 0,'
		'lst_chk_access_key integer default 0,'
		'lst_live_silver integer default 0'
		')'))
		self.cur.execute(('create table if not exists video_fav('
		'uid varchar(255),'
		'aid integer'
		')'))
		self.commit_cnt=0
		self.commit_lim=20
		self.lock=threading.RLock()
	
	def __del__(self):
		self.conn.commit()
		self.conn.close()
	
	def delayCommit(self):
		self.commit_cnt+=1
		if self.commit_cnt>=self.commit_lim:
			self.commit_cnt=0
			self.conn.commit()

	def getUser(self,uid):
		cur=self.conn.cursor()
		cur.execute("select * from accounts where uid=?",(uid,))
		for i in cur:return i

	def getUsers(self):
		cur=self.conn.cursor()
		cur.execute("select * from accounts")
		return cur

	def setPwd(self,uid,pwd):
		self.lock.acquire()
		self.cur.execute("update accounts set pwd=? where uid=?",(pwd,uid))
		self.conn.commit()
		self.lock.release()

	def setAuth(self,uid,cookie,access_key,commit=True):
		self.lock.acquire()
		self.cur.execute("update accounts set cookie=?,access_key=? where uid=?",(cookie,access_key,uid))
		if commit:self.conn.commit()
		self.lock.release()

	def setUser(self,uid,extra_args):
		self.lock.acquire()
		self.cur.execute("update accounts set userinfo=?,ban=?,lst_answer=?,lst_video=?,lst_chk_login=?,lst_live_sign=?,lst_chk_access_key=?,lst_live_silver=? where uid=?",extra_args+(uid,))
		self.delayCommit()
		self.lock.release()

	def addUser(self,uid,pwd,cookie=nullCookie(),access_key=''):
		self.lock.acquire()
		self.cur.execute("insert into accounts values(?,?,?,?,'',0,0,0,0)",(uid,pwd,access_key,cookie))
		self.conn.commit()
		self.lock.release()
	
	def addVideoRecord(self,t,uid,aid):
		self.lock.acquire()
		self.cur.execute("insert into %s values(?,?)"%t,(uid,aid))
		self.delayCommit()
		self.lock.release()
	
	def getVideoUsers(self,t,aid):
		self.lock.acquire()
		cur=self.conn.cursor()
		cur.execute("select * from %s where aid=?"%t,(aid,))
		res=[]
		for i in cur:
			res.append(i[0])
		self.lock.release()
		return res
	
	def commit(self):
		self.lock.acquire()
		self.conn.commit()
		self.lock.release()


def loadAccounts(filename):
	conn=sqlite3.connect(filename,check_same_thread=False)
	return __Accounts(conn,conn.cursor())
