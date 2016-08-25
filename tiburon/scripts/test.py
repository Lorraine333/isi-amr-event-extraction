import sys

mod = sys.argv[1]

with open("test_"+mod+".txt") as f:
	lines = f.read().splitlines()
	
num = []
for line in lines:
	if "Document" in line:
		t = float(line[line.find("F-score:")+8:])
		num.append(t)
print sum(num)/len(num)