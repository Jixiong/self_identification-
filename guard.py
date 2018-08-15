import subprocess,time,log

while True:
	pid=subprocess.Popen('python main.py'.split()).pid
	time.sleep(10800)
	subprocess.Popen(('kill %d'%pid).split())
	log.log('-------------------------- Main Program Exited --------------------------')
	log.log('------------------------------ Sleep 120s -------------------------------')
	time.sleep(120)
