import pickle
from collections import deque
from sets import Set
import sys
import re
import union_rules
import generate_rtg

def get_stack_from_ted_repre(ted_input):
    ted_input = ted_input.replace("addkid(","")
    ted_input = ted_input.replace(").","")
    ted_input = ted_input.replace("Node",'')
    ted_input = ted_input.replace("\"",'')
    ted_input = ted_input[1:]
    stack = []
    seq = []
    for i in range(len(ted_input)):
        if ted_input[i] == "(":
            seq.append(i)
        elif ted_input[i] == ")":
            seq.append(i)
    word_list = []
    for j in range(len(seq)-1):
        stack.append(ted_input[seq[j]])
        if seq[j+1] - seq[j] >1:
            stack.append(ted_input[seq[j]+1:seq[j+1]])
            word_list.append(ted_input[seq[j]+1:seq[j+1]])
    return stack

def mark_node(stack, trace, graph_dics, smr_dics):
    j = 0
    i = 1
    mystack = []
    mystack.append(stack[0])
    while len(mystack)!=0 and (i<len(stack)):
        element = stack[i]
        if element is ")":
            current = mystack.pop()
            mystack.pop()
            if len(mystack)!=0 and current[:current.find("*")] in trace[j]:
                current_com = trace[j]
                operation = current_com[:current_com.find(":")]
                num = int(current_com[current_com.find("(")+1:current_com.find(")")])
                if num in graph_dics:
                    if operation == "Rename":
                        rename_t = current_com[current_com.find(" To ")+4:]
                        graph_dics[num] += "$R$"
                        graph_dics[num] += rename_t
                        mystack[-1] += "*"
                        rename_tn = int(current_com[find_nth(current_com, "(",2)+1:find_nth(current_com,")",2)])
                        smr_dics[rename_tn] += "$R$"
                    elif operation == "Delete":
                        if "*" in current:
                            graph_dics[num] += "$D*$"
                            mystack[-1] += "*"
                        else:
                            graph_dics[num] += "$D$"
                    elif operation == "Match":
                        maname_t = current_com[current_com.find(" and ")+5:]
                        graph_dics[num] += "$M$"
                        graph_dics[num] += maname_t
                        mystack[-1] += "*"
                        maname_tn = int(current_com[find_nth(current_com, "(",2)+1:find_nth(current_com,")",2)])
                        smr_dics[maname_tn] += "$M$"
                    else:
                        pass
                j += 1
            if len(mystack) == 0 and current[:current.find("*")] in trace[j]:
                current_com = trace[j]
                operation = current_com[:current_com.find(":")]
                num = int(current_com[current_com.find("(")+1:current_com.find(")")])
                if num in graph_dics:
                    if operation == "Rename":
                        graph_dics[num] += "$R$"
                        rename_t = current_com[current_com.find(" To ")+4:]
                        graph_dics[num] += rename_t
                        rename_tn = int(current_com[find_nth(current_com, "(",2)+1:find_nth(current_com,")",2)])
                        smr_dics[rename_tn] += "$R$"
                    elif operation == "Delete":
                        if "*" in current:
                            graph_dics[num] += "$D*$"
                        else:
                            graph_dics[num] += "$D$"
                    else:
                        maname_t = current_com[current_com.find(" and ")+5:]
                        graph_dics[num] += "$M$"
                        graph_dics[num] += maname_t

                        maname_tn = int(current_com[find_nth(current_com, "(",2)+1:find_nth(current_com,")",2)])
                        smr_dics[maname_tn] += "$M$"
            i += 1
        else:
            mystack.append(stack[i])
            i += 1
    return graph_dics, smr_dics


def createTree(stack, total):
    j = 0
    i = 1
    left = []
    result = stack[:]
    mystack = []
    mystack.append(stack[0])
    if stack[0] == "(":
        left.append(0)
    while len(mystack)>0 and i<len(stack):
        element = stack[i]
        if element is ")":
            mystack.pop()
            if len(left)>0:
                cur_pos = left.pop()
                result[cur_pos+1] = total - j-1
                # print result
            mystack.pop()
            if len(mystack) == 0:
                pass
            i += 1
            j += 1
        else:
            mystack.append(stack[i])
            if element == "(":
                left.append(i)
            i += 1
    return result

