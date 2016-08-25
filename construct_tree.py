from sets import Set
import sys
import cPickle

def readin(filename):
    inputfile = open(filename, 'r')
    lines = inputfile.read().splitlines()
    i = 0
    amr = []
    while i < len(lines):
    #     print i
        temp = []
        temp_line = lines[i]
        while temp_line!="*"*50:
            temp.append(temp_line)
            i += 1
            temp_line = lines[i]

        else:
            amr.append(temp)
            i += 1
    inputfile.close()
    return amr

def get_dics(lines):
    dics = {}
    root = ""
    j = 0
    for i in range(len(lines)):
        line = lines[i]
        if line.find("is-a")!= -1:
            t1 = line[:line.find("is-a")]
            t2 = line[line.find("is-a")+5:]
            t1 = t1.strip()
            t2 = t2.strip()
            dics[t1] = t1+'$'+t2
            if j == 0:
                root = t1+'$'+t2
            j += 1
    return dics, root

def get_skipline(lines):
    i = 0;
    stack = []
    j = 0
    yes = False
    while j< len(lines) and not yes:
        if lines[j] == "{":
            yes = True
            mark = j
            stack.append(lines[j])
        j += 1
    j = mark+1
    if stack == []:
        return 0
    else:
        while j< len(lines) and stack != []:
            if lines[j] == "{":
                stack.append(lines[j])
            elif lines[j] == "}":
                stack.pop()
            j += 1
        return j-mark+1
        

def all_func(dics, lines):
    delimiter = "*****"
    newlines = []
    num = 0
    i = 0
    compared = False
    compare = []
    while i < len(lines)-1:
        if lines[i].find("has-a")!= -1:
            line = lines[i]
            if "has-a :prob" in line:
                i +=1
                pass
            else:
                t3 = line[:line.find("has-a")-1] 
                t4 = line[line.find("has-a")+6:] 
                t5 = t4[t4.find(" ")+1:] 
                t4 = t4[t4.find(":")+1:t4.find(" ")] 
    
                temp_line = line
                if temp_line in compare:
                    compared = True
                    ans = get_skipline(lines[i:])
                    i += ans
                else:
                    compare.append(temp_line)
                    if (t5.islower()) and ("\"" not in t5):
                        line = line.replace(t4,t3+t5+"$r_"+t4)
                        t4 = t3+t5+"$r_"+t4 
                    elif t5.isdigit():
                        line = line.replace(" "+t5,"")
                        line = line.replace(t4,"r_"+t4 + "_"+t5+"_")
                        t4 = "r_"+t4 + "_"+t5+"_"
                    else:
                        line = line.replace(t4,t3+"$r_"+t4)

                        t4 = t3+"$r_"+t4 

                    line = line.replace(t3, dics[t3],1)
                    line = line.replace(" has-a :",delimiter)
                    if (t5.islower()) and ("\"" not in t5):
                        line = line.replace(" "+t5,"")
                    else:
                        line = line.replace(" \"", "(")
                        line = line.replace("\"",")")
                    newlines.append(line)

                    if t5 in dics:
                        newlines.append(t4+delimiter+dics[t5])
                    i+=1
        else:
            i+=1
            
    for j in range(len(newlines)):
        new_line = newlines[j]
        new_line = new_line.replace(" ","_")
        newlines[j] = new_line
        t1 = new_line[:new_line.find(delimiter)]
        t2 = new_line[new_line.find(delimiter)+len(delimiter):]
        t1 = t1.strip()
        t2 = t2.strip()
        if (("value" in new_line) or ("prob" in new_line)) and "$" not in t2:
            new_line = new_line.replace(t2,t1[:t1.find("$")+1]+t2)
            newlines[j] = new_line
        if t1 == t2:
            newlines.remove(new_line)
    return newlines


def get_ordered_child(tree_dict, root):
    children = tree_dict[root]
    children.sort()
    return children

def dfs(tree_dict, root, visited, seq):
    visited.add(root)
    if root in tree_dict:
        i=0
        for node in get_ordered_child(tree_dict, root):
            if node not in visited:
                if i==0:
                    if node.find("$")!=-1:
                        temp = node[node.find("$")+1:]
                        output = "("+temp 
                    else:
                        output = "("+node
                else:
                    if node.find("$")!=-1:
                        temp = node[node.find("$")+1:]
                        output = " "+temp 
                    else:
                        output = " "+node
                i = i+1
                seq += output
                seq = dfs(tree_dict, node, visited, seq)
            else:
                return seq
        seq += ")"
        return seq
    else:
        return seq


def get_graph(zhangshasha):
    delimiter = "*"*5
    graph_dics = {}
    root = zhangshasha[0].split(delimiter)[0]
    for line in zhangshasha:
        parent,child = line.split(delimiter)
        if "(" in child and ")" in child:
            child = child.replace("(","_")
            child = child.replace(")","_")
        if parent in graph_dics:
            graph_dics[parent].append(child)
        else:
            graph_dics[parent] = [child]
    return graph_dics


def save_params(filename,s,e, smrs):
    save_result = {}
    result_dict = []
    result_root = []

    for i in range(s,e,1):
        # print 'Process',i,'th AMR-SMR pair now'
        smr_tree = smrs[i]
        dics, root = get_dics(smr_tree)
        zhangshasha = all_func(dics,smr_tree)
        if len(zhangshasha) > 0:
            graph_dics = get_graph(zhangshasha)
        else:
            if "immortalize" in root:
                graph_dics = {'x2$immortalize-03':[]}
            else:
                graph_dics = {'s$smr-empty':[]}
        result_dict.append(graph_dics)
        result_root.append(root)
    save_result['dics'] = result_dict
    save_result['root'] = result_root
    cPickle.dump(save_result, filename, protocol=cPickle.HIGHEST_PROTOCOL)
    filename.close()

def check(s,e, smrs):
    for i in range(s,e,1):
        print 'Process',i,'th AMR-SMR pair now'
        smr_tree = smrs[i]
        dics, root = get_dics(smr_tree)
        zhangshasha = all_func(dics,smr_tree)
        graph_dics = get_graph(zhangshasha)
        # print 'zhangshasha',zhangshasha
        print 'graph_dics',graph_dics
        print 'root',root

                
if __name__ == "__main__":
    mod = sys.argv[1]
    start = sys.argv[2]
    num = sys.argv[3]
    amrs = readin("data/amr_list"+num+".txt")
    smrs = readin("data/smr_list"+num+".txt")
    if mod == "save":
        f_smr = open("data/smrs_permutation_input.p","wb")
        f_amr = open("data/amrs_permutation_input.p","wb")
        s = 0
        e = len(smrs)
        print e
        save_params(f_smr,s,e,smrs)
        save_params(f_amr,s,e,amrs)
    elif mod == "test":
        s = int(start)
        e = int(start)+1
        check(s, e, smrs)
        check(s, e, amrs)
    else:
        raise Exception("Wrong input!")



