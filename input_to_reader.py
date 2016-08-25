def getAMR(filename, smr):
    fin = open(filename)
    lines = fin.readlines()
    result = []
    snt_id = []
    snt = []
    i = 0
    while i <= len(lines)-1:
        line = lines[i]
        if line.startswith("# ::id"):
            single_snt_id = line[line.find("# ::id")+7:].strip()
            if smr:
                single_snt_id = single_snt_id[:single_snt_id.find(" ::date")].strip()
                single_snt_id = single_snt_id.replace("_","")
            snt_id.append(single_snt_id)
        elif line.startswith("# ::snt"):
            single_snt = line[line.find("# ::snt")+8:].strip()
            snt.append(single_snt)
        elif line.startswith("("):
            temp = ''
#             #Until a new empty line
            while (i <= len(lines)-1) and (lines[i] !='\n'):
                temp = temp + lines[i]
                i = i+1
            result.append(temp)
        i = i+1
    fin.close()
    return snt_id, snt, result



def multismr(old_AMR, old_SMR, amr_id, AMR, smr_id, SMR, smr_index, amr_index, count):
    parts_smr = old_SMR[smr_index].split("\n")
    uni_amr = old_AMR[amr_index]
    i = 0
    while i<=len(parts_smr)-1:
        if (parts_smr[i].find(":card")!=-1) and "multi-index-card" not in parts_smr[i]:
            temp = parts_smr[i][parts_smr[i].find(":card")+7:]+"\n"
            i+=1
            while (i <= len(parts_smr)-1) and (parts_smr[i].find(':card')==-1):
                temp = temp + (parts_smr[i]) + "\n"
                i += 1
            amr_id.append(count)
            AMR.append(uni_amr)
            smr_id.append(count)
            SMR.append(temp)
            count += 1
        else:
            i += 1
    return amr_id, AMR, smr_id, SMR, count



def multiamr(old_AMR, old_SMR, amr_id, AMR, smr_id, SMR, smr_index, amr_index, count):
    parts_amr = old_AMR[amr_index].split("\n")
    uni_smr = old_SMR[smr_index]
    i = 0
    while i<=len(parts_amr)-1:
        if (parts_amr[i].find(":snt")!=-1) and "multi-sentence" not in parts_amr[i]:
            temp = parts_amr[i][parts_amr[i].find(":snt")+6:]+"\n"
            i+=1
            while (i <= len(parts_amr)-1) and (parts_amr[i].find(':snt')==-1):
                temp = temp + (parts_amr[i]) + "\n"
                i += 1
            amr_id.append(count)
            SMR.append(uni_smr)
            smr_id.append(count)
            AMR.append(temp)
            count += 1
        else:
            i += 1
    return amr_id, AMR, smr_id, SMR, count



def multiamrsmr(old_AMR, old_SMR, amr_id, AMR, smr_id, SMR, smr_index, amr_index, count):
    parts_smr = old_SMR[smr_index].split("\n")
    parts_amr = old_AMR[amr_index].split("\n")
    uni_smr = old_SMR[smr_index]
    uni_amr = old_AMR[amr_index]
    smr_list = []
    amr_list = []
    i = 0
    while i<=len(parts_smr)-1:
        if (parts_smr[i].find(":card")!=-1) and "multi-index-card" not in parts_smr[i]:
            temp = parts_smr[i][parts_smr[i].find(":card")+7:]+"\n"
            i+=1
            while (i <= len(parts_smr)-1) and (parts_smr[i].find(':card')==-1):
                temp = temp + (parts_smr[i]) + "\n"
                i += 1
            smr_list.append(temp)
        else:
            i += 1

    i = 0
    while i<=len(parts_amr)-1:
        if (parts_amr[i].find(":snt")!=-1) and "multi-sentence" not in parts_amr[i]:
            temp = parts_amr[i][parts_amr[i].find(":snt")+6:]+"\n"
            i+=1
            while (i <= len(parts_amr)-1) and (parts_amr[i].find(':snt')==-1):
                temp = temp + (parts_amr[i]) + "\n"
                i += 1
            amr_list.append(temp)
        else:
            i += 1
    for single_amr in amr_list:
        for single_smr in smr_list:
            amr_id.append(count)
            SMR.append(single_smr)
            smr_id.append(count)
            AMR.append(single_amr)
            count += 1
    return amr_id, AMR, smr_id, SMR, count


