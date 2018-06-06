import itertools,copy,sys,math
import numpy as np
import matplotlib.pyplot as plt
from operator import itemgetter, attrgetter, methodcaller

class function:
	def __init__(self,label,values):
		self.values = values
		self.label = label

	def apply_seq(self,seq): #returns reward without altering function
		state=0
		rew=0
		for i in seq:
			if i==0 or state>=len(self.values):
				rew+=0
				state+=1
			else:
				rew+=self.values[state]
				state=0
		return rew

	def brute_force(self,T):
		max_rew=0;
		seq=[]
		count=0
		for i in itertools.product(range(2), repeat=T):
			rew = self.apply_seq(i)
			if rew>max_rew:
				seq=[]
				max_rew=rew
				seq.append(i)
		return [seq,max_rew]

	def find_best_arm(self,state,i):
		if state>=len(self.values):
			rew_1=0
		else:
			rew_1=self.values[state]
		rew_0 = 0

		n_state_1=0
		n_state_0=state+1

		if i>1:	
			rew_1+=(self.data)[i-1][n_state_1][1]
			rew_0+=(self.data)[i-1][n_state_0][1]

		if rew_1>rew_0:
			max_rew=rew_1
			if i>1:
				seq = [self.label]+(self.data)[i-1][n_state_1][0]
			else:
				seq = [self.label]
		else:
			best_arm = [0]
			max_rew=rew_0
			if i>1:
				seq = [0]+(self.data)[i-1][n_state_0][0]
			else:
				seq = [0]
		return [seq,max_rew]

	def dynamic(self,T): #coordinates the dynamic programming algorithm
		self.data = {}
		initial_state = 0
		for i in range(1,T+1): #i stands for time remaining
			self.data[i] = {}
			for state in range(T-i+1):
				self.data[i][state] = self.find_best_arm(state,i)
			if i>1:
				del self.data[i-1]
		#print "Function "+str(self.label)+": "
		#print "Optimum sequence:",	self.data[T][initial_state][0]																																																																																																											
		#print "Maximum reward:", self.data[T][initial_state][1]
		num_played=0
		for i in self.data[T][initial_state][0]:
			if i==self.label:
				num_played+=1
		return [self.data[T][initial_state][0],self.data[T][initial_state][1],num_played]
		

class set_of_functions:
	def __init__(self,filename):
		self.f = []
		self.filename=filename
		self.f.append(function(0,[0]))
		with open(filename, "r") as fo:
			i=1
			for line in fo:
				(self.f).append(function(i,[int(x) for x in line.split()]))
				i+=1

	def apply_seq(self,seq): #returns reward without altering function
		original = set_of_functions(self.filename)
		rew=0
		k=1
		for i in seq:
			a=original.pull_i(i)
			k+=1
			rew+=a[1]
		return rew

	#The next four functions are used to implement the dynamic programming algortithm
	def find_valid_states(self,initial_state,T,time_left):
		t=T-time_left
		valid=[]
		#print "Time: ",t
		length = len(initial_state)
		if t==0:
			valid.append(initial_state)
		else:
			for i in itertools.product(range(t+1), repeat=length):
				zeros = sum(x==0 for x in i)
				count=0
				for x in range(length):
					for y in range(x+1,length):
						if i[x]==i[y] and i[x]!=t:
							count=1
							break
					if count>0:
						break
				if zeros<2 and count==0:
					valid.append(i)
					#print i,"Count: ", count,"Zeros: ", zeros
		#print t, len(valid)
		'''for x in valid:
			print x'''
		return valid

	def find_next_state(self,cur_state,arm_played):
		next_state=[]
		for i in range(1,len(cur_state)+1):
			if i==arm_played:
				next_state.append(0)
			else:
				next_state.append(cur_state[i-1]+1)
		#print next_state
		return next_state

	def state_valid(self,state):
		a=True
		for i in range(len(state)):
			if state[i]>=len(self.f[i+1].values):
				a=False
				break
		return a

	def find_best_arm(self,state,i):
		best_arm = [0]
		max_rew = 0
		prev = [0]
		seq=[]
		for func in self.f:
			if func.label==0 or state[func.label-1]>=len(func.values):
				rew=0
			else:
				rew=func.values[state[func.label-1]]
			if i>1:
				n_state=self.find_next_state(state,func.label)
				rew+=(self.data)[i-1][tuple(n_state)][1]
			if rew>max_rew:
					seq=[]
					best_arm = [func.label]
					max_rew=rew
					if i>1:
						for prev in (self.data)[i-1][tuple(n_state)][0]:
							seq.append(best_arm+prev)
					else:
						seq.append(best_arm)
			elif rew==max_rew:
					best_arm = [func.label]
					if i>1:
						for prev in (self.data)[i-1][tuple(n_state)][0]:
							seq.append(best_arm+prev)
					else:
						seq.append(best_arm)
		#print i,state,seq,max_rew
		return [[seq[0]],max_rew] #change this here to go back to seq

	def dynamic(self,T): #coordinates the dynamic programming algorithm
		self.data = {}
		#print "Dynamic Programming: "
		initial_state = []
		for i in range(len(self.f)-1):
			initial_state.append(0)
		count=0
		for i in range(1,T+1): #i stands for time remaining
			#print "Running, Time instants left to compute: ",T-i
			self.data[i] = {}
			for state in self.find_valid_states(initial_state,T,i):
				count+=1
				#print "This: ",state,self.find_best_arm(state,i)
				self.data[i][tuple(state)] = self.find_best_arm(state,i)
				#print "Data: ", self.data
			if i>1:
				del self.data[i-1]
			#print self.data
		'''for x in self.data:
			print x
			for y in self.data[x]:
				print y,': ',self.data[x][y]'''
		#print "Total number of states considered overall: " + str(count)
		#print "Optimum sequence(s): "
		count=0																																																																																																													
		'''for i in self.data[T][tuple(initial_state)][0]:
			count+=1
			if count<=10:
				print i'''
		#print "Number of optimum sequences: ", count
		#print "Maximum reward: ", self.data[T][tuple(initial_state)][1]
		return self.data[T][tuple(initial_state)][0], self.data[T][tuple(initial_state)][1]

	def Find_Ideal_Period(self,T):
		opt_seq,max_rew=self.dynamic(T)
		print "Optimum Seqenece:", opt_seq[0]
		per = []
		periods = []
		for i in range(len(self.f)):
			per.append(1)
			periods.append([])
		for arm in opt_seq[0]:
			periods[arm].append(per[arm])
			for k in range(len(self.f)):
				if k!=arm:
					per[k]+=1
				else:
					per[k]=1


		for i in range(len(periods)):
			print "Arm",i,": ",periods[i]
		
