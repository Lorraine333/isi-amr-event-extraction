import sys
import pickle
import cPickle

class pathnode:
    def __init__(self, label, children):
        self.label = label
        self.children = children
    def set_label(self, label):
        self.label = label
    def set_children(self, children):
        self.children = children

class State:
    def __init__(self, pathnode, path, past_state, seq = ""):
        self.pathnode = pathnode
        self.path = path
        self.past_state = past_state
        self.seq = seq

def back_helper(graph, state):
    # state: a, [b], a
    # new_state: b, [], ab
    old_state = state.past_state
    old_state.seq = state.seq+")"
    temp = old_state.seq
    old_label = old_state.pathnode.label
    visited_children = old_state.pathnode.children
    left = False
    old = False
    while (not old) and (not left):
        if old_label in graph:
            children = graph[old_label]
            left_children = [x for x in children if x not in visited_children]
            if len(left_children) > 0:
                # left = True
                return old_state
            old_state = old_state.past_state
            old_label = old_state.pathnode.label
            temp = temp+")"
            old_state.seq = temp
            visited_children = old_state.pathnode.children
        elif old_label == "":
            old = True
            old_state.seq = temp+")"
            return old_state
        else:
            old_state = old_state.past_state
            old_state.seq = temp+")"
            old_label = old_state.pathnode.label
            visited_children = old_state.pathnode.children

def draw_back_helper(graph, state):
    # state: a, [b], a
    # new_state: b, [], ab
    old_state = state.past_state
    old_state.seq = state.seq+"]"
    temp = old_state.seq
    old_label = old_state.pathnode.label
    visited_children = old_state.pathnode.children
    left = False
    old = False
    while (not old) and (not left):
        if old_label in graph:
            children = graph[old_label]
            left_children = [x for x in children if x not in visited_children]
            if len(left_children) > 0:
                # left = True
                return old_state
            old_state = old_state.past_state
            old_label = old_state.pathnode.label
            temp = temp+"]"
            old_state.seq = temp
            visited_children = old_state.pathnode.children
        elif old_label == "":
            # old = True
            old_state.seq = temp+"]"
            return old_state
        else:
            old_state = old_state.past_state
            old_state.seq = temp+"]"
            old_label = old_state.pathnode.label
            visited_children = old_state.pathnode.children

def exploreAll(graph, state):
    result = []
    current = state.pathnode.label
    visited_children = state.pathnode.children
    path = state.path
    if current in graph:
        children = graph[current]
        left_children = [x for x in children if x not in visited_children]
        if len(left_children) > 0:
            for i in left_children:
                new_children = visited_children[:]
                new_children.append(i)
                each_state = State(pathnode(current,new_children),path+i, state.past_state)
                new_state = State(pathnode(i,[]),path+i, each_state, each_state.seq)
                result.append(new_state)
    return result

def stateR(graph, state, temp_seq = "", seq = []):
    states = exploreAll(graph, state)
    for single_state in states:
        current = single_state.pathnode.label
        old_label = single_state.past_state.pathnode.label
        # single_state.seq = temp_seq+".addkid(Node("+current+"))"
        input_node = current[current.find("$")+1:]
        single_state.seq = temp_seq+".addkid(Node(\""+input_node+"\")"
        # single_state.seq = temp_seq+"("+current
        # single_state.seq = temp_seq+old_label+"*****"+current+";"
        if current not in graph:
            single_state = back_helper(graph, single_state)
            if single_state.pathnode.label == "":
                seq.append(single_state.seq)
                return seq
            seq = stateR(graph, single_state, single_state.seq, seq)
        else:
            seq = stateR(graph, single_state, single_state.seq, seq)
    return seq

def get_representation(graph, state, temp_seq = "", seq = []):
    states = exploreAll(graph, state)
    for single_state in states:
        current = single_state.pathnode.label
        old_label = single_state.past_state.pathnode.label
        # single_state.seq = temp_seq+".addkid(Node("+current+"))"
        input_node = current[current.find("$")+1:]
        single_state.seq = temp_seq+".addkid(Node(\""+input_node+"\")"
        # single_state.seq = temp_seq+"("+current
        # single_state.seq = temp_seq+old_label+"*****"+current+";"
        if current not in graph:
            single_state = back_helper(graph, single_state)
            if single_state.pathnode.label == "":
                seq.append(single_state.seq)
                return seq
            seq = get_representation(graph, single_state, single_state.seq, seq)
        else:
            seq = get_representation(graph, single_state, single_state.seq, seq)
        return seq
    return seq


