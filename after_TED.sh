num=$1
train=$[$num-19]
python generate_state_rule.py all new$num $train 0
cd tiburon/scripts
./run_all.sh ./new_index$num > ../../result/unk_concept_role_arbi_node$num.txt
