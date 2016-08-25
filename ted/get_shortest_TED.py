import pickle
import sys
import cPickle
from simple_tree import Node
import compare

model_smr = pickle.load(open("data/zhangshasha_smr_input.p", "r"))
model_amr = pickle.load(open("data/zhangshasha_amr_input.p", "r"))
start = int(sys.argv[1])
end = int(sys.argv[2])

# print len(model_amr)
# print len(model_smr)

model_trace = {}

treeA_list = []
treeB_list = []
path_list = []
dist_list = []
best_amr_list = []
best_smr_list = []
# for i in range(len(model_amr)):
for i in range(start, end, 1):
	# i = 24
	current_smr_perm = model_smr[i]
	# print model_amr[i][0]
	A = eval(model_amr[i][0])
	print 'Eval on No',i,'AMR and SMR pair'
	print 'SMR permutations:',len(current_smr_perm)
	best_A = {}
	best_B = {}
	best_amr = ""
	best_smr = ""
	best_Path = []
	best_dist = 500000
	# if i ==153 or i == 154:
	for j in range(len(current_smr_perm)):
		print 'Current Using',j,'SMR with',i,'AMR'
		B = eval(current_smr_perm[j])
		treeA, treeB, path, dist = compare.simple_distance(A, B, Node.get_children)
		print 'Distance', dist
		if dist < best_dist:
			best_amr = model_amr[i]
			# print model_amr[i]
			best_smr = current_smr_perm[j]
			# print current_smr_perm[j]
			best_A = treeA
			best_B = treeB
			best_Path =path
			best_dist = dist
	best_amr_list.append(best_amr)
	best_smr_list.append(best_smr)
	treeA_list.append(best_A)
	treeB_list.append(best_B)
	path_list.append(best_Path)
	dist_list.append(best_dist)
model_trace['best_amr'] = best_amr_list
model_trace['best_smr'] = best_smr_list
model_trace['treeA'] = treeA_list
model_trace['treeB'] = treeB_list
model_trace['path_list'] = path_list
model_trace['dist_list'] = dist_list

# f = open("data/zhangshasha_"+str(start)+"to"+str(end)+"_traces.p","wt")
f = open("data/zhangshasha_traces.p","wt")
cPickle.dump(model_trace, f, protocol=cPickle.HIGHEST_PROTOCOL)
f.close()