def get_draw(graph, state, temp_seq = "", seq = []):
    states = exploreAll(graph, state)
    for single_state in states:
        current = single_state.pathnode.label
        old_label = single_state.past_state.pathnode.label
        # single_state.seq = temp_seq+".addkid(Node("+current+"))"
        input_node = current[current.find("$")+1:]
        single_state.seq = temp_seq+"["+input_node
        # single_state.seq = temp_seq+"("+current
        # single_state.seq = temp_seq+old_label+"*****"+current+";"
        if current not in graph:
            single_state = draw_back_helper(graph, single_state)
            if single_state.pathnode.label == "":
                seq.append(single_state.seq)
                return seq
            seq = get_draw(graph, single_state, single_state.seq, seq)
        else:
            seq = get_draw(graph, single_state, single_state.seq, seq)
        return seq

def get_draw_smr(graph, state, temp_seq = "", seq = []):
    states = exploreAll(graph, state)
    for single_state in states:
        current = single_state.pathnode.label
        old_label = single_state.past_state.pathnode.label
        # single_state.seq = temp_seq+".addkid(Node("+current+"))"
        input_node = current[current.find("$")+1:]
        single_state.seq = temp_seq+"["+input_node
        # single_state.seq = temp_seq+"("+current
        # single_state.seq = temp_seq+old_label+"*****"+current+";"
        if current not in graph:
            single_state = draw_back_helper(graph, single_state)
            if single_state.pathnode.label == "":
                seq.append(single_state.seq)
                return seq
            seq = get_draw_smr(graph, single_state, single_state.seq, seq)
        else:
            seq = get_draw_smr(graph, single_state, single_state.seq, seq)
    return seq


def save_params(model, f, smr = True):
    graph_list = model['dics']
    root_list = model['root']
    save_model = {}
    dics = {}
    for i in range(len(graph_list)):
        # print "*"*10
        # print i
        graph = graph_list[i]
        root = root_list[i]
        dum_old = (pathnode("",[]),"")
        old_start = State(pathnode("",[]),"", dum_old)
        start = State(pathnode(root,[]),root,old_start)
        if smr:
            #for smr, get the permutation
            result = stateR(graph, start,"(Node(\"TOP\").addkid(Node(\""+root[root.find("$")+1:]+"\")",[])
            if len(result) == 0:
                result = ["(Node(\"TOP\").addkid(Node(\""+root[root.find("$")+1:]+"\")))"]
            # print result
        else:
            #for amr, only get representation
            result = get_representation(graph, start,"(Node(\"TOP\").addkid(Node(\""+root[root.find("$")+1:]+"\")",[])
            if len(result) == 0:
                result = ["(Node(\"TOP\").addkid(Node(\""+root[root.find("$")+1:]+"\")))"]
        save_smr = []
        # print len(result)
        dics[i] = len(result)
        for j in result:
            j = j.replace(":","_")
            save_smr.append(j[:])
        save_model[i] = save_smr
        # result = ""
    cPickle.dump(save_model, f, protocol=cPickle.HIGHEST_PROTOCOL)
    f.close()

    if smr:
        fmap = open("data/smr_map.p","wt")
        cPickle.dump(dics, fmap, protocol=cPickle.HIGHEST_PROTOCOL)
        fmap.close()
    return

def check(model, s, e, smr):
    graph_list = model['dics']
    root_list = model['root']
    save_model = {}
    dics = {}
    for i in range(s, e, 1):
        graph = graph_list[i]
        root = root_list[i]
        dum_old = (pathnode("",[]),"")
        old_start = State(pathnode("",[]),"", dum_old)
        start = State(pathnode(root,[]),root,old_start)
        if smr:
            #for smr, get the permutation
            # print graph
            # print root
            result = stateR(graph, start,"(Node(\"TOP\").addkid(Node(\""+root[root.find("$")+1:]+"\")",[])
            if len(result) == 0:
                result = ["(Node(\"TOP\").addkid(Node(\""+root[root.find("$")+1:]+"\")))"]
            print 'For SMR'
            print result
        else:
            #for amr, only get representation
            result = get_representation(graph, start,"(Node(\"TOP\").addkid(Node(\""+root[root.find("$")+1:]+"\")",[])
            print 'For AMR'
            print result
        save_smr = []
        dics[i] = len(result)
        for j in result:
            j = j.replace(":","_")
            save_smr.append(j[:])
        save_model[i] = save_smr
        result = ""
    return

