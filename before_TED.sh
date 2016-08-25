#!/bin/sh
# $1 = training data size
num=$1
# upload = $2
echo "Preparing Data to AMR reader......"
python input_to_reader.py 
echo "Reading Data using AMR reader......"
python amr_reader.py SMR $num > data/smr_list$num.txt
python amr_reader.py AMR $num > data/amr_list$num.txt

#get the TED input representation
python main.py save 0 $num

#upload to hpc to run zss
# if [ $upload = "True" ]; then
# 	scp -r data/zhangshasha_amr_input.p xl_780@hpc-login2.usc.edu:
# 	scp -r data/zhangshasha_smr_input.p xl_780@hpc-login2.usc.edu:
# 	scp -r command/ xl_780@hpc-login2.usc.edu:
#download running result from hpc
# scp -r xl_780@hpc-login2.usc.edu:new_data960/ ./
# python combine.py

#if not uploading, still works on local machine while taking really long time especially 
#for large data set.
#"""After this, all TED result will be saved in data/zhangshasha_traces.p"""
python ted/get_shortest_TED.py 0 $num
