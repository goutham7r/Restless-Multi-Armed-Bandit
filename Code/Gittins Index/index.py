import itertools,copy,math,random
import sys
import matplotlib.pyplot as plt

class function:
	def __init__(self,label,values):
		self.values = values
		self.label = label
		
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
		self.tau_0 = []
		self.K = len(self.f)-1
		for i in range(self.K):
			self.tau_0.append(0)

	def apply_seq(self,seq):
		state=copy.copy(self.tau_0)
		rew=0
		#print seq
		for arm in seq:
			rew = rew + self.f[arm].values[state[arm]]
			#print rew
			for i in range(1,self.K):
				state[i]+=1
			state[arm]=0
		return rew

	def brute_force(self,T): #finds optimum sequences and maximum reward by brute force
		max_rew=0;
		seq=[]
		count=0
		for i in itertools.product(range(len(self.f)), repeat=T):
			rew = self.apply_seq(i)
			if rew>max_rew:
				seq=i
				max_rew=rew
		#print "Brute Force: "
		#print "Optimum sequence: ",seq
		#print "Maximum reward: ", max_rew
		return seq,max_rew

	#next 4 functions find overall optimum sequence
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
		cur_state=list(cur_state)
		for i in range(len(cur_state)):
			cur_state[i]+=1
		if arm_played>0:
			cur_state[arm_played-1]=0
		return cur_state

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
		return [seq,max_rew]

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
		count=1
		'''for i in self.data[T][tuple(initial_state)][0]:
			count+=1
			if count<=10:
				print i'''
		#print "Number of optimum sequences: ", count
		#print "Maximum reward: ", self.data[T][tuple(initial_state)][1]
		return self.data[T][tuple(initial_state)][0][0], self.data[T][tuple(initial_state)][1]

	def opt_period(self,arm,W):
		temp=[]
		for i in range(len(self.f[arm].values)):
			temp.append([i,(((1.0*i*W)+self.f[arm].values[i])/(i+1.0))])
		temp=sorted(temp, key=lambda temp: temp[1],reverse=True)
		return temp[0][0]

	#find the minimum reward such that I want to wait further to play the arm
	def find_arm_index(self,arm,cur_state,epsilon):
		step=16.0
		W=0					#W is reward obtained on playing the zero arm
		state = True		#True means we are decreasing V
		count=0
		while step>epsilon/2:
			count+=1
			opt = self.opt_period(arm,W)
			if opt<=cur_state:
				if state:
					step/=2
				W+=step
				state=False
			else:
				if not state:
					step/=2
				W-=step
				state=True

		check = self.opt_period(arm,W)
		if check>cur_state:
			W-=step
		elif check<cur_state:
			W+=step
		
		'''
		for delta in range(-5,6):
			print W+(delta/100.0), self.opt_period(arm,W+(delta/100.0))
		'''

		#print "Index of ",cur_state,": ",W
		return W

	def arm_index_algorithm(self,T):
		state=self.tau_0
		epsilon=0.001
		seq=[]
		rew=0

		for t in range(1,T+1):
			#print "T=",t
			indices=[[0,0]]
			for i in range(0,self.K):
				#print "Arm",i+1
				indices.append([i+1,self.find_arm_index(i+1,state[i],epsilon)])
			indices=sorted(indices, key=lambda indices: indices[1],reverse=False)
			#print indices
			arm_to_play = indices[0][0]
			seq.append(arm_to_play)
			if(arm_to_play>0):
				rew+=self.f[arm_to_play].values[state[arm_to_play-1]]
			state = self.find_next_state(state,arm_to_play)
			#print seq,state,rew
			#print

		print "Obtained:",seq,rew
		
		opt_seq,max_rew = self.dynamic(T)
		approx = rew*100.0/max_rew

		print "Optimum:",opt_seq,max_rew
		print "Approximation Ratio:",approx
		
		return approx

	def arm_index_algorithm_analyze(self,Time): 
		print "Working, please wait..."
		approx = [0]

		for T in range(1,Time+1):
			print "T=",T
			approx.append(self.arm_index_algorithm(T))
			print

		plt.plot(range(Time+1),approx)
		plt.axis([1, Time, 0, 101])
		plt.title('Approximation Ratio vs Length of sequence')
		plt.xlabel('Length of Sequence')
		plt.ylabel('Approximation Ratio')
		plt.grid(True)
		plt.show()


f_all=set_of_functions("arms.txt")
#f_all.arm_index_algorithm(20)
T=input("Enter T: ")
f_all.arm_index_algorithm_analyze(T)