def draw(model, s, e, smr):
    graph_list = model['dics']
    root_list = model['root']
    save_model = {}
    dics = {}
    for i in range(s, e, 1):
        graph = graph_list[i]
        root = root_list[i]
        # graph = {'a':['b','c','d','z'],'b':['e','f','m']}
        # root = 'a'
        dum_old = (pathnode("",[]),"")
        old_start = State(pathnode("",[]),"", dum_old)
        start = State(pathnode(root,[]),root,old_start)
        if smr:
            #for smr, get the permutation
            result = get_draw_smr(graph, start,"[TOP["+root[root.find("$")+1:],[])
            print 'For SMR'
            print result
        else:
            #for amr, only get representation
            result = get_draw(graph, start,"[TOP["+root[root.find("$")+1:],[])
            print 'For AMR'
            print result
        save_smr = []
        dics[i] = len(result)
        print len(result)
        for j in result:
            j = j.replace(":","_")
            save_smr.append(j[:])
        save_model[i] = save_smr
        # result = ""
    return

if __name__ == "__main__":
    print 'generating representation for zhangshasha algorithm'
    mod = sys.argv[1]
    start = sys.argv[2]
    if mod == "save":
        read_smr_model = pickle.load(open("data/smrs_permutation_input.p", "r"))
        read_amr_model = pickle.load(open("data/amrs_permutation_input.p", "r"))
        write_smr = open("data/zhangshasha_smr_input.p","wt")
        write_amr = open("data/zhangshasha_amr_input.p","wt")
        # read_smr_model = pickle.load(open("data/smrs_permutation_input.p", "r"))
        # read_amr_model = pickle.load(open("data/amrs_permutation_input.p", "r"))
        # write_smr = open("data/zhangshasha_smr_input.p","wt")
        # write_amr = open("data/zhangshasha_amr_input.p","wt")
        s = 0
        save_params(read_smr_model ,write_smr, True)
        save_params(read_amr_model ,write_amr, False)
    elif mod == "save_binary":
        read_smr_model = pickle.load(open("data/smrs_b_permutation_input.p", "r"))
        read_amr_model = pickle.load(open("data/amrs_b_permutation_input.p", "r"))
        write_smr = open("data/zhangshasha_smr_b_input.p","wt")
        write_amr = open("data/zhangshasha_amr_b_input.p","wt")
        s = 0
        save_params(read_smr_model ,write_smr, True)
        save_params(read_amr_model ,write_amr, False)

    elif mod == "save_right_binary":
        read_smr_model = pickle.load(open("data/smrs_rb_permutation_input.p", "r"))
        read_amr_model = pickle.load(open("data/amrs_rb_permutation_input.p", "r"))
        write_smr = open("data/zhangshasha_smr_rb_input.p","wt")
        write_amr = open("data/zhangshasha_amr_rb_input.p","wt")
        s = 0
        save_params(read_smr_model ,write_smr, True)
        save_params(read_amr_model ,write_amr, False)

    elif mod == "test_binary":
        s = int(start)
        e = int(start)+1
        read_smr_model = pickle.load(open("data/smrs_b_permutation_input.p", "r"))
        read_amr_model = pickle.load(open("data/amrs_b_permutation_input.p", "r"))
        check(read_smr_model, s, e, False)

    elif mod == "test":
        s = int(start)
        e = int(start)+1
        read_smr_model = pickle.load(open("data/smrs_permutation_input960.p", "r"))
        read_amr_model = pickle.load(open("data/amrs_permutation_input960.p", "r"))
        check(read_smr_model, s, e, True)
        # check(read_amr_model, s, e, False)
    elif mod == "draw":
        s = int(start)
        e = int(start)+1
        read_smr_model = pickle.load(open("data/smrs_permutation_input.p", "r"))
        read_amr_model = pickle.load(open("data/amrs_permutation_input.p", "r"))
        draw(read_smr_model, s, e, False)
        draw(read_amr_model, s, e, False)
    else:
        raise Exception("Wrong input!")
