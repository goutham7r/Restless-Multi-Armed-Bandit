import itertools,copy,math,random
import sys
import matplotlib.pyplot as plt

class function:
	def __init__(self,label,values):
		self.tau = 0
		self.values = values
		self.label = label
		
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
		self.K = len(self.f)
		for i in range(self.K):
			self.tau_0.append(0)

	def print_functions(self,a): #a=0 for displaying function values, otherwise for displaying feasibility values
		for func in self.f:
			func.disp_func()

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

	#following functions are for the non-deterministic algorithm
	def get_weights(self,tau,def_no):
		#definition 1
		if def_no==1:
			weights=[0]
			for i in range(1,self.K):
				if len(self.f[i].values)<=tau[i]:
					weights.append(0)
				else:
					weights.append(self.f[i].values[tau[i]])
		elif def_no==2:
			weights=[]
			for i in range(self.K):
				weights.append(10)
		return weights

	#single test for T=T
	def Non_deter(self,T,def_no):
		tau = copy.copy(self.tau_0)
		seq = []
		rew = 0

		print "Running algorithm:"
		for t in range(1,T+1):	
			weights = self.get_weights(tau,def_no)
			rnd = random.random() * sum(weights)
			r=rnd
			for i, w in enumerate(weights):
				rnd-=w
				if rnd<0:
					arm=i
					break
			seq.append(arm)
			if len(self.f[arm].values)<=tau[arm]:
				rew += 0
			else:
				rew+= self.f[arm].values[tau[arm]]
			for i in range(0,self.K):
				if i==arm:
					tau[i]=0
				else:
					tau[i]+=1
			print "T=",t,"Weights:",weights,"Random:",'{0:.5g}'.format(r)
			print "Arm:",arm,"Reward:",rew,"Tau:",tau

		print
		print "Working, please wait..."
		opt_seq, max_rew = self.dynamic(T)
		print "Sequence:", seq, "	Reward:", rew
		print "Optimum:"
		print "Sequence:", opt_seq[0], "	Reward:", max_rew
		print "Approximation ratio: ", '{0:.5g}'.format(rew*100.0/max_rew), " %"
		return (rew*100.0/max_rew) #run it once 

	#average of N tests for T=T
	def avg(self,T,N,def_no):
		print "Working, please wait..."
		opt_seq, max_rew = self.dynamic(T)
		approx=[]
		high_rew = 0
		high_seq = []
		for n in range(N):
			tau = copy.copy(self.tau_0)
			seq = []
			rew = 0

			for t in range(1,T+1):
				weights = self.get_weights(tau,def_no)	
				rnd = random.random() * sum(weights)
				r=rnd
				for i, w in enumerate(weights):
					rnd-=w
					if rnd<0:
						arm=i
						break
				seq.append(arm)
				if len(self.f[arm].values)<=tau[arm]:
					rew += 0
				else:
					rew+= self.f[arm].values[tau[arm]]
				for i in range(0,self.K):
					if i==arm:
						tau[i]=0
					else:
						tau[i]+=1
			if rew>high_rew:
				high_rew = rew
				high_seq = seq
			approx.append((rew*100.0/max_rew))
			print "Test No",(n+1),"		Approximation Ratio:",'{0:.5g}'.format(approx[n])
		print "Average Performance:",'{0:.5g}'.format(sum(approx)/float(len(approx)))
		print "Best Performance:", '{0:.5g}'.format(high_rew*100.0/max_rew), " with sequence:",high_seq

	#graph of average of N tests for T=1,2,....,T
	def avg_T(self,Time,N,def_no): 
		print "Working, please wait..."
		approx = [0]
		best = [0]
		for T in range(1,Time+1):
			opt_seq, max_rew = self.dynamic(T)
			approx.append(0)
			high_rew = 0
			high_seq = []

			for n in range(N):
				tau = copy.copy(self.tau_0)
				seq = []
				rew = 0
				for t in range(1,T+1):
					weights = self.get_weights(tau,def_no)
					rnd = random.random() * sum(weights)
					for i, w in enumerate(weights):
						rnd-=w
						if rnd<0:
							arm=i
							break
					seq.append(arm)
					if len(self.f[arm].values)<=tau[arm]:
						rew += 0
					else:
						rew+= self.f[arm].values[tau[arm]]
					for i in range(0,self.K):
						if i==arm:
							tau[i]=0
						else:
							tau[i]+=1
				approx[T]+= rew*100.0/max_rew
				#print rew,seq,high_rew
				if rew>high_rew:
					high_rew = rew
					high_seq = seq
			approx[T]/=N
			print "T=",T,": Average:",'{0:.5g}'.format(approx[T]),"%", "Best:", '{0:.5g}'.format(high_rew*100.0/max_rew)
			print "Our Best sequence:",high_seq
			print "Optimum:",opt_seq
			best.append(high_rew*100.0/max_rew)
		plt.plot(range(Time+1),approx,range(Time+1),best)
		plt.axis([1, Time, 0, 101])
		plt.title('Average Approximation Ratio vs Length of sequence')
		plt.text(2, 90,"N="+str(N))
		plt.xlabel('Length of Sequence')
		plt.ylabel('Approximation Ratio')
		plt.grid(True)
		plt.show()
 


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

print "Select option: "
print "1. Single time T"
print "2. N times T"
print "3. N times from 1 to T with graph"
op = input("Enter option: ")
T=input("Enter T: ")
if op in (2,3):
	N=input("Enter N: ")
if op==1:
	f_all.Non_deter(T,2)
elif op==2:
	f_all.avg(T,N,2)
elif op==3:
	f_all.avg_T(T,N,1)
else:
	sys.exit(0)

'''
Definitons:
1. Proportional to reward. 0 for zero arm.
2. Equal probability for all
'''

#sys.setrecursionlimit(2*T+1)
#print sys.getrecursionlimit()
#f_all.print_functions(0)
#f_all.print_feas(len(f_all.f[0].values))
#seq=get_seq()
#print "Sequence: ", seq
#print "Total Reward: " + str(f_all.apply_seq(seq))
#f_all.brute_force(len(f_all.f[0].values))
#f_all.dynamic(len(f_all.f[1].values))