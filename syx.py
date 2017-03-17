import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize
from numpy import *


###            ###
###  GEOMETRY  ###
###            ###

## Get fitting polyline
def f_polyline(x, *p):
    return np.poly1d(p)(x)
def getPolylineModel(x,y):
	sigma =np.ones(len(x))
	sigma[[0, -1]] = 0.00001
	try:
		p_polyline, pcov = optimize.curve_fit(f_polyline, x, y, (0, 0, 0, 0), sigma=sigma)
	except TypeError:
		print(x,y)
	gap_polyline=np.abs(y-f_polyline(x, *p_polyline))
	gap_max=mean(gap_polyline)
	return p_polyline,gap_max

## Get fitting circle
x0 = []
y0 = []
def calc_R(xc, yc):
    """ calculate the distance of each 2D points from the center (xc, yc) """
    return sqrt((x0-xc)**2 + (y0-yc)**2)
def f_2(c):
    """ calculate the algebraic distance between the 2D points and the mean circle centered at c=(xc, yc) """
    Ri = calc_R(*c)
    return Ri - Ri.mean()
def getCircleModel(x,y,draw=True,diag=0.00001):
	global x0,y0
	x0=x
	y0=y
	sigma=ones(len(x))
	sigma[0]=diag
	sigma[-1] = diag
	x_m = mean(x0)
	y_m = mean(y0)
	center_estimate = x_m, y_m
	center_2, ier = optimize.leastsq(f_2, center_estimate,diag=sigma)

	xc_2, yc_2 = center_2
	Ri_2       = calc_R(xc_2, yc_2)
	R_2        = Ri_2.mean()
	residu = abs(Ri_2 - R_2)
	if draw==True:
		drawCircle(xc_2,yc_2,R_2,x,y)
	gap_max=mean(residu)
	return [xc_2, yc_2,R_2] ,gap_max


###        ###
###  PLOT  ###
###        ###
def drawCircle(a=0,b=0,r=1,x=x0,y=y0,color='r'):
	circle=plt.Circle((a,b),r,color=color)
	fig, ax = plt.subplots()
	plt.plot(x,y,'.')
	ax.add_artist(circle)
	ax.set_xlim(a-r*2,a+r*2)
	ax.set_ylim(b-r*2,b+r*2)
	plt.show()






def modifyListElement(list,index,value):
	list[index]=value
	return list
def getLeastSquare(list):
	x=0
	for i in list:
		x=i**2+x
	return np.sqrt(x)



def getLineModel(x,y):
	gap_line=np.abs(y)
	gap_max=mean(gap_line)
	return gap_max
def getOrientation(x,y):
	orientation=10000

	if x>=0:
		if y>=0:
			orientation=np.arctan(y/x)
		else:
			orientation=2*np.pi-np.arctan(-y/x)
	else :
		if y>=0:
			orientation=np.pi-np.arctan(-y/x)
		else:
			orientation=np.pi+np.arctan(y/x)
	if orientation==10000:
		print("error of orientation")
		return orientation
	return orientation
#
# def mult(matrix1,matrix2):
# # Matrix multiplication
#     if len(matrix1[0]) != len(matrix2):
# 		print("")
# 	else:
# 		# Multiply if correct dimensions
# 		new_matrix = zero(len(matrix1),len(matrix2[0]))
#         for i in range(len(matrix1)):
#             for j in range(len(matrix2[0])):
#                 for k in range(len(matrix2)):
#                     new_matrix[i][j] += matrix1[i][k]*matrix2[k][j]
#         return new_matrix

def rotateAndTranslate(x_list,y_list,angle=0,x0=0,y0=0):
	# TranMatrix = zero(3,3)
	# TranMatrix[0][0]=1
	# TranMatrix[0][2]=-x0
	# TranMatrix[1][1]=1
	# TranMatrix[1][2]=-y0
	# TranMatrix[2][2]=1
	x_t=[]
	y_t=[]
	if len(x_list)!=len(y_list):
		print("Error:x_list has to have the same size of y_list")
	else:
		size=len(x_list)
		for i in range(size):
			x1=(x_list[i]-x0)*np.cos(angle)-(y_list[i]-y0)*np.sin(angle)
			y1=(x_list[i]-x0)*np.sin(angle)+(y_list[i]-y0)*np.cos(angle)
			x_t.append(x1)
			y_t.append(y1)
			# x_t.append(x_list[i]*np.cos(angle)-y_list[i]*np.sin(angle)+x0*(1-np.cos(angle)+y0*np.sin(angle)))
			# y_t.append(x_list[i]*np.sin(angle)+y_list[i]*np.cos(angle)-y0*(1-np.cos(angle)-x0*np.sin(angle)))
	return x_t,y_t
def reverseRT(x,y,angle,x0,y0):
	x1=x*np.cos(angle)-y*np.sin(angle)+x0
	y1=x*np.sin(angle)+y*np.cos(angle)+y0
	return x1,y1
def getArcSign(tanX,tanY,centerX,centerY):
	oriTan=getOrientation(tanX,tanY)
	oriCenter=getOrientation(centerX,centerY)
	if oriTan-oriCenter>np.pi:
		oriCenter=oriCenter+np.pi*2
	if oriCenter-oriTan>np.pi:
		oriTan=oriTan+np.pi*2
	if oriTan>oriCenter:
		return "-"
	if oriTan<oriCenter:
		return "+"

