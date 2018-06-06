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
		
	def feasibility(self,tau_0,T,def_no):
		#define a feasibility value for each value of the function
		#ordered pairs stored as (tau,tau',feasibility value(tau'),reward)
		#tau'=tau-tau_0
		feas_t = [] 
		self.feas=[]
		self.length = len(self.values)
		#definition of feasibility is up for experimentation
		if def_no==1:
			for i in range(tau_0,self.length):
				(self.feas).append([i,i-tau_0,float("{:.5f}".format((self.values[i]*1.0/((i-tau_0)+1)))),self.values[i]])
				#(self.feas).append([i,i-tau_0,float("{:.5f}".format((self.values[i]*int(T/((i-tau_0)+1))))),self.values[i]])
			return self.feas
		elif def_no==2:
			for i in range(tau_0,self.length):
				(self.feas).append([i,i-tau_0,float("{:.5f}".format((self.values[i]*1.0/((i-tau_0)+T)))),self.values[i]])
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
		for i in self.data[T][tuple(initial_state)][0]:
			count+=1
			if count<=10:
				print i
		print "Number of optimum sequences: ", count
		#print "Maximum reward: ", self.data[T][tuple(initial_state)][1]
		return self.data[T][tuple(initial_state)][0], self.data[T][tuple(initial_state)][1]

	#following functions are for the feasibility algorithm
	def overall_feasibility(self,tau_0,T,def_no): #(function,tau,tau',feasibility value(tau'),reward)
		ov_feas=[]
		n=0
		for i in tau_0:
			if i>=0:
				n+=1
		N=len(tau_0)
		for func in self.f:
			label=[func.label]
			if tau_0[func.label]>=0 or func.label==0:
				for val in func.feasibility(tau_0[func.label],T,def_no):
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
					#if feasibilities are equal, return one with the lower tau' value
					best_entry = i
					high_reward = entry[4]
					high_tau = entry[2]
					low_next_rew= " "
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
									for m in range(j+1,len(feas_list)):
										if feas_list[m][0]==best_entry:
											low_next_rew=feas_list[m][4]
											break
								elif feas_list[j][2]==high_tau:
									for m in range(j+1,len(feas_list)):
										if feas_list[m][4]<low_next_rew:
											low_next_rew=feas_list[m][4]
											break
						else:
							break
					return feas_list[best_entry][0],feas_list[best_entry][1],feas_list[best_entry][4]  
			else:
				return entry[0],entry[1],entry[4] 
		return 0,0,0

	def Algorithm(self,T,tau_0,def_no,cur_index): #returns seq,rew,final_state
		#print "Entered function: T=",T,"tau_0=",tau_0, "cur_index=",cur_index
		seq=[]
		rew=0
		if T==0:
			return seq,rew,tau_0
		feas_list = self.overall_feasibility(tau_0,T,def_no)
		#print feas_list
		
		#pivot computation
		arm_pivot,tau_pivot,rew_pivot = self.best_possible(T,feas_list,tau_0)
		#print "Pivot: ",arm_pivot,tau_pivot,rew_pivot
		self.seq[cur_index+tau_pivot-tau_0[arm_pivot]] = arm_pivot
		self.print_seq_build()
		
		#Sequence 1 computation
		tau_0_s1 = copy.copy(tau_0)
		if arm_pivot>0:
			tau_0_s1[arm_pivot] = -1
		#print
		#print "start S1: ",tau_pivot-tau_0[arm_pivot],tau_0_s1,cur_index
		seq_s1,rew_s1,final_state_s1 = self.Algorithm(tau_pivot-tau_0[arm_pivot],tau_0_s1,def_no,cur_index)
		#print "end S1: ",seq_s1,rew_s1,final_state_s1
		
		#Sequence 2 computation
		for i in range(1,len(final_state_s1)):
			if final_state_s1[i]>=0:
				final_state_s1[i]+=1
		final_state_s1[arm_pivot]=0
		#print
		#print "start S2: ",T-tau_pivot+tau_0[arm_pivot]-1,final_state_s1,cur_index+tau_pivot-tau_0[arm_pivot]+1
		seq_s2,rew_s2,final_state = self.Algorithm((T-tau_pivot+tau_0[arm_pivot]-1),final_state_s1,def_no,cur_index+tau_pivot-tau_0[arm_pivot]+1)
		#print "end S2: ",seq_s2,rew_s2,final_state
		
		#Putting it together
		seq = seq_s1 + [arm_pivot] + seq_s2
		rew = rew_s1 + rew_pivot + rew_s2
		#print "Exited function: seq=",seq,"rew=",rew,"Final State: ",final_state
		return seq,rew,final_state

	def Optimum_Sequence(self,T):
		tau_0 = []
		for i in range(len(self.f)):
			tau_0.append(0)
		best_def=1
		best_approx=0
		approx=[]
		for def_no in range(1,2):	
			self.seq=[]
			for i in range(T):
				self.seq.append(-1)
			seq, rew, final_state = self.Algorithm(T,tau_0,def_no,0)
		print "Sequence: ",seq
		print "Optimum Sequences: "
		a, max_rew = self.dynamic(T)
		if max_rew>0:
			approx.append((rew*100.0/max_rew))
		else: 
			approx.append(100)
		print "Reward: ", rew, "Max Reward: ",max_rew, "Approximation Ratio: ",approx[0]
		feas_list = self.overall_feasibility(tau_0,T,1)		
		return approx[0],feas_list
			
	def print_seq_build(self):
		p = ""
		for a in self.seq:
			if a==-1:
				p = p + "_ "
			else:
				p= p + str(a) + " "
		print p


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
		approx,feas_list=f_all.Optimum_Sequence(T)
		if approx<worst:
			worst=approx
			worst_index=T
		if T>9:
			s+=approx
			c+=1
		data.append(approx)
		if T<=2:
			bound.append(100)
		else:
			bound.append((T-int((T-1)/2))*100.0/T)
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

f_all=set_of_functions("bw.txt")
T=input("Enter T: ")
sys.setrecursionlimit(100000)
graph_approx(T,f_all)
#f_all.print_functions(0)
#f_all.print_feas(len(f_all.f[0].values))
#seq=get_seq()
#print "Sequence: ", seq
#print "Total Reward: " + str(f_all.apply_seq(seq))
#f_all.brute_force(len(f_all.f[0].values))
#f_all.dynamic(len(f_all.f[1].values))