import sys
import pickle
import cPickle
import construct_tree
import generate_TED_input
import parallel_TED

mod = sys.argv[1]
start = sys.argv[2]
num = sys.argv[3]

if __name__ == "__main__":
    amrs = construct_tree.readin("data/amr_list"+num+".txt")
    smrs = construct_tree.readin("data/smr_list"+num+".txt")

    print "Construsting Tree from AMR and SMR......"
    f_smr = open("data/smrs_permutation_input.p","wb")
    f_amr = open("data/amrs_permutation_input.p","wb")
    s = 0
    e = len(smrs)
    construct_tree.save_params(f_smr,s,e,smrs)
    construct_tree.save_params(f_amr,s,e,amrs)

    print "Generating Representation for TED algorithm......"
    read_smr_model = pickle.load(open("data/smrs_permutation_input.p", "r"))
    read_amr_model = pickle.load(open("data/amrs_permutation_input.p", "r"))
    write_smr = open("data/zhangshasha_smr_input.p","wt")
    write_amr = open("data/zhangshasha_amr_input.p","wt")
    generate_TED_input.save_params(read_smr_model ,write_smr, True)
    generate_TED_input.save_params(read_amr_model ,write_amr, False)

    print "Parallel TED algorithm......"
    dics= pickle.load(open("data/smr_map.p", "r"))
    key, value = parallel_TED.makelist(dics)
    breakpoint = parallel_TED.distribu(key, value)
    parallel_TED.write(breakpoint)





    # if mod == "save":




    # elif mod == "test":
    #     s = int(start)
    #     e = int(start)+1
    #     check(s, e, smrs)
    #     check(s, e, amrs)
    # else:
    #     raise Exception("Wrong input!")





