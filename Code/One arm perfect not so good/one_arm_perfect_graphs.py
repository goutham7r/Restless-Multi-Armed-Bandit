import itertools,copy,sys,math
import numpy as np
import matplotlib.pyplot as plt

class function:
	def __init__(self,label,values):
		self.tau = 0
		self.values = values
		self.label = label
		self.feas=[]
		
	def disp_func(self):		#prints function
		print "Function " + str(self.label) + ": "
		for i in range(len(self.values)):
			print str(i) + ": " + str(self.values[i])
		
	def feasibility(self,T,best_so_far):
		feas_t = [] 
		self.feas=[]
		self.length = len(self.values)
		for i in range(min(self.length,T)):
			max_rew=0
			for j in range(1,int(T/(i+1))+1): #find best number of ways to play the arm
				rew = self.values[i]*j+best_so_far[T-j*(i+1)][0]
				if rew>max_rew:
					max_rew=rew
					n=j
			(self.feas).append([i,max_rew,n])
		self.feas.sort(key=lambda x:x[1], reverse=True)
		return self.feas

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

	def print_functions(self):
		for func in self.f:
			func.disp_func()

	def apply_seq(self,seq): #returns reward without altering function
		original = set_of_functions(self.filename)
		rew=0
		k=1
		for i in seq:
			a=original.pull_i(i)
			k+=1
			rew+=a[1]
		return rew

	#The next five functions are used to implement the dynamic programming algortithm
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
				print i
		print "Number of optimum sequences: ", count'''
		#print "Maximum reward: ", self.data[T][tuple(initial_state)][1]
		return self.data[T][tuple(initial_state)][0], self.data[T][tuple(initial_state)][1]

	def Optimum_Sequence(self,T):
		best_t = [] #stores (reward, sequence)
		best_t.append([0,[]])
		for t in range(1,T+1):
			feas = self.f[1].feasibility(t,best_t) # stores (tau, total reward)
			best=feas[0][0]
			rew=feas[0][1]
			n=feas[0][2]
			seq=[]
			for i in range(best):
				seq.append(0)
			seq.append(1)
			opt_seq=[]
			for i in range(n):
				opt_seq = opt_seq + seq
			rem = t%(best+1)
			best_t.append([rew,opt_seq+best_t[rem][1]])
			#print best_t
		return best_t

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
	K=len(f_all.f)-1
	for t in range(T_max+1):
		X.append(t)
	data.append(100)
	for i in range(1,K+1):
		print
		print "Function",i,": "

		f = open("f_k.txt", 'w')
		s=""
		for elem in f_all.f[i].values:
			s=s+str(elem)+" "
		s=s[:-1]
		f.truncate()
		f.write(s)
		f.close()
		f_temp=set_of_functions("f_k.txt")
		our_best = f_temp.Optimum_Sequence(T_max)
		for t in range(1,T_max+1):
			print
			print "Working, T = "+str(t)+":"
			seq,opt_rew=f_temp.dynamic(t)
			print "Best Sequence:", seq[0],"with Reward=",opt_rew
			print "This Sequence:", our_best[t][1],"with Reward=",our_best[t][0]
			approx = 100.0 * our_best[t][0]/opt_rew
			print "Approximation Ratio:",approx
			data.append(approx)
	plt.subplot(212)
	plt.plot(X,data)
	plt.axis([0, T_max, 90, 101])
	plt.title('Approximation Ratio vs Length of sequence')
	plt.xlabel('T')
	plt.ylabel('Approximation Ratio')
	plt.grid(True)
	plt.show()

f_all=set_of_functions("bw.txt")
T=input("Enter T: ")
sys.setrecursionlimit(100000)
graph_approx(T,f_all)