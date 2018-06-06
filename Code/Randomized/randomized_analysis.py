import itertools,copy,math,random
import sys
import matplotlib.pyplot as plt

def seq_state_count(seq,K):
	state=0
	count=[]
	for i in range(len(seq)):
		count.append(0)
	#print "Sequence:",seq
	for arm in seq:
		#print "Arm:",arm
		if arm==0:
			count[state]+=1
			state=0
		else:
			state+=1
	'''for i in count:
			print i'''
	return count



def brute_force(K,T):
	for t in range(1,T+1):
		count=[]
		for j in range(t):
			count.append(0)
		for i in itertools.product(range(K+1),repeat=t):
			count = map(sum, zip(copy.copy(count),seq_state_count(i,K)))
		print count

#seq_state_count([0,1,2,2,1,0],3)
for i in range(1,6):
	print "K=",i
	brute_force(i,7)
	