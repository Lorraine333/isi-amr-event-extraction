with open("test.txt") as f:
	lines = f.read().splitlines()
# i = 0
# while i < len(lines):
# 	if lines[i].isdigit() and "Document" not in lines[i+1]:
# 		print lines[i]+",",
# 		i+=1
# 	else:
# 		i+=2
num = []
for line in lines:
	if "Document" in line:
		num.append(float(line[line.find("F-score:")+8:]))
print sum(num)/len(num)