def get_tree_dic(stack, root):
    tree_dics = {}
    j = 0
    i = 1
    parent = []
    mystack = []
    mystack.append(stack[0])
    parent.append(int(root))
    while len(mystack)>0 and i<len(stack):
        element = stack[i]
        if element is ")":
            mystack.pop()
            if len(parent)>0:
                cur_child = parent.pop()
                if len(parent)==0:
                    pass
                else:
                    if parent[-1] in tree_dics:
                        tree_dics[parent[-1]].append(cur_child)
                    else:
                        tree_dics[parent[-1]] = [cur_child]
            mystack.pop()
            if len(mystack) == 0:
                pass
            i += 1
            j += 1
        else:
            mystack.append(stack[i])
            if element == "(":
                parent.append(int(stack[i+1]))
            i += 1
    return tree_dics


def find_nth(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+len(needle))
        n -= 1
    return start



def find_parent(current, root, mydict, result):
    if current != root:
        for p, c in mydict.items():
            if current in c:
                result.append(p)
                result = find_parent(p, root, mydict, result)
    return result

def get_ope(command):
    return command[command.find("$")+1:find_nth(command,"$",2)]

def get_amr_node(command):
    if "$" in command:
        return command[:find_nth(command,"$",1)]
    else:
        return command

def get_smr_node(command):
    return command[find_nth(command,"$",2)+1:find_nth(command,"(",1)]

def get_smr_node_num(command):
    return command[find_nth(command,"(",1)+1:find_nth(command,")",1)]

def dfs(tree_dict, root, visited, seq, input_map):
    visited.add(root)
    if root in tree_dict:
        i=0
        for node in tree_dict[root]:
            if node not in visited:
                current_node = input_map[node]
                # print current_node
                if i==0:
                    if current_node.find("$")!=-1:
                        temp = current_node[:current_node.find("$")]
                        output = "("+temp
                    else:
                        output = "("+current_node
                else:
                    if current_node.find("$")!=-1:
                        temp = current_node[:current_node.find("$")]
                        output = " "+temp
                    else:
                        output = " "+current_node
                i = i+1
                seq += output
                seq = dfs(tree_dict, node, visited, seq, input_map)
            else:
                return seq
        seq += ")"
        return seq
    else:
        return seq


def find_parent(current, mydict):
    for p, c in mydict.items():
        if current in c:
            return p
    return ""

def get_amr_points(mydict, mymap, original_root, root, trace = [], num = 0, child_list = [], n=0):
    trace.append(root)
    current_ope = get_ope(mymap[root])
    if original_root not in mydict:
        return trace, n, child_list, num
    if root == original_root:
        i = 0
        for children in mydict[root]:
            if i ==0:
                trace.append("(")
            i+= 1
            trace, n, child_list, num = get_amr_points(mydict, mymap, original_root, children, trace, num, child_list, n)
            trace.append(" ")
        trace.append(")")
    else:
        if current_ope == "M" or current_ope == "R" or current_ope == "D" or root not in mydict:
            if current_ope != "D":
                child_list.append(n)
                child_list.append(root)
                n += 1
            else:
                n += 1
                pass
            return trace, n, child_list, num
        else:
            i = 0
            for children in mydict[root]:
                if i ==0:
                    trace.append("(")
                i+=1
                trace, n, child_list, num = get_amr_points(mydict, mymap, original_root, children, trace, num, child_list, n)
                trace.append(" ")
            trace.append(")")
    return trace, n, child_list, num


def get_smr_points(mydict, mymap, original_root, root, trace = [], num = 0, child_list = []):
    trace.append(root)
    current_ope = get_ope(mymap[root])
    if original_root not in mydict:
        return trace, num, child_list
    if root == original_root:
        i = 0
        for children in mydict[root]:
            if i ==0:
                trace.append("(")
            i+= 1
            trace, num, child_list = get_smr_points(mydict, mymap, original_root, children, trace, num, child_list)
            trace.append(" ")
        trace.append(")")
    else:
        if current_ope == "M" or current_ope == "R":
            child_list.append(root)
            num += 1
        elif root not in mydict:
            pass
        else:
            i = 0
            for children in mydict[root]:
                if i ==0:
                    trace.append("(")
                i+=1
                trace, num, child_list = get_smr_points(mydict, mymap, original_root, children, trace, num, child_list)
                trace.append(" ")
            trace.append(")")
    return trace, num, child_list

