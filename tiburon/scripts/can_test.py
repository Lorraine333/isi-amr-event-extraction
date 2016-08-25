import sys

with open("can_test.txt","r") as f:
   	lines = f.read().splitlines()

i = 0
for line in lines:
	if 'derivations' not in line:
		if line.startswith("#"):
			current_id = int(line[line.find("#")+1:])
		pass
	else:
		line = line.strip()
		num = line[:line.find("derivations")-1]
		if num.isdigit() and int(num) != 0:
			print current_id,"can generate some smr"
			i+=1
print str(i)+"/19 test data can generate some smr"
