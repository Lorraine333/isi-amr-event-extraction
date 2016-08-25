import sys

mod = sys.argv[1]
indexfile = sys.argv[2]

with open(indexfile+"/index.txt","r") as f:
   	lines = f.read().splitlines()
train = int(lines[0][lines[0].find(" = ")+3:])
test = int(lines[1][lines[1].find(" = ")+3:])
new_list = lines[2][lines[2].find(" = ")+4:-1]

num_list = new_list.split(", ")

if mod == "union":
	folder = "../amr_train_union/"
	start = 0
	num = train
	total = num - start
if mod == "single":
	folder = "../amr_train_single/"
	start = 0
	num = train
	total = num - start
if mod == "test_now":
	folder = "../amr_test/"
	start = train
	num = train+test
	total = num - start
if mod == "single_count":
	folder = "../amr_train_single/best"
	start = 0
	num = train
	total = num - start
if mod == "union_count":
	folder = "../amr_train_single/best_prob"
	start = 0
	num = train
	total = num - start
if mod == "test_count":
	folder = "../amr_test/test_prob"
	start = train
	num = train+test
	total = num - start

success = True
s_num = 0
f_num = 0
for f in range(start, num, 1):
	i = num_list[f]
	fin = open(folder+str(i)+'.result')
	lines = fin.read().splitlines()
	if len(lines)<=1:
		# print lines
		# print folder,str(i),'.result'
		success = False
		print 'Number ',i,' Failed!'
		f_num += 1
	else:
		s_num += 1
		if mod == "test_now" or mod =="single_count" or mod == "union_count" or mod == "test_count":
			print 'Test Number ',i,' Success!'
		
if success:
	print 'All Trees Have Been Generated!'

print 'Successed on ',s_num,"/",total
print 'Failed on ',f_num,"/",total

