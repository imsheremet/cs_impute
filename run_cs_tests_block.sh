#!/bin/bash

set -e

# script parameters
SEQ_LEN=72

NUM_FEAT_ITERATIONS=1
NUM_BLK_ITERATIONS=36

# create results file
timestamp=$(date +%s)
results_file_path="cs_test_results/tests_results_block_${timestamp}.csv"
touch $results_file_path
printf "mask_feat,block_len,MAE,RMSE,MRE\n" >> $results_file_path

# run multiple iterations with different missing block sizes
for i in $(seq 1 $NUM_FEAT_ITERATIONS)
do
    for j in $(seq 1 $NUM_BLK_ITERATIONS)
    do
        mask_block_len=$((2*j))

        echo ""
        echo "-------------------------------------------------------------------"
        echo "| Mask num. features: $i Mask block length: $mask_block_len"
        echo "-------------------------------------------------------------------"

        # select dataset; note that the dataset needs to be generated, and the SAITS
        # code needs to be in the parent directory
        printf "\n---- Selecting dataset ----\n\n"
        cd ../SAITS/generated_datasets
        if [ -d DSM2 ]; then
            rm -rf DSM2
        fi
        dataset_path=DSM2_seqlen${SEQ_LEN}_block_maskfeat${i}_blocklen${mask_block_len}
        ln -s $dataset_path DSM2
        cd -
        echo "selected $dataset_path"

        # run SAITS model
        printf "\n---- Running CS model ----\n\n"
        python run_cs_model.py

        # get test metrics
        mae=$(grep -i 'imputation_MAE'  cs_result.txt | awk 'NF{ print $NF }')
        rmse=$(grep -i 'imputation_RMSE'  cs_result.txt | awk 'NF{ print $NF }')
        mre=$(grep -i 'imputation_MRE'  cs_result.txt | awk 'NF{ print $NF }')

        # save test metrics to file
        printf "\n---- Saving results ----\n\n"
        printf "%i,%i,%4.3f,%4.3f,%4.3f\n" $i $mask_block_len $mae $rmse $mre >> $results_file_path
        echo "saved results to $results_file_path"

    done
done

# cleanup
rm cs_result.txt
