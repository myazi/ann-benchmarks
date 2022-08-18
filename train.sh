#########################################################################
# File Name: train.sh
# Author: yingwenjie
# mail: yingwenjie.com
# Created Time: Fri 13 May 2022 10:27:43 AM CST
#########################################################################
#!/bin/bash

#/mnt/work/yingwenjie/python36/bin/python run.py --dataset aurora_5M --definitions algos_10M.yaml --algorithm scann -k 100

#/mnt/work/yingwenjie/python36/bin/python run.py --dataset aurora_30M --definitions algos_10M.yaml --algorithm hnsw_sq8\(faiss\) -k 100

/root/anaconda3/envs/python_ann/bin/python run.py --dataset aurora_1M --definitions algos_modify.yaml --algorithm hnsw_sq8\(faiss\) -k 100

#/root/anaconda3/envs/python_ann/bin/python plot.py --dataset aurora_1M --count 100 --recompute
