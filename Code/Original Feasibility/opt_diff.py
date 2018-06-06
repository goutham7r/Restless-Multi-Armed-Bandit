import itertools,copy

class function:
	def __init__(self,label,values):
		self.tau = 0
		self.values = values
		self.label = label
		self.diff=[]
		for i in range(len(values)-1):
			self.diff.append(self.values[i+1]-self.values[i])

	def pull(self):		#returns reward, resets tau
		ret=self.values[self.tau]
		self.tau=0
		return ret

	def get_rew_and_gain(self):
		return [self.values[self.tau], self.diff[self.tau]]
	
	def incr(self):		#increments tau
		self.tau+=1
		return self.tau

	def disp_func(self):		#prints function
		print "Function " + str(self.label) + ": "
		for i in range(len(self.values)):
			print str(i) + ": " + str(self.values[i])


class set_of_functions:
	def __init__(self,filename):
		self.f = []
		self.filename=filename
		with open(filename, "r") as fo:
			i=1
			for line in fo:
				(self.f).append(function(i,[int(x) for x in line.split()]))
				i+=1

	def print_functions(self):
		for f in self.f:
			f.disp_func()

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

	def brute_force(self,T): #finds optimum sequence and maximum reward by brute force
		max_rew=0;
		opt_seq=[]
		for i in itertools.product(range(len(self.f)+1), repeat=T):
			rew = self.apply_seq(i)
			if rew>max_rew:
				max_rew=rew
				opt_seq=i
		print "Brute Force: "
		print "Optimum sequence: ",opt_seq
		print "Maximum reward: ", max_rew
		return [opt_seq,max_rew]

	def find_best_seq(self, T):
		seq=[]
		rew=0
		for t in range(T):	
			seq.append(0)
			sum_gain=0
			rew_at_max_gain=0
			best_i=0
			gain=0
			for func in self.f:
				sum_gain+=(func.get_rew_and_gain())[1]
			max_gain=sum_gain
			for func in self.f:
				gain=sum_gain-(2*func.get_rew_and_gain()[1])
				if gain>max_gain or (gain==max_gain and func.get_rew_and_gain()[0]>rew_at_max_gain):
					seq[t]=func.label
					rew_at_max_gain=func.get_rew_and_gain()[0]
					best_i=func.label
			rew+=self.pull_i(best_i)[1]
		print "Using Algorithm: "
		print "Optimum sequence: ", seq
		print "Maximum reward: ", rew
		return [seq,rew]

def get_seq(): # gets sequence from the file
	#n = raw_input("Number of pulls: ")
	#filename = raw_input("Filename to get data: ")
	filename = "seq_bw.txt"
	seq = []
	with open(filename, "r") as fo:
		line=fo.readline()
		seq=[int(x) for x in line.split()]
	return seq 


f_all=set_of_functions("bw.txt")
f_all.print_functions()
seq=get_seq()
print "Sequence applied: ", seq
print "Total Reward: " + str(f_all.apply_seq(seq))
T = input("Enter number of pulls: ")
f_all.brute_force(T)
f_all.find_best_seq(T)