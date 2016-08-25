index_file=$1
# index_file="new_index960"
#####################################train#############################################
for i in $(cat $index_file/index_train_batch.txt); do
	#single_membership_test
	# echo $i
	.././tiburon ../amr_train_amr_tree/amr$i.tree ../amr_train_single_trans/simple$i.trans > ../amr_train_single/single$i.rtg
	.././tiburon ../amr_train_single/single$i.rtg ../amr_train_smr_rtg/smr$i.rtg > ../amr_train_single/$i.result
	#union_membership_test
	.././tiburon ../amr_train_amr_tree/amr$i.tree ../union.trans > ../amr_train_union/union_$i.rtg
	.././tiburon ../amr_train_union/union_$i.rtg ../amr_train_smr_rtg/smr$i.rtg > ../amr_train_union/$i.result
	#single_number
	.././tiburon -c ../amr_train_amr_tree/amr$i.tree ../amr_train_single_trans/simple$i.trans > ../amr_single_result_tree/result$i.tree
	#union_number
	.././tiburon -c ../amr_train_amr_tree/amr$i.tree ../union.trans > ../amr_union_result_tree/result$i.tree
	#single_best
	.././tiburon -k 1 ../amr_train_amr_tree/amr$i.tree ../amr_train_single_trans/simple_prob$i.trans > ../amr_train_single/generate$i.tree
	# union_best
	.././tiburon -k 1 ../amr_train_amr_tree/amr$i.tree ../union_prob.trans > ../amr_train_single/generate_prob$i.tree
done
echo "******************************single membership test******************************"
python check_membership.py single $index_file
echo "******************************union membership test******************************"
python check_membership.py union $index_file
echo "******************************single rule number******************************"
python count.py single $index_file
echo "******************************union rules number******************************"
python count.py union $index_file

#for train best testing
python get_generate_rtg.py train $index_file
python get_generate_rtg.py union $index_file
for j in $(cat $index_file/index_train_batch.txt); do
	.././tiburon ../amr_train_single/best$j.rtg ../amr_train_smr_rtg/smr$j.rtg > ../amr_train_single/best$j.result
	.././tiburon ../amr_train_single/best_prob$j.rtg ../amr_train_smr_rtg/smr$j.rtg > ../amr_train_single/best_prob$j.result
done

#for train best testing
echo "******************************single best******************************"
python check_membership.py single_count $index_file
echo "******************************union best******************************"
python check_membership.py union_count $index_file

####################################test#############################################
for i1 in $(cat $index_file/index_test_batch.txt); do 
	#test_membership 
	.././tiburon ../amr_test_amr_tree/amr$i1.tree ../union.trans > ../amr_test/test$i1.rtg
	.././tiburon ../amr_test/test$i1.rtg ../amr_test_smr_rtg/smr$i1.rtg > ../amr_test/$i1.result
	#test_number
	.././tiburon -c ../amr_test_amr_tree/amr$i1.tree ../union.trans > ../amr_test_result_tree/result$i1.tree
	#test_best
	.././tiburon -k 1 ../amr_test_amr_tree/amr$i1.tree ../union_prob.trans > ../amr_test/test_prob$i1.tree
done
echo "******************************test membership******************************"
python check_membership.py test_now $index_file
echo "******************************test count******************************"
python count.py test_now $index_file

#for best_testing
python get_generate_rtg.py test_now $index_file
for j1 in $(cat $index_file/index_test_batch.txt); do  
	.././tiburon ../amr_test/test_best_prob$j1.rtg ../amr_test_smr_rtg/smr$j1.rtg > ../amr_test/test_prob$j1.result
done
echo "******************************test best******************************"
python check_membership.py test_count $index_file

echo "******************************test can generate some smr******************************"
rm can_test.txt
for k in $(cat $index_file/index_test_batch.txt); do 
	echo "#"$k >> can_test.txt; .././tiburon -c ../amr_test_amr_tree/amr$k.tree ../union.trans >>can_test.txt; done;
python can_test.py

#####################################smatch_train###########################################
rm test_single.txt
rm test_union.txt
rm test_test_now.txt
python generate_amr.py train_smr $index_file
python generate_amr.py train_single_best $index_file
python generate_amr.py train_union_best $index_file
for i2 in $(cat $index_file/index_train_batch.txt); do 
	python ../../smatch_2.0/smatch.py -f /Users/lorraine/Uchicago/USC/Code/package_code/tiburon/amr_train_smr_tree/smr$i2.txt /Users/lorraine/Uchicago/USC/Code/package_code/tiburon/amr_train_single/generate$i2.txt >> test_single.txt
	python ../../smatch_2.0/smatch.py -f /Users/lorraine/Uchicago/USC/Code/package_code/tiburon/amr_train_smr_tree/smr$i2.txt /Users/lorraine/Uchicago/USC/Code/package_code/tiburon/amr_train_single/generate_prob$i2.txt >> test_union.txt
done

echo "******************************average single smatch score******************************"
python test.py single
echo "******************************average union smatch score******************************"
python test.py union

######################################smatch_test###########################################
python generate_amr.py test_smr $index_file
python generate_amr.py test_best $index_file
for j2 in $(cat $index_file/index_test_batch.txt); do 
	python ../../smatch_2.0/smatch.py -f /Users/lorraine/Uchicago/USC/Code/package_code/tiburon/amr_test_smr_tree/smr$j2.txt /Users/lorraine/Uchicago/USC/Code/package_code/tiburon/amr_test/test_prob$j2.txt >> test_test_now.txt
done
echo "******************************average test smatch score******************************"
python test.py test_now