def test(amr_id, amr_snt, AMR, smr_id, smr_snt, SMR):
    total = 0
    new_amr_id = []
    new_AMR = []
    new_smr_id = []
    new_SMR = []
    num = 0
    for i in range(len(smr_id)):
        for j in range(len(amr_id)):
            uni_smrid = smr_id[i]
            uni_amrid = amr_id[j]
            if uni_smrid.lower() == uni_amrid.lower():
                parts_amr = AMR[j].split("\n")
                parts_smr = SMR[i].split("\n")
                total+=1
                if "multi-index-card" in parts_smr[0] and "multi-sentence" not in parts_amr[0]:
                    new_amr_id, new_AMR, new_smr_id, new_SMR, num = multismr(AMR, SMR, new_amr_id, new_AMR, new_smr_id, new_SMR, i, j, num)
                elif "multi-sentence" in parts_amr[0] and "multi-index-card" not in parts_smr[0]:
                    new_amr_id, new_AMR, new_smr_id, new_SMR, num = multiamr(AMR, SMR, new_amr_id, new_AMR, new_smr_id, new_SMR, i, j, num)
                elif "multi-sentence" in parts_amr[0] and "multi-index-card" in parts_smr[0]:
                    new_amr_id, new_AMR, new_smr_id, new_SMR, num = multiamrsmr(AMR, SMR, new_amr_id, new_AMR, new_smr_id, new_SMR, i, j, num)
                    
                else:
                    new_amr_id.append(num)
                    new_smr_id.append(num)
                    new_SMR.append(SMR[i])
                    new_AMR.append(AMR[j])
                    num +=1
    return new_amr_id, new_smr_id, new_AMR, new_SMR



def write(filename, amr):
    fout = open(filename,'w')
    i = 0
    for uni_amr in amr:
        fout.write(str(i)+uni_amr+"\n")
        i+=1
    fout.close()

if __name__ == "__main__":
    #generative AMR, over 2000 AMRs
    amr_id, amr_snt, AMR = getAMR("data/bbadarau-bioset-combined.fixed-pmc.amrs.with-ids.grounded", False)
    #smr contains 95 SMRs
    smr_id, smr_snt, SMR = getAMR("data/bbadarau-bioset-reference_SMR_MITRE-2016-08-02.smrs.txt", True)
    #smr contains 413 SMRs 
    smr1_id, smr1_snt, SMR1 = getAMR("data/bbadarau-bioset-hv-snt1-2016-08-03.smrs.txt", True)

    # print len(amr_id), len(amr_snt), len(AMR)
    # print len(smr_id), len(smr_snt), len(SMR)

    #for 95 SMRs
    new_amr_id, new_smr_id, new_AMR, new_SMR = test(amr_id, amr_snt, AMR, smr_id, smr_snt, SMR)
    #for 413 SMRs
    amrid1, smrid1, AMR1, SMR1 = test(amr_id, amr_snt, AMR, smr1_id, smr1_snt, SMR1)


    t_new_amr_id = amrid1+new_amr_id
    t_new_smr_id = smrid1+new_smr_id
    t_new_AMR = new_AMR+AMR1
    t_new_SMR = new_SMR+SMR1
    # print len(t_new_amr_id)
    # print len(t_new_smr_id)
    # print len(t_new_AMR)
    # print len(t_new_SMR)
    write("data/AMR186.txt", new_AMR)
    write("data/SMR186.txt", new_SMR)
    write("data/AMR960.txt", t_new_AMR)
    write("data/SMR960.txt", t_new_SMR)






