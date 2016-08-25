import pickle
import sys
import cPickle
import os

model_trace = {}

treeA_list = []
treeB_list = []
path_list = []
dist_list = []
best_amr_list = []
best_smr_list = []

num_list = [0, 1, 2, 5, 6, 11, 15, 21, 28, 29, 35, 36, 41, 42, 43, 44, 46, 48, 49, 54, 57, 58, 59, 61, 62, 64, 72, 75, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 99, 101, 103, 116, 118, 125, 132, 151, 167, 170, 174, 177, 178, 182, 185, 190, 191, 192, 194, 196, 197, 210, 215, 222, 229, 232, 240, 245, 247, 251, 253, 256, 260, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 304, 306, 310, 312, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 331, 335, 337, 339, 346, 354, 361, 363, 368, 381, 383, 384, 386, 391, 393, 395, 399, 405, 406, 416, 424, 456, 494, 523, 553, 572, 573, 574, 575, 579, 588, 595, 596, 602, 614, 615, 617, 618, 623, 624, 625, 626, 627, 629, 630, 631, 636, 640, 645, 655, 662, 665, 668, 674, 686, 688, 691, 694, 788, 840, 842, 846, 904, 906, 908, 909, 910, 913, 921, 924, 930, 936, 937, 938, 939, 940, 950, 957, 960]
f = open("../data/zhangshasha_traces.p","wt")

for i in range(len(num_list)-1):
# for i in range(3):
	start = num_list[i]
	end = num_list[i+1]
	# print "*"*50
	print start, end
	sing_model_trace = pickle.load(open("zhangshasha_"+str(start)+"to"+str(end)+"_traces.p",'r'))
	# print sing_model_trace['treeA']
	# print sing_model_trace['treeB']
	# print sing_model_trace['path_list']
	# print sing_model_trace['dist_list']
	# print sing_model_trace['best_amr']
	# print sing_model_trace['best_smr']
	treeA_list += sing_model_trace['treeA']
	treeB_list += sing_model_trace['treeB']
	path_list += sing_model_trace['path_list']
	dist_list += sing_model_trace['dist_list']
	best_amr_list += sing_model_trace['best_amr']
	best_smr_list += sing_model_trace['best_smr']
model_trace['treeA'] = treeA_list
model_trace['treeB'] = treeB_list
model_trace['path_list'] = path_list
model_trace['dist_list'] = dist_list
model_trace['best_amr'] = best_amr_list
model_trace['best_smr'] = best_smr_list
cPickle.dump(model_trace, f, protocol=cPickle.HIGHEST_PROTOCOL)
f.close()
		