def get_lhs_rule(sub, mymap, smr_map, smrhead):
    smr_label = get_amr_node(smr_map[smrhead])
    if "r_" in smr_label or "TOP" in smr_label:
        rule = "qr."
    else:
        rule = "qc."
    i = 0
    for x in range(len(sub)):
        t = sub[x]
        if t == "(" or t == ")" or t == " ":
            rule += t
        # if str(t).isdigit():
        #     if x+1 < len(sub) and sub[x+1] == " ":
        #         rule = rule + "x"+str(i)+":"
        #         i+=1
        #     else:
        #         pass
        #     rule = rule + get_amr_node(mymap[t])
        #get no specific node rule
        if str(t).isdigit():
            if x+1 < len(sub) and sub[x+1] == " ":
                rule = rule + "x"+str(i)+":"
                i+=1
            else:
                rule = rule + get_amr_node(mymap[t])
        if t == -1:
            rule = rule + get_amr_node(mymap[t])
    return rule

def get_loose_lhs_rule(sub, mymap, smr_map, smrhead):
    smr_label = get_amr_node(smr_map[smrhead])
    if "r_" in smr_label or "TOP" in smr_label:
        rule = "qr."
    else:
        rule = "qc."
    i = 0
    for x in range(len(sub)):
        t = sub[x]
        if t == "(" or t == ")" or t == " ":
            rule += t
        if str(t).isdigit():
            if x+1 < len(sub) and sub[x+1] == " ":
                rule = rule + "x"+str(i)+":"
                i+=1
            else:
                rule = rule + get_amr_node(mymap[t])
        if t == -1:
            rule = rule + get_amr_node(mymap[t])
    return rule

def get_smr_parent(num_rep):
    mydict = {}
    result = {}
    parent_stack = []
    for j in range(1,len(num_rep)):
        element = num_rep[j]
        if (element != '(') and (element != ')') and (element != ' '):
            if current_parent in mydict:
                mydict[current_parent].append(element)
            else:
                mydict[current_parent] = [element]
        if element == ')':
            parent_stack.pop()
            if len(parent_stack) != 0:
                current_parent = parent_stack[-1]
        if element == '(':
            parent_stack.append(num_rep[j-1])
            current_parent = parent_stack[-1]
    # print num_rep
    # print mydict
    for k in mydict:
        for v in mydict[k]:
            result[v] = k
    # print result
    return result

def get_rhs_rule(sub, mymap, smr_child):
    rule = ""
    i = 0
    parents = get_smr_parent(sub)
    for x in range(len(sub)):
        t = sub[x]
        if t == "(" or t == ")" or t == " ":
            rule += t
        if str(t).isdigit():
            if x+1 < len(sub) and sub[x+1] == " " and (t in smr_child):
                smr_label = get_amr_node(mymap[parents[t]])
                if "r_" in smr_label or "TOP" in smr_label:
                    state = "qc"
                else:
                    state = "qr"
                rule = rule + state + ".x"+str(i)
                i+=1
            else:
                rule = rule + get_amr_node(mymap[t]).replace(" ","_")
    return rule

def get_delete_rhs_rule(sub, mymap, amr_child, smr_child):
    rule = ""
    i = 0
    parents = get_smr_parent(sub)
    # print sub
    for x in range(len(sub)):
        t = sub[x]
        if t == "(" or t == ")" or t == " ":
            rule += t
        if str(t).isdigit():
            if x+1<len(sub) and sub[x+1] == " " and (t in smr_child) :
                # print t
                # print parents[t]
                smr_label = get_amr_node(mymap[parents[t]])
                if "r_" in smr_label or "TOP" in smr_label:
                    state = "qc"
                else:
                    state = "qr"
                rule = rule + state + ".x"+str(amr_child[i*2])
                i+=1
            else:
                rule = rule + get_amr_node(mymap[t]).replace(" ","_")
    return rule

def check(node, mymap):
    return get_ope(mymap[node]) == "M" or get_ope(mymap[node]) == "R"

