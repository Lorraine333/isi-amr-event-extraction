from collections import deque
import sys

def get_list(tree):
    stack_list = []
    symbol = ''
    for char in tree:
        if char != '(' and char != ')' and char != " ":
            symbol = symbol+ char
        else:
            if symbol != '':
                stack_list.append(symbol)
            stack_list.append(char)
            symbol = ''
    return stack_list

def generate_dict_map(tree):
    list_rep = get_list(tree)
    i = 0
    num_rep = []
    mydict = {}
    parent_stack = []
    mymap = {}
    for temp in list_rep:
        if temp != '(' and temp != ')' and temp !=' ':
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
    return mydict, mymap


def generate_rtg(mydict, mymap, root):
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

def save(fin_folder, fout_folder, s, e, num_list):
    for f in range(s, e, 1):
    # for f in range(0,1,1):
        i = num_list[f]
        fin = open(fin_folder+str(i)+".tree","r")
        fout = open(fout_folder+str(i)+".rtg","wt")

        tree = fin.readlines()
        line = tree[0]
        single_tree = line[:line.find("#")]
        # print single_tree
        if single_tree!="0":
            mydict, mymap = generate_dict_map(single_tree)
            rtg = generate_rtg(mydict, mymap, 0)
            fout.write("q0\n")
            for t in rtg:
                fout.write(t+"\n")
        else:
            pass
        fin.close()
        fout.close()

def printout(fin_folder, fout_folder, s, e, num_list):
    # for f in range(s, e, 1):
    for f in range(0,1,1):
        i = num_list[f]
        fin = open(fin_folder+str(i)+".tree","r")
        fout = open(fout_folder+str(i)+".rtg","wt")

        tree = fin.readlines()
        line = tree[0]
        single_tree = line[:line.find("#")]
        print single_tree
        if single_tree!="0":
            mydict, mymap = generate_dict_map(single_tree)
            print mydict, mymap
            rtg = generate_rtg(mydict, mymap, 0)
            print "q0"
            for t in rtg:
                print t
        else:
            pass
        fin.close()
        fout.close()

if __name__ == "__main__":
    mod = sys.argv[1]
    index_file = sys.argv[2]

    with open(index_file+"/index.txt","r") as f:
        lines = f.read().splitlines()
    train = int(lines[0][lines[0].find(" = ")+3:])
    test = int(lines[1][lines[1].find(" = ")+3:])
    new_list = lines[2][lines[2].find(" = ")+4:-1]

    num_list = new_list.split(", ")
    


    if mod == "train":
        s = 0
        e = train
        fin_folder = "../amr_train_single/generate"
        fout_folder = "../amr_train_single/best"
        save(fin_folder, fout_folder, s, e, num_list)
    elif mod == "union":
        s = 0
        e = train
        fin_folder = "../amr_train_single/generate_prob"
        fout_folder = "../amr_train_single/best_prob"
        save(fin_folder, fout_folder, s, e, num_list)
    elif mod == "test_now":
        s = train
        e = len(num_list)
        fin_folder = "../amr_test/test_prob"
        fout_folder = "../amr_test/test_best_prob"
        save(fin_folder, fout_folder, s, e, num_list)
    elif mod == "check":
        s = 0
        e = train
        fin_folder = "../amr_train_single/generate"
        fout_folder = "../amr_train_single/best"
        printout(fin_folder, fout_folder, s, e, num_list)