def get_seq(): # gets sequence from the file
	#n = raw_input("Number of pulls: ")
	#filename = raw_input("Filename to get data: ")
	filename = "seq.txt"
	seq = []
	with open(filename, "r") as fo:
		line=fo.readline()
		seq=[int(x) for x in line.split()]
	return seq

def draw_functions(T,f_all):
	k=len(f_all.f)-1
	data=[]
	X=[]
	m=0
	for func in f_all.f:
		if len(func.values)>m:
			m=len(func.values)
	T=min(T,m)
	for i in range(T):
		X.append(i)
	for i in range(0,k+1):
		data.append(copy.copy(X))
	for func in f_all.f:
		if func.label==0:
			continue
		else:
			for i in range(min(len(func.values),T)):
				data[func.label][i]=func.values[i]
	plt.title('Functions')
	plt.subplot(211)
	if k==1:
		plt.plot(X,data[1])
		for i in range(1,2):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	if k==2:
		plt.plot(X,data[1],X,data[2])
		for i in range(1,3):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	if k==3:
		plt.plot(X,data[1],X,data[2],X,data[3])
		for i in range(1,4):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	if k==4:
		plt.plot(X,data[1],X,data[2],X,data[3],X,data[4])
		for i in range(1,5):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	if k==5:
		plt.plot(X,data[1],X,data[2],X,data[3],X,data[4],X,data[5])
		for i in range(1,6):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	if k==6:
		plt.plot(X,data[1],X,data[2],X,data[3],X,data[4],X,data[5],X,data[6])
		for i in range(1,7):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	if k==7:
		plt.plot(X,data[1],X,data[2],X,data[3],X,data[4],X,data[5],X,data[6],X,data[7])
		for i in range(1,8):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)	
	if k==8:
		plt.plot(X,data[1],X,data[2],X,data[3],X,data[4],X,data[5],X,data[6],X,data[7],X,data[8])
		for i in range(1,9):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	if k==9:
		plt.plot(X,data[1],X,data[2],X,data[3],X,data[4],X,data[5],X,data[6],X,data[7],X,data[8],X,data[9])
		for i in range(1,10):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)	
	if k==10:
		plt.plot(X,data[1],X,data[2],X,data[3],X,data[4],X,data[5],X,data[6],X,data[7],X,data[8],X,data[9],X,data[10])
		for i in range(1,11):
			plt.text(i*T/(k+1),data[i][i*T/(k+1)],i)
	plt.ylabel('f(tau)')

def graph_approx(T_max, f_all):
	draw_functions(T_max,f_all)
	data=[]
	X=[]
	worst=100
	worst_index=0
	s=0
	c=0
	k=len(f_all.f)-1
	bound=[]
	violations=[]
	for T in range(1,T_max+1):
		print "Working, T=",T
		X.append(T)
		approx=f_all.Optimum_Sequence(T)
		if approx<worst:
			worst=approx
			worst_index=T
		if T>9:
			s+=approx
			c+=1
		data.append(approx)
		bound.append(100.0/k)
		if bound[T-1]>approx:
			violations.append([T,bound[T-1],approx])
		print
	ar=[]
	avg=[]
	if c>0:
		s=(s*1.0)/c
	for i in range(1,T_max+1):
		ar.append(worst)
		avg.append(s)
	print "Violations: "
	for i in violations:
		print i
	#plt.plot(X,bound_data)
	plt.subplot(212)
	plt.plot(X,data,X,ar,X,avg,X,bound)
	plt.axis([1, T_max, max(0,worst-30), 101])
	plt.title('Approximation Ratio vs Length of sequence')
	plt.text(2, worst-4,'Worst= '+"{:.2f}".format(worst) + " percent at T=" + str(worst_index))
	plt.text(2, worst-9,"Average approximation ratio from T=10 to T=" + str(T_max) +" is "+"{:.2f}".format(s)+" percent")
	#plt.text(5, 30,'Worst Def 2= '+"{:.2f}".format(worst[1]) + " percent at T=" + str(worst_index[1]))
	#plt.text(5, 40,"Average Def 2 approximation ratio from T=10 to T=" + str(T_max) +" is "+"{:.2f}".format(s1)+" percent")
	plt.xlabel('T')
	plt.ylabel('Approximation Ratio')
	plt.grid(True)
	plt.show()

def Ideal_Period(T,f_all):
	for i in range(T,T+1):
		f_all.Find_Ideal_Period(T)

f_all=set_of_functions("bw.txt")
T=input("Enter T: ")
#sys.setrecursionlimit(100000)
Ideal_Period(T,f_all)
#graph_approx(T,f_all)