def getInput(objectName,typeList=[],unit="",valueType="s"):
	abbreviation=[]
	title=""
	if valueType=="s":
		if not unit=="":
			unit="(%s)"%unit
		if len(typeList)>0:
			for i in range(len(typeList)):
				if not typeList[i][0] in abbreviation:
					abbreviation.append(typeList[i][0])
				elif not typeList[i][0:2] in abbreviation:
					abbreviation.append(typeList[i][0:2])
				elif not typeList[i][0:3] in abbreviation:
					abbreviation.append(typeList[i][0:3])
				else:
					abbreviation.append(typeList[i])
				title+="%s--%s; "%(typeList[i],abbreviation[i])
			out=raw_input("%s %s: \n(%s):"%(objectName,unit,title))
			if out in abbreviation:
				return typeList[abbreviation.index(out)]
			else :
				return getInput(objectName,typeList,unit,valueType)
		else:
			out=raw_input("%s %s: "%(objectName,unit))
			return out
	elif valueType=="i":
		try:
			if not unit=="":
				unit="(%s)"%unit
			if len(typeList)>0:
				for i in range(len(typeList)):
					if not typeList[i][0] in abbreviation:
						abbreviation.append(typeList[i][0])
					elif not typeList[i][0:2] in abbreviation:
						abbreviation.append(typeList[i][0:2])
					elif not typeList[i][0:3] in abbreviation:
						abbreviation.append(typeList[i][0:3])
					else:
						abbreviation.append(typeList[i])
					title+="%s--%s; "%(typeList[i],abbreviation[i])
				out=int(raw_input("%s %s: \n(%s):"%(objectName,unit,title)))
				if out in abbreviation:
					return typeList[abbreviation.index(out)]
				else :
					return getInput(objectName,typeList)
			else:
				out=int(raw_input("%s %s: "%(objectName,unit)))
				print("out:",type(out))
				return out
		except ValueError:
			print("you have to input integer!")
			return getInput(objectName,typeList,unit,'i')
	elif valueType=="f":
		try:
			if not unit=="":
				unit="(%s)"%unit
			if len(typeList)>0:
				for i in range(len(typeList)):
					if not typeList[i][0] in abbreviation:
						abbreviation.append(typeList[i][0])
					elif not typeList[i][0:2] in abbreviation:
						abbreviation.append(typeList[i][0:2])
					elif not typeList[i][0:3] in abbreviation:
						abbreviation.append(typeList[i][0:3])
					else:
						abbreviation.append(typeList[i])
					title+="%s--%s; "%(typeList[i],abbreviation[i])
				out=float(raw_input("%s %s: \n(%s):"%(objectName,unit,title)))
				if out in abbreviation:
					return typeList[abbreviation.index(out)]
				else :
					return getInput(objectName,typeList)
			else:
				out=float(raw_input("%s %s: "%(objectName,unit)))
				return out
		except ValueError:
			print("you have to input number!")
			return getInput(objectName,typeList,unit,'f')

def checkVariedLane(lineInfo):
    isVaried=False
    for i in range(len(lineInfo)):
        if lineInfo[i][-1]=="variedlane":
            isVaried=True
    return isVaried
def compareLaneSection(section1,section2,takeDistance=False):
    sameSection=[]
    if takeDistance:
        if len(section1)==len(section2):
            for i in range(len(section1)):
                for j in range(len(section2)):
                    if section1[i]==section2[j]:
                        sameSection.append(True)
            if len(sameSection)==len(section1):
                return True
            else:
                return False
        else:
            return False
    else:
        if len(section1)==len(section2):
            for i in range(len(section1)):
                for j in range(len(section2)):
                    if section1[i][1:]==section2[j][1:]:
                        sameSection.append(True)
            if len(sameSection)==len(section1):
                return True
            else:
                return False
        else:
            return False

def ReadList3L(filename):
	with open(filename,'r') as file:
		data=file.read()
	start=0
	size=data.count("[[")
	allData=[]
	for i in range(size):
		start=data.find("[[",start)+1
		end=data.find("]]",start)
		temp=data[start+0:end+1]
		temp=temp.split('], [')
		temp_new=[]
		for st in temp:
			st=st.replace('[','')
			st=st.replace(']','')
			st=st.replace('\'','')
			st=st.replace(' ','')
			st=st.replace('\n','')
			l=st.split(',')
			temp_new.append(l)
		allData.append(temp_new)
	return allData
def checkSingleSide(LineInfo):
	hasLeft=False
	hasRight=False
	for info in LineInfo:
		if info[1]=="right":
			hasRight=True
		if info[1]=="left":
			hasLeft=True
	if hasRight and hasLeft:
		return False
	else:
		return True
def analyseSectionLanes(sectionInfo):
	sizeLanes=len(sectionInfo[0])
	sizeSections=len(sectionInfo)
	
	sectionDistance=[]
	for i in range(sizeLanes):
		colInfo=[]
		colInfo.append(sectionInfo[0][i][1])
		for j in range(sizeSections):
			
			try:
				colInfo.append(sectionInfo[j][i][0]) #0 est la distance
			except IndexError:
				print("analyseSectionLanes out of index")
		sectionDistance.append(colInfo)
	return sectionDistance
def getSectionGeometry(distantceList,distanceGap=0.1,tolerace=0.02):
	y=[]
	for d in distantceList:
		y.append(float(d))
	x=np.linspace(0,(len(distantceList)-1)*distanceGap,len(distantceList))
	p_polyline,gap_polyline=getPolylineModel(x,y)
	gap=np.max(gap_polyline)
	d,c,b,a=p_polyline
	s=(len(distantceList)-1)*distanceGap
	return a,b,c,d,s,gap