def generate(amr_dics, amr_map, smr_dics, smr_map, root):
    amrqueue = deque([root])
    smrqueue = deque([root])
    rules = []
    while len(amrqueue) != 0 and len(smrqueue) != 0:
        amr_node = amrqueue.popleft()
        smr_node = smrqueue.popleft()

        if check(amr_node, amr_map) and check(smr_node, smr_map):
            amr_sub, amr_child_num, amr_child, _ = get_amr_points(amr_dics, amr_map, amr_node, amr_node, [], 0, [], 0)
            smr_sub, smr_child_num, smr_child = get_smr_points(smr_dics, smr_map, smr_node, smr_node, [], 0, [])
            # print 'amr',amr_sub, amr_child_num, amr_child
            # print 'smr',smr_sub, smr_child_num, smr_child
            if amr_child_num == smr_child_num:
                lhs_rule = get_lhs_rule(amr_sub, amr_map, smr_map, smr_sub[0])
                rhs_rule = get_rhs_rule(smr_sub, smr_map, smr_child)
                # lhs_loose_rule = get_loose_lhs_rule(amr_sub, amr_map, smr_map, smr_sub[0])
                for x in range(1,len(amr_child),2):
                    amr_c = amr_child[x]
                    amrqueue.append(amr_c)
                for smr_c in smr_child:
                    smrqueue.append(smr_c)
                rule = lhs_rule +" -> "+rhs_rule
                # loose_rule = lhs_loose_rule + " -> "+rhs_rule
                # print rule
            else:
                lhs_rule = get_lhs_rule(amr_sub, amr_map, smr_map, smr_sub[0])
                rhs_rule = get_delete_rhs_rule(smr_sub, smr_map, amr_child, smr_child)
                # lhs_loose_rule = get_loose_lhs_rule(amr_sub, amr_map, smr_map, smr_sub[0])
                # print smr_child
                # print lhs_rule
                # print rhs_rule
                for x in range(1,len(amr_child),2):
                    amr_c = amr_child[x]
                    amrqueue.append(amr_c)
                for smr_c in smr_child:
                    smrqueue.append(smr_c)
                rule = lhs_rule +" -> "+rhs_rule
                # loose_rule = lhs_loose_rule + " -> " + rhs_rule
                # print rule
            rules.append(rule)
            # rules.append(loose_rule)
            # pass
        else:
            pass
    return rules

def preprocess(treeA, best_amr, treeB, best_smr, trace):
    #for treeA
    for z in treeA:
        m = treeA[z]
        m = m.replace(".","_")
        m = m.replace(":","_")
        if "mod " in m:
            m = m.replace("mod ","mod_")
        # m = m.replace("add-modification-00","add-modification")
        treeA[z] = m
    
    #for treeB
    for z1 in treeB:
        m1 = treeB[z1]
        m1 = m1.replace(".","_")
        m1 = m1.replace(":","_")
        if "mod " in m1:
            m1 = m1.replace("mod ","mod_")
        # m1 = m1.replace("add-modification-00","add-modification")
        treeB[z1] = m1

    #for traces
    new_trace= [x for x in trace if "Insert" not in x]
    for z2 in range(len(new_trace)):
        m2 = new_trace[z2]
        m2 = m2.replace(".","_")
        if "mod " in m2:
            m2 = m2.replace("mod ","mod_")
        # m2 = m2.replace("add-modification-00","add-modification")
        new_trace[z2] = m2

    #for best amr
    p = re.compile('\d+[.]\d+')
    iterator = p.finditer(best_amr)
    for match in iterator:
        match_str = best_amr[match.span()[0]:match.span()[1]]
        dot_pos = match_str.find(".")
        best_amr = best_amr[:match.span()[0]+dot_pos]+"_"+best_amr[match.span()[0]+dot_pos+1:]
    best_amr = best_amr.replace(":","_")

    p = re.compile('\"(.+?)\"')
    iterator = p.finditer(best_amr)
    for match in iterator:
        match_str = best_amr[match.span()[0]:match.span()[1]]
        if match_str.find(".") != -1:
            dot_pos = match_str.find(".")
            best_amr = best_amr[:match.span()[0]+dot_pos]+"_"+best_amr[match.span()[0]+dot_pos+1:]

    best_amr = best_amr.replace("mod ","mod_")

    #for best smr
    p = re.compile('\d+[.]\d+')
    iterator = p.finditer(best_smr)
    for match in iterator:
        match_str = best_amr[match.span()[0]:match.span()[1]]
        dot_pos = match_str.find(".")
        best_smr = best_smr[:match.span()[0]+dot_pos]+"_"+best_smr[match.span()[0]+dot_pos+1:]
    best_smr = best_smr.replace(":","_")

    p = re.compile('\"(.+?)\"')
    iterator = p.finditer(best_smr)
    for match in iterator:
        match_str = best_smr[match.span()[0]:match.span()[1]]
        if match_str.find(".") != -1:
            dot_pos = match_str.find(".")
            best_smr = best_smr[:match.span()[0]+dot_pos]+"_"+best_smr[match.span()[0]+dot_pos+1:]
    # best_smr = best_smr.replace("add-modification-00","add-modification")
    best_smr = best_smr.replace("mod ","mod_")

    #after preprocessing everything, return the new result
    return treeA, best_amr, treeB, best_smr, new_trace

