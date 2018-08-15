import sys

to_char=['X' for i in range(1111)]
to_char[152]='+'
to_char[4]='-'
to_char[950]='0'
to_char[927]='0'
to_char[466]='1'
to_char[451]='1'
to_char[439]='2'
to_char[626]='3'
to_char[651]='3'
to_char[411]='4'
to_char[404]='4'
to_char[424]='4'
to_char[588]='5'
to_char[532]='5'
to_char[855]='6'
to_char[786]='6'
to_char[390]='7'
to_char[365]='7'
to_char[885]='8'
to_char[908]='8'
to_char[910]='9'
to_char[863]='9'

def get(img):
	t=img.convert('L').load()
	v=[[0 for i in range(20)]for j in range(60)]
	for j in range(20):
		for i in range(60):
			sum=0
			for k in range(2):
				for l in range(2):
					sum+=t[i*2+k,j*2+l]
			v[i][j]=1 if sum<512 else 0
			#if sum<512:
			#	sys.stdout.write('O')
			#else:
			#	sys.stdout.write(' ')
		#print
	res=''
	lst=-1
	for i in range(60):
		flag=True
		for j in range(20):
			if v[i][j]:flag=False
		if flag:
			if lst+1!=i:
				sum=0
				for k in range(lst+1,i):
					cnt=0
					for j in range(20):
						cnt+=v[k][j]
					sum+=cnt*cnt
				res+=to_char[sum]
				#if to_char[sum]=='X':print '--------------------------------'
				#print sum
			lst=i
	#print res
	if res.find('X')==-1:return eval(res)
	return False