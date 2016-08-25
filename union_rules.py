from __future__ import division

def func(num_list, train):
    inputlist = []
    for f in range(train):
        i = num_list[f]
        inputlist.append(i)
    total_rule, total = union_rules(inputlist)
    print 'Total Number of Rules:',total
    order_by_rule(total_rule)
    order_by_value(total_rule)
    prob = count_union_rules(total_rule)
    count_single_rules(num_list, train, prob)


def union_rules(inputlist):
    total_rule = {}
    for i in inputlist:
        fin = open("tiburon/amr_train_single_trans/simple"+str(i)+".trans","r")
        lines = fin.read().splitlines()
        for line in lines:
            if line != "qr":
                if line not in total_rule:
                    total_rule[line] = 1
                else:
                    total_rule[line] += 1
        fin.close()

    d = total_rule
    fout = open("tiburon/union.trans","wt")
    fout.write("qr\n")
    for w in sorted(d, key=d.get, reverse=True):
        fout.write(w+"\n")
    fout.close()
    return total_rule, len(total_rule)

def order_by_rule(total_rule):
    fout = open("tiburon/orderbyrule.rule","wt")
    for key in sorted(total_rule):
        fout.write(key+" #"+str(total_rule[key])+"\n")
    fout.close()

def order_by_value(total_rule):
    d = total_rule
    fout = open("tiburon/orderbyvalue.rule","wt")
    for w in sorted(d, key=d.get, reverse=True):
        fout.write(w+" #"+str(d[w])+"\n")
    fout.close()

def count_union_rules(total_rule):
    prob = {}
    rhs = {}
    for line in total_rule:
        right = line[:line.find(" -> ")]
        if right in rhs:
            rhs[right] += total_rule[line]
        else:
            rhs[right] = total_rule[line]
    fout = open("tiburon/union_prob.trans","wt")
    fout.write("qr\n")
    for key in sorted(total_rule):
        right_key = key[:key.find(" -> ")]
        dominater = rhs[right_key]
        prob[key] = total_rule[key]/dominater
        fout.write(key+" #"+str(total_rule[key]/dominater)+"\n")
    fout.close()
    return prob

def count_single_rules(num_list, train, prob):
    for f in range(train):
        i = num_list[f]
        fin = open("tiburon/amr_train_single_trans/simple"+str(i)+".trans",'r')
        fout = open("tiburon/amr_train_single_trans/simple_prob"+str(i)+".trans",'wt')
        lines = fin.read().splitlines()
        fout.write("qr\n")
        for j in range(1,len(lines),1):
            fout.write(lines[j]+" #"+ str(prob[lines[j]])+"\n")
        fin.close()
        fout.close()