def save_part(train, tree_amr_dics, new_treeA_map, tree_smr_dics, new_treeB_map, i):
    if train:
        rules = generate(tree_amr_dics, new_treeA_map, tree_smr_dics, new_treeB_map, 0)
        rules = Set(rules)
        if len(rules) ==0:
            # print i
            # print new_treeA_map
            # print new_treeB_map
            raise Exception("No Rules generated in this case")
        else:
            # fout = open("../tiburon-tar-gz_2/amr_train_single_trans/simple"+str(i)+".trans","wt")
            fout = open("tiburon/amr_train_single_trans/simple"+str(i)+".trans","wt")
            fout.write("qr\n")
            for rule in rules:
                if rule == "unrecognize command":
                    raise Exception("Unrecognize Command")
                if rule != "" :
                    fout.write(rule+"\n")
            fout.close()

        # fout = open("../tiburon-tar-gz_2/amr_train_amr_tree/amr"+str(i)+".tree","wt")
        # fout1 = open("../tiburon-tar-gz_2/amr_train_smr_tree/smr"+str(i)+".tree","wt")
        fout = open("tiburon/amr_train_amr_tree/amr"+str(i)+".tree","wt")
        fout1 = open("tiburon/amr_train_smr_tree/smr"+str(i)+".tree","wt")
    else:
        # fout = open("../tiburon-tar-gz_2/amr_test_amr_tree/amr"+str(i)+".tree","wt")
        # fout1 = open("../tiburon-tar-gz_2/amr_test_smr_tree/smr"+str(i)+".tree","wt")
        fout = open("tiburon/amr_test_amr_tree/amr"+str(i)+".tree","wt")
        fout1 = open("tiburon/amr_test_smr_tree/smr"+str(i)+".tree","wt")

    ti_amr = new_treeA_map[0][:new_treeA_map[0].find("$")]
    ti_amr = dfs(tree_amr_dics, 0, Set(), ti_amr, new_treeA_map)
    ti_smr = new_treeB_map[0][:new_treeB_map[0].find("$")]
    ti_smr = dfs(tree_smr_dics, 0 ,Set(), ti_smr, new_treeB_map)
    fout.write(ti_amr)
    fout1.write(ti_smr)

def generate_single_rtg(mydict, mymap, root):
    result = []
    myqueue = deque([root])
    while len(myqueue) != 0:
        node = myqueue.popleft()
        rule = "q"+str(node) + " -> "
        rule = rule+mymap[node].replace(" ","_")
        if node in mydict:
            rule += "("
            for children in mydict[node]:
                myqueue.append(children)
                rule = rule+"q"+str(children)+" "
            rule += ")"
        result.append(rule)
    return result

def save_smr_rtg(train, best_smr, treeB, i):
    smr_stack = get_stack_from_ted_repre(best_smr)
    new_smr_tree = createTree(smr_stack, len(treeB))
    tree_smr_dics = get_tree_dic(new_smr_tree, 0)
    rtg = generate_rtg.generate_rtg(tree_smr_dics, treeB, 0)

    if train:
        fout = open("tiburon/amr_train_smr_rtg/smr"+str(i)+".rtg","wt")
    else:
        fout = open("tiburon/amr_test_smr_rtg/smr"+str(i)+".rtg","wt")
    fout.write("q0\n")
    for single_rtg in rtg:
        fout.write(single_rtg+"\n")
    fout.close()


