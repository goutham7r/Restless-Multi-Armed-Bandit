import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def nCr(n,r):
	f=math.factorial
	if r>n:
		return 0
	else:
		return f(n)/f(r)/f(n-r)

def data_point(k,T):
	f=math.factorial
	sum=0
	for t in range(1,T+1):	
		for n in range(k+1):
			sum = sum + nCr(t-1,k-n)*f(k)/f(n)
	return sum 

def data_plot_T(k1,k2=0):
	data=[]
	if k2==0:
		k2=k1
	for k in range(k1,k2+1):
		X=[]
		data=[]
		data1=[]
		total=0	
		for T in range(1,100):
			X.append(T)
			total=total+T**k
			print T,total,data_point(k,T)
			data.append(data_point(k,T))
			data1.append(total)
		plt.plot(X,data,X,data1)
	plt.title('k='+str(k1))
	plt.xlabel('T')
	plt.ylabel('Number of states')
	plt.show()
	plt.show()

def data_plot_k(k1,k2):
	data=[]
	X=[]
	for k in range(k1,k2+1):
		X.append(k)
		data.append(data_point(k,50))
	plt.plot(X,data)
	plt.title('k='+str(k1))
	plt.xlabel('T')
	plt.ylabel('Number of states')
	plt.show()

def data_3D_plot(k1,k2,T1,T2):
	X=[]
	Y=[]
	Z=[]
	fig=plt.figure()
	ax=fig.add_subplot(111,projection='3d')
	for k in range(k1,k2+1):
		X.append(k)
	for T in range(T1,T2+1):
		Y.append(T)
	XX, YY = np.meshgrid(X,Y)
	ZZ=[]
	for i in range(len(XX)):
		Z=[]
		for j in range(len(YY)):
			Z.append(data_point(XX[i][j],YY[i][j]))
		ZZ.append(Z)
	ax.plot_surface(XX,YY,Z)
	ax.set_xlabel('K')
	ax.set_ylabel('T')
	ax.set_zlabel('Number of states')
	plt.show()

k1 = raw_input("Enter k: ")
#k2 = raw_input("Enter end k: ")
data_plot_T(int(k1))
#data_plot_k(int(k1),int(k2))
#data_3D_plot(1,30,1,30)
