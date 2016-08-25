import amr
import sys

mod = sys.argv[1]
num = sys.argv[2]

inputfile = open("data/"+mod+num+".txt",'r')
lines = inputfile.readlines()
temp = []
t = ""
for line in lines:
	if line != "\n":
		t += line
	else:
		if t not in temp and t != "\n" and t != "":
			temp.append(t)
		t = ""

for t1 in temp:
	if t1.find("(")!=-1:
		t1 = t1[t1.find("("):]
   		amr_rep = amr.readAMRFromString(t1)
   		amr.demoFunction(amr_rep)
   		print '*'*50

inputfile.close()

    