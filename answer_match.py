import os,threading
import log
import environment
from subprocess import Popen,PIPE

lock=threading.RLock()
plock=threading.RLock()

def calLCS(a,b):
	a=list(a);b=list(b)
	n=len(a);m=len(b)
	dp=[[0 for j in xrange(m+1)]for i in xrange(n+1)]
	for i in xrange(1,n+1):
		for j in xrange(1,m+1):
			dp[i][j]=max(dp[i-1][j],dp[i][j-1])
			if i and j and(a[i-1]==b[j-1]):
				dp[i][j]=dp[i-1][j-1]+1
	return dp[n][m]

def getBestAns1(x):
	global q
	plock.acquire()
	log.log('get best ans')
	plock.release()
	lock.acquire()
	score=-1
	x=map(unicode,x)
	for y in q:
		t=calLCS(x[0],y[0])
		for i in range(1,5):
			v=0
			for j in range(1,5):
				v=max(v,calLCS(x[i],y[j]))
			t+=v
		if t>score:
			score=t
			best=y
	lock.release()
	if score==-1:return 0
	score=-1;ans=0
	for i in range(1,5):
		t=calLCS(x[i],best[5])
		if t>score:
			score=t
			ans=i
	if score<=0:return 0
	return ans

def getBestAns2(x):
	global q,qs
	plock.acquire()
	log.log('get best ans')
	plock.release()
	lock.acquire()
	t=x[0]+','+x[1]+','+x[2]+','+x[3]+','+x[4]
	cmd='answer_match'
	if not environment.is_windows:
		cmd='./'+cmd
	p=Popen(cmd,stdin=PIPE,stdout=PIPE)
	p.stdin.write((t+'\n'+qs).encode('utf-8','ignore'))
	p.stdin.close()
	res=int(p.stdout.readline())
	lock.release()
	return res

def getBestAns(x):
	return getBestAns2(x)

q=[]
with open('answers.txt','r') as f:
	t=f.readlines()
	qs=''
	for i in t:
		qs+=i.decode('utf-8')
		#q.append(i.decode('utf-8'))
		v=i.decode('utf-8').strip('\n').strip('\r').split(',')
		if len(v)==6:q.append(v)

'''
x=[]
for i in range(5):
	x.append(raw_input().decode('gbk'))
print getBestAns(x)
'''
