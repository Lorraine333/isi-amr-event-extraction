from sets import Set
import sys

def get_list(tree):
    stack_list = []
    symbol = ''
    i = 0
    tree = tree[tree.find("TOP(")+4:-1]
    for char in tree:
        if char != '(' and char != ')' and char != " ":
            symbol = symbol+ char
        else:
            if symbol != '':
                if "r_" not in symbol:
                    stack_list.append("x"+str(i)+" / "+symbol)
                    i += 1
                else:
                    stack_list.append(":"+symbol)
            stack_list.append(char)
            symbol = ''
    if "(" not in tree and ")" not in tree and " " not in tree:
        if "r_" not in symbol:
            stack_list.append("x"+str(i)+" / "+symbol)
    return stack_list


def generate_dict_map(tree):
    list_rep = get_list(tree)
    i = 0
    num_rep = []
    mydict = {}
    parent_stack = []
    mymap = {}
    # print list_rep
    for temp in list_rep:
        if temp != '(' and temp != ')' and temp !=' ':
            if "/" in temp and ":r_" in temp:
                t1 = temp[temp.find(":r_")+3:]
                t1 = t1.replace("/","_")
                temp = ":r_"+t1
            mymap[i] = temp
            num_rep.append(i)
            i+=1
        else:
            num_rep.append(temp)
            pass

    for j in range(1,len(num_rep)):
        element = num_rep[j]
        if (element != '(') and (element != ')') and (element != ' '):
            if current_parent in mydict:
                mydict[current_parent].append(element)
            else:
                mydict[current_parent] = [element]
            i+=1
        if element == ')':
            parent_stack.pop()
            if len(parent_stack) != 0:
                current_parent = parent_stack[-1]
        if element == '(':
            parent_stack.append(num_rep[j-1])
            current_parent = parent_stack[-1]
    return mydict, mymap, list_rep

def construct_amr(mydict, mymap, root, visited, seq):
    visited.add(root)
    if root in mydict:
        rel = True
        child = []
        for node in mydict[root]:
            current_node = mymap[node]
            if ":r_" not in current_node:
                rel = False
                child.append(False)
            else:
                child.append(True)
        for node in mydict[root]:
            if node not in visited:
                current_node = mymap[node]
                if rel:
                    current_node = current_node.replace(":r_",":")
                    current_node = current_node.replace("_","\"")
                    if 'op' in current_node:
                        op = current_node[:current_node.find("op")+3]
                        value = current_node[current_node.find("op")+3:]
                        # print op
                        # print value
                        current_node = op +" "+value
                    elif 'value' in current_node:
                        op = current_node[:current_node.find("value")+5]
                        value = current_node[current_node.find("value")+5:]
                        # print op
                        # print value
                        current_node = op+" "+value
                    elif 'quant' in current_node:
                        op = current_node[:current_node.find("quant")+5]
                        value = current_node[current_node.find("quant")+5:]
                        current_node = op +" "+value
                    elif 'mod' in current_node:
                        op = current_node[:current_node.find("mod")+3]
                        value = current_node[current_node.find("mod")+3:]
                        current_node = op +" "+value

                    if ":r_" in mymap[node] and ":r_" not in mymap[root]:
                        child_right = False
                        if node in mydict:
                            for child_id in mydict[node]:
                                if ":r_" not in mymap[child_id]:
                                    child_right = True
                                    break
                        elif ("xref" not in mymap[node]) and ("name") not in mymap[node]:
                            child_right = True
                        if child_right:
                            output = " "+current_node
                            seq += output
                            seq = construct_amr(mydict, mymap, node, visited, seq)
                            seq += " "

                else:

                    if ":r_" not in current_node and ":r_" in mymap[root]:
                        child_right = False
                        if node in mydict:
                            for child_id in mydict[node]:
                                if ":r_" in mymap[child_id]:
                                    child_right = True
                                    break
                        else:
                            child_right = True
                        if child_right:
                            output = "("+current_node
                            seq += output
                            seq = construct_amr(mydict, mymap, node, visited, seq)
                            seq += ")"
        return seq
    else:
        return seq

def save(folder, s, e, num_list):
    for f in range(s,e, 1):
        i = num_list[f]
        # print i
        fin = open(folder+str(i)+".tree","r")
        fout = open(folder+str(i)+".txt","wt")
        lines = fin.read().splitlines()
        single_tree = lines[0][:lines[0].find(" #")]
        if "TOP" in single_tree:
            mydict, mymap, stack_list = generate_dict_map(single_tree)
            amr = "("+stack_list[0]
            amr = construct_amr(mydict, mymap, 0, Set(), amr)
            amr += ")"
            if " :xref " in amr:
                amr = amr.replace(" :xref ","")
            elif " :name" in amr:
                amr = amr.replace(" :name ","")
            fout.write(amr)
        fin.close()
        fout.close()

def printout(folder, s):
    fin = open(folder+str(s)+".tree","r")
    lines = fin.read().splitlines()
    # single_tree = lines[0][:lines[0].find(" #")]
    if lines[0].find(" #") != -1:
        single_tree = lines[0][:lines[0].find(" #")]
    else:
        single_tree = lines[0][:]
        single_tree.strip()
    print single_tree
    if "TOP" in single_tree:
        mydict, mymap, stack_list = generate_dict_map(single_tree)
        print mydict
        print mymap
        print stack_list
        amr = "("+stack_list[0]
        amr = construct_amr(mydict, mymap, 0, Set(), amr)
        amr += ")"
        if " :xref " in amr:
            amr = amr.replace(" :xref ","")
        elif " :name " in amr:
            amr = amr.replace(" :name ","")
        elif " :ARG1 )" in amr:
            amr = amr.replace(" :ARG1 )",")")
        elif " :ARG0 )" in amr:
            amr = amr.replace(" :ARG0 )",")")
        elif " :ARG2 )" in amr:
            amr = amr.replace(" :ARG2 )",")")
        elif " :ARG1 :" in amr:
            amr = amr.replace(" :ARG1 :","")
        elif " :ARG0 :" in amr:
            amr = amr.replace(" :ARG0 :","")
        elif " :ARG2 :" in amr:
            amr = amr.replace(" :ARG2 :","")
        print amr
    fin.close()

if __name__ == "__main__":
    mod = sys.argv[1]
    index_file = sys.argv[2]

    with open(index_file+"/index.txt","r") as f:
        lines = f.read().splitlines()
    train = int(lines[0][lines[0].find(" = ")+3:])
    test = int(lines[1][lines[1].find(" = ")+3:])
    new_list = lines[2][lines[2].find(" = ")+4:-1]

    num_list = new_list.split(", ")
    
    

    if mod == "train_smr":
        s = 0
        e = train
        folder = "../amr_train_smr_tree/smr"
        save(folder, s, e, num_list)
    elif mod == "train_single_best":
        s = 0
        e = train
        folder = "../amr_train_single/generate"
        save(folder, s, e, num_list)
    elif mod == "train_union_best":
        s = 0
        e = train
        folder = "../amr_train_single/generate_prob"
        save(folder, s, e, num_list)
    elif mod == "test_smr":
        s = train
        e = len(num_list)
        folder = "../amr_test_smr_tree/smr"
        save(folder, s, e, num_list)
    elif mod == "test_best":
        s = train
        e = len(num_list)
        folder = "../amr_test/test_prob"
        save(folder, s, e, num_list)
    elif mod == "single":
        s = 201
        # folder = "../amr_train_smr_tree/smr"
        # folder = "../amr_train_single/generate"
        folder = "../amr_train_single/generate_prob"
        printout(folder, s)
    else:
        raise Exception("Wrong input!")

    

