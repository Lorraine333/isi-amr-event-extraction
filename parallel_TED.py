import pickle

def distribu(key, value):
	total = 0
	i = 0
	breakpoint = []
	while i < len(key):
		k = key[i]
		v = value[i]
		total = v
		while total<500 and (i+1) < len(key):
			i += 1
			k = key[i]
			v = value[i]
			total += v
		breakpoint.append(i+1)
		i+=1
	return breakpoint

def makelist(dics):
	key = []
	value = []
	for k in dics:
		key.append(k)
		value.append(dics[k])
	return key, value

def write(breakpoint):
	i = 0
	f = open("command/run.sh","wt")
	f.write("array=(")
	while i < (len(breakpoint)-1):
		f.write(str(i)+" ")
		fout = open("command/run"+str(i)+".pbs","wt")
		fout.write("#!/bin/bash\n#PBS -l nodes=1:ppn=2\n#PBS -l walltime=100:00:00\n")
		fout.write("python zhang_shasha_master/new_data_zss/get_shortest_TED.py "+str(breakpoint[i])+" "+str(breakpoint[i+1])+"\n")
		i+=1
	f.write(")\n")
	f.write("for i in \"${array[@]}\"\n")
	f.write("do\nqsub -q isi -l walltime=100:00:00 run$i.pbs\n done;\n")
	f.close()


if __name__ == '__main__':
	dics= pickle.load(open("data/smr_map.p", "r"))
	key, value = makelist(dics)
	breakpoint = distribu(key, value)
	print breakpoint
	write(breakpoint)