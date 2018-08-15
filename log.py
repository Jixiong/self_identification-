import threading,time,sys

f=open('log.txt','w')
#f=sys.stdout

lock=threading.RLock()

def log(x,t='Info'):
	if type(x) is unicode:
		x=x.encode('gbk','ignore')
	if not type(x) is str:
		x=str(x)
	tm=time.strftime('%H:%M:%S')
	lock.acquire()
	f.write('['+tm+'] ['+t+'] '+x+'\n')
	f.flush()
	lock.release()
