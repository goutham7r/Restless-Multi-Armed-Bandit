import itertools,copy,math
import sys

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

	def pull(self):		#returns reward, resets tau
		if self.label==0:
			ret=0
		else:
			ret=self.values[self.tau]
		self.tau=0
		return ret

	def incr(self):		#increments tau
		self.tau+=1
		return self.tau
		
	def feasibility(self,tau_0,T,n):
		#define a feasibility value for each value of the function
		#ordered pairs stored as (tau,tau',feasibility value(tau'),reward)
		#tau'=tau-tau_0
		feas_t = [] 
		self.feas=[]
		self.length = len(self.values)
		#definition of feasibility is up for experimentation
		for i in range(tau_0,self.length):
			(self.feas).append([i,i-tau_0,float("{:.5f}".format((self.values[i]*n*1.0/(((i-tau_0)+T)**2)))),self.values[i]])			
		return self.feas

	def disp_feas(self,T):		#prints feasibility values of function
		self.feasibility(T)
		print "Function " + str(self.label) + ": "
		for i in range(len(self.feas)):
			print str(i) + ": tau=" + str(self.feas[i][0]) + ", value: " + str(self.values[self.feas[i][0]]) + ", feasibility= " + str(self.feas[i][1])

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

	def print_functions(self,a): #a=0 for displaying function values, otherwise for displaying feasibility values
		if a==0:	
			for func in self.f:
				func.disp_func()
		else:
			for func in self.f:
				func.disp_feas(a)

	def pull_i(self,i): #returns ret=[tau_i,f_i(tau_i)]
		if i==0:
			ret = [0,0]
		else:
			ret = []
		for func in self.f:
			if func.label==i:
				ret.append(func.tau)
				ret.append(func.pull())
			else:
				func.incr()
		return ret

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
		return a #redundant function

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
		print "Dynamic Programming: "
		initial_state = []
		for i in range(len(self.f)-1):
			initial_state.append(0)
		count=0
		for i in range(1,T+1): #i stands for time remaining
			print "Running, Time instants left to compute: ",T-i
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
		print "Total number of states considered overall: " + str(count)
		print "Optimum sequence(s): "
		count=1
		for i in self.data[T][tuple(initial_state)][0]:
			count+=1
			if count<=10:
				print i
		print "Number of optimum sequences: ", count
		print "Maximum reward: ", self.data[T][tuple(initial_state)][1]
		return self.data[T][tuple(initial_state)][0], self.data[T][tuple(initial_state)][1]

	def brute_force(self,T): #finds optimum sequences and maximum reward by brute force
		max_rew=0;
		seq=[]
		count=0
		print "Total Possibilities to be explored: " + str((len(self.f))**T)
		for i in itertools.product(range(len(self.f)), repeat=T):
			if(count%10000==0):
				print count
			count+=1
			rew = self.apply_seq(i)
			if rew>max_rew:
				seq=[]
				max_rew=rew
				seq.append(i)
			elif rew==max_rew:
				seq.append(i)
		print "Brute Force: "
		print "Optimum sequence(s): "
		count = 1
		i = len(seq)-1
		while i>=0:
			print seq[i],count
			count+=1
			i-=1;
		print "Maximum reward: ", max_rew
		return [seq,max_rew]

	#following functions are for the feasibility algorithm
	def overall_feasibility(self,tau_0,T): #(function,tau,tau',feasibility value(tau'),reward)
		ov_feas=[]
		n=0
		for i in tau_0:
			if i>=0:
				n+=1
		for func in self.f:
			label=[func.label]
			if tau_0[func.label]>=0:
				for val in func.feasibility(tau_0[func.label],T,n):
					if val[1]<T:
						ov_feas.append(label+val)
		ov_feas.sort(key=lambda x:x[3], reverse=True)
		self.ov_feas = ov_feas
		return ov_feas

	def print_feas(self,T):
		self.overall_feasibility(T)
		print "[function, tau, tau', feasibility, reward]"
		for i in self.ov_feas:
			print i

	def best_possible(self,T,feas_list,tau_0): #returns arm_pivot,tau_pivot,rew_pivot
		for i in range(len(feas_list)):
			entry=feas_list[i]
			if tau_0[entry[0]]==-1:
				continue
			if entry[1]<tau_0[entry[0]]:
				continue
			if (i+1)<len(feas_list):
				if entry[3]>feas_list[i+1][3]:
					return entry[0],entry[1],entry[4]
				else:
					#if feasibilities are equal, return one with highest reward
					#if rewards are equal, return one with the larger tau' value
					#if tau' values are equal, return one which has a higher reward on the next step of difference
					best_entry = i
					high_reward = entry[4]
					high_tau = entry[2]
					high_next_rew=0
					for j in range(i+1,len(feas_list)):
						if entry[3]==feas_list[j][3]: 
							if feas_list[j][4]>high_reward:
								high_reward=feas_list[j][4]
								best_entry=j
								high_tau=feas_list[j][2]
							elif high_reward==feas_list[j][4]:
								if feas_list[j][2]>high_tau:
									best_entry=j
									high_tau=feas_list[j][2]
									if (j+1)<len(feas_list):
										high_next_rew=feas_list[j+1][4]
								elif feas_list[j][2]==high_tau:
									if (j+1)<len(feas_list):
										if feas_list[j+1][4]>high_next_rew:
											best_entry=j
											high_next_rew=feas_list[j+1][4]
						else:
							break
					return feas_list[best_entry][0],feas_list[best_entry][1],feas_list[best_entry][4]  
			else:
				return entry[0],entry[1],entry[4] 
		return 0,0,0


	def Algorithm(self,T,tau_0): #returns seq,rew,final_state
		#print "Entered function: T=",T,"tau_0=",tau_0
		seq=[]
		rew=0
		if T==0:
			return seq,rew,tau_0
		feas_list = self.overall_feasibility(tau_0,T)
		#print feas_list
		
		#pivot computation
		arm_pivot,tau_pivot,rew_pivot = self.best_possible(T,feas_list,tau_0)
		#print "Pivot: ",arm_pivot,tau_pivot,rew_pivot
		
		#Sequence 1 computation
		tau_0_s1 = copy.copy(tau_0)
		tau_0_s1[arm_pivot] = -1
		#print
		#print "start S1: ",tau_pivot-tau_0[arm_pivot],tau_0_s1
		seq_s1,rew_s1,final_state_s1 = self.Algorithm(tau_pivot-tau_0[arm_pivot],tau_0_s1)
		#print "end S1: ",seq_s1,rew_s1,final_state_s1

		#Sequence 2 computation
		for i in range(len(final_state_s1)):
			if final_state_s1[i]>=0:
				final_state_s1[i]+=1
		final_state_s1[arm_pivot]=0
		#print
		#print "start S2: ",T-tau_pivot+tau_0[arm_pivot]-1,final_state_s1
		seq_s2,rew_s2,final_state = self.Algorithm((T-tau_pivot+tau_0[arm_pivot]-1),final_state_s1)
		#print "S2: ",seq_s2,rew_s2,final_state
		
		#Putting it together
		seq = seq_s1 + [arm_pivot] + seq_s2
		rew = rew_s1 + rew_pivot + rew_s2
		#print "Exited function: seq=",seq,"rew=",rew,"Final State: ",final_state
		return seq,rew,final_state

	def Optimum_Sequence(self,T):
		tau_0 = []
		for i in range(len(self.f)):
			tau_0.append(0)
		seq, rew, final_state = self.Algorithm(T,tau_0)
		print
		print "Using the feasibility algorithm: "
		print "Sequence: ", seq
		print "Reward: ", rew
		print
		print "Optimum: "
		a, max_rew = self.dynamic(T)
		print
		print "Approximation ratio: ", (rew*100.0/max_rew), " %"

def get_seq(): # gets sequence from the file
	#n = raw_input("Number of pulls: ")
	#filename = raw_input("Filename to get data: ")
	filename = "seq.txt"
	seq = []
	with open(filename, "r") as fo:
		line=fo.readline()
		seq=[int(x) for x in line.split()]
	return seq


f_all=set_of_functions("bw.txt")
T=input("Enter T: ")
sys.setrecursionlimit(2*T+1)
#print sys.getrecursionlimit()
f_all.Optimum_Sequence(T)
#f_all.print_functions(0)
#f_all.print_feas(len(f_all.f[0].values))
#seq=get_seq()
#print "Sequence: ", seq
#print "Total Reward: " + str(f_all.apply_seq(seq))
#f_all.brute_force(len(f_all.f[0].values))
#f_all.dynamic(len(f_all.f[1].values))