def save(model_trace, train, num_list, iftrain, b):
    treeA_list = model_trace['treeA']
    treeB_list = model_trace['treeB']
    path_list = model_trace['path_list']
    dist_list = model_trace['dist_list']
    best_amr_list = model_trace['best_amr']
    best_smr_list = model_trace['best_smr']

    if iftrain:
        s = 0
        e = train
    else:
        s = train
        e = len(num_list)

    for f in range(s,e,1):
        i = num_list[f]
        print f,i
        treeA = treeA_list[i]
        #for binary
        if b:
            best_amr = best_amr_list[i]
        #not binary
        else:
            best_amr = best_amr_list[i][0]
        treeB = treeB_list[i]
        best_smr = best_smr_list[i]
        trace = path_list[i]
        # print f,i
        # if i == 197:
            # print trace
        #preprocess the data
        treeA, best_amr, treeB, best_smr, trace = preprocess(treeA, best_amr, treeB, best_smr, trace)
        save_smr_rtg(iftrain, best_smr, treeB, i)
        #get the dictionary and map for AMR
        amr_stack = get_stack_from_ted_repre(best_amr)
        new_treeA_map, new_treeB_map = mark_node(amr_stack, trace, treeA, treeB)
        new_tree = createTree(amr_stack, len(treeA))
        tree_amr_dics = get_tree_dic(new_tree, 0)

        #get the dictionary and map for SMR
        smr_stack = get_stack_from_ted_repre(best_smr)
        new_smr_tree = createTree(smr_stack, len(new_treeB_map))
        tree_smr_dics = get_tree_dic(new_smr_tree, 0)

        save_part(iftrain, tree_amr_dics, new_treeA_map, tree_smr_dics, new_treeB_map, i)



def printout(tree_amr_dics, new_treeA_map, tree_smr_dics, new_treeB_map):
    rules = generate(tree_amr_dics, new_treeA_map, tree_smr_dics, new_treeB_map, 0)
    rules = Set(rules)

    print "Rules"
    if len(rules) ==0:
        raise Exception("No Rules generated in this case")
    else:
        print "qr"
        for rule in rules:
            if rule == "unrecognize command":
                raise Exception("Unrecognize Command")
            if rule != "" :
                print rule

    ti_amr = new_treeA_map[0][:new_treeA_map[0].find("$")]
    ti_amr = dfs(tree_amr_dics, 0, Set(), ti_amr, new_treeA_map)
    ti_smr = new_treeB_map[0][:new_treeB_map[0].find("$")]
    ti_smr = dfs(tree_smr_dics, 0 ,Set(), ti_smr, new_treeB_map)
    # print tree_amr_dics
    # print new_treeA_map
    # print tree_smr_dics
    # print new_treeB_map
    print "AMR"
    print ti_amr
    print "SMR"
    print ti_smr

def check_test(model_trace, start, b):
    treeA_list = model_trace['treeA']
    treeB_list = model_trace['treeB']
    path_list = model_trace['path_list']
    dist_list = model_trace['dist_list']
    best_amr_list = model_trace['best_amr']
    best_smr_list = model_trace['best_smr']

    i = start
    treeA = treeA_list[i]
    #for binary
    if b:
        best_amr = best_amr_list[i]
    #not binary
    else:   
        best_amr = best_amr_list[i][0]
    treeB = treeB_list[i]
    best_smr = best_smr_list[i]
    trace = path_list[i]
    #preprocess the data 
    treeA, best_amr, treeB, best_smr, trace = preprocess(treeA, best_amr, treeB, best_smr, trace)

    #get the dictionary and map for AMR
    amr_stack = get_stack_from_ted_repre(best_amr)
    new_treeA_map, new_treeB_map = mark_node(amr_stack, trace, treeA, treeB)
    # print 'new_treeA_map',new_treeA_map
    # print 'new_treeB_map',new_treeB_map
    new_tree = createTree(amr_stack, len(treeA))
    # print 'new_tree', new_tree
    tree_amr_dics = get_tree_dic(new_tree, 0)
    # print tree_amr_dics
        
    #get the dictionary and map for SMR
    # print best_smr
    smr_stack = get_stack_from_ted_repre(best_smr)
    # print smr_stack
    new_smr_tree = createTree(smr_stack, len(new_treeB_map))
    # print 'new_smr_tree',new_smr_tree
    tree_smr_dics = get_tree_dic(new_smr_tree, 0)
    # print tree_smr_dics

    printout(tree_amr_dics, new_treeA_map, tree_smr_dics, new_treeB_map)


