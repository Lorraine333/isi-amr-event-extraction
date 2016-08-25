from collections import deque
import itertools

def get_permutation(input_list):
    return itertools.permutations(input_list)

def generate_rtg(mydict, mymap, root):
    result = []
    myqueue = deque([root])
    while len(myqueue) != 0:
        node = myqueue.popleft()
        rule = "q"+str(node) + " -> "
        rule = rule+mymap[node].replace(" ","_")
        # print rule
        if node in mydict:
            rule += "("
            single_rule = rule
            for children in mydict[node]:
                myqueue.append(children)
                single_rule = single_rule+"q"+str(children)+" "
            single_rule += ")"
            if single_rule not in result:
                result.append(single_rule)
            if len(mydict[node]) > 1:
                single_rule = rule
                for value in get_permutation(mydict[node]):
                    for v in value:
                        single_rule = single_rule + "q"+str(v)+" "
                    single_rule += ")"
                    if single_rule not in result:
                        result.append(single_rule)
                    single_rule = rule
        else:
            result.append(rule)
    return result


if __name__ == "__main__":
    mydict = {0:[1],1:[2,3],2:[4,5,6]}
    mymap = {0:'a$',1:'b$',2:'c$',3:'d$',4:'e$',5:'f$',6:'h$'}
    result = generate_rtg(mydict, mymap, 0)
    for i in result:
        print i