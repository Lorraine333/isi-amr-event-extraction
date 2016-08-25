import sys

index_file = sys.argv[2]

with open(index_file+"/index.txt","r") as f:
   	lines = f.read().splitlines()
train = int(lines[0][lines[0].find(" = ")+3:])
test = int(lines[1][lines[1].find(" = ")+3:])
new_list = lines[2][lines[2].find(" = ")+4:-1]

num_list = new_list.split(", ")

mod = sys.argv[1]

if mod == "single":
	start = 0
	num = train
	folder = "../amr_single_result_tree/result"

if mod == "union":
	start = 0
	num = train
	folder = "../amr_union_result_tree/result"

if mod == "test_now":
	start = train
	num = train+test
	folder = "../amr_test_result_tree/result"
	
count = []


for f in range(start, num, 1):
	i = num_list[f]
	fin = open(folder+str(i)+".tree")
	num = 0
	lines = fin.read().splitlines()
	for line in lines:
		if 'derivations' not in line:
			pass
		else:
			line = line.strip()
			num = line[:line.find("derivations")-1]
	count.append(long(num))
print count
print sum(count)/len(count)