import random

def generate(N,T,filename):
	f = open(filename+".txt", 'w')
	f.truncate()
	for n in range(N):
		line=""
		t_extrema = random.randint(1,T)
		rand = random.randint(1,100)
		if rand<51: #1 for increasing first, -1 for decreasing first
			max_or_min=-1
			number = random.randint(0,100)
		else:
			max_or_min=1
			number = random.randint(50,150)
		line=line+str(number)+" "
		sign = 1 #sign is 1 until extremum is reached, then -1 after that
		print "Function", n,": ", max_or_min, t_extrema
		for t in range(2,T+1):
			if t>t_extrema:
				sign=-1
			if sign*max_or_min==1:
				number = random.randint(number, number + 30) #maximum positive derivative=30
			else:
				if number>0:
					number = random.randint(max(number-30,0), number) #maximum negative derivative=10
				elif number==0 and max_or_min==-1:
					t_extrema=t
			if t==T:
				line=line+str(number)
			else:
				line=line+str(number)+" "
		f.write(line)
		if n<N:
			f.write("\n")
			
N = input("Enter number of bitonic functions to generate: ")
T = input("Enter length of each function to generate: ")
filename = raw_input("Enter filename to create: ")
generate(N,T,filename)