if __name__ == "__main__":
    mod = sys.argv[1]
    trace = sys.argv[2]
    train = int(sys.argv[3])
    start = int(sys.argv[4])
    if mod == 'all' and trace == "new960":
        with open("./tiburon/scripts/new_index960/index.txt","r") as f:
            lines = f.read().splitlines()
        train = int(lines[0][lines[0].find(" = ")+3:])
        test = int(lines[1][lines[1].find(" = ")+3:])
        new_list = lines[2][lines[2].find(" = ")+4:-1]

        num_list = new_list.split(", ")
        num_list = [int(s) for s in num_list]
        # num_list = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 39, 40, 42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 58, 59, 60, 61, 62, 63, 64, 65, 67, 68, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 101, 102, 103, 104, 105, 106, 107, 108, 109, 111, 112, 113, 114, 115, 116, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 155, 156, 157, 158, 159, 160, 161, 163, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 178, 180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208, 209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 280, 281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 336, 337, 338, 339, 340, 341, 342, 343, 344, 345, 346, 347, 348, 349, 350, 351, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 362, 363, 364, 365, 366, 367, 368, 369, 370, 371, 372, 373, 374, 375, 376, 377, 378, 379, 380, 381, 382, 383, 384, 385, 386, 387, 388, 389, 390, 391, 392, 393, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 412, 413, 414, 415, 416, 417, 418, 419, 420, 421, 422, 423, 424, 425, 426, 427, 428, 429, 430, 431, 432, 433, 434, 435, 436, 437, 438, 439, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 460, 461, 462, 463, 464, 465, 466, 467, 468, 469, 470, 471, 472, 473, 474, 475, 476, 477, 478, 479, 480, 481, 482, 483, 484, 485, 486, 487, 488, 489, 490, 491, 492, 493, 494, 495, 496, 497, 498, 499, 500, 501, 502, 503, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 517, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 529, 530, 531, 532, 533, 534, 535, 536, 537, 538, 539, 540, 541, 542, 543, 544, 545, 546, 547, 548, 549, 550, 551, 552, 553, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 566, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 585, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 613, 614, 615, 616, 617, 618, 619, 620, 621, 622, 623, 624, 625, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 637, 638, 639, 640, 641, 642, 643, 644, 645, 646, 647, 648, 649, 650, 651, 652, 653, 654, 655, 656, 657, 658, 659, 660, 661, 662, 663, 664, 665, 666, 667, 668, 669, 670, 671, 672, 673, 674, 675, 676, 677, 678, 679, 680, 681, 682, 683, 684, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 696, 697, 698, 699, 700, 701, 702, 703, 704, 705, 706, 707, 708, 709, 710, 711, 712, 713, 714, 715, 716, 717, 718, 719, 720, 721, 722, 723, 724, 725, 726, 727, 728, 729, 730, 731, 732, 733, 734, 735, 736, 737, 738, 739, 740, 741, 742, 743, 744, 745, 746, 747, 748, 749, 750, 751, 752, 753, 754, 755, 756, 757, 758, 759, 760, 761, 762, 763, 764, 765, 766, 767, 768, 769, 770, 771, 772, 773, 774, 775, 776, 777, 778, 779, 780, 781, 782, 783, 784, 785, 786, 787, 788, 789, 790, 791, 792, 793, 794, 795, 796, 797, 798, 799, 800, 801, 802, 803, 804, 805, 806, 807, 808, 809, 810, 811, 812, 813, 814, 815, 816, 817, 818, 819, 820, 821, 822, 823, 824, 825, 826, 827, 828, 829, 830, 831, 832, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 11, 13, 35, 41, 46, 57, 66, 69, 87, 99, 100, 110, 117, 137, 154, 162, 164, 177, 179]
        print 'Data Number:',len(num_list)
        model_trace = pickle.load(open('data/zhangshasha_traces.p','r'))
        save(model_trace, train, num_list, True, False)
        save(model_trace, train, num_list, False, False)
        union_rules.func(num_list, train)
