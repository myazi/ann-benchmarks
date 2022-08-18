# -*- coding: utf-8 -*-
import sys
import json
import time

def get_q2p(file_name):
    d = {}
    with open(file_name) as f:
        for line in f:
            line_list = line.strip('\n').split('\t')
            if len(line_list) < 2:
                continue
            #query_id, query_content, para_id, offset, rank, dist = line_list
            #query_id, para_id, sim = line_list
            #query_id, topk, para_u, para_t, para_p, para_id = line_list
            query_id, para_id = line_list[0:2]
            d.setdefault(query_id,[])
            d[query_id].append(para_id)
    return d

def cal_pre(baseline_dict, test_dict, topK=50):
    all = 0 
    pre = 0
    #if len(baseline_dict) != len(test_dict):
    #    print("file is error")
    #    return
    for qid in test_dict:
        test_list = test_dict[qid]
        if qid not in baseline_dict:
            print("qid file is error")
            return
        baseline_list = baseline_dict[qid]
        for pid in test_list[0:topK]:
            all += 1
            if pid in baseline_list[0:topK]:
            #if str(int(pid)+1) in baseline_list[0:topK]:
                pre += 1
    if all == 0 : return -1 
    print(str(all) + "\t" + str(pre))
    pre = round(pre/float(all),4)
    print(pre)
    return pre
    

if __name__ == "__main__":

    baseline_file = sys.argv[1]
    test_file = sys.argv[2]
    topK = sys.argv[3]
    topK = int(topK)

    baseline_dict = get_q2p(baseline_file)
    test_dict = get_q2p(test_file)
    pre = cal_pre(baseline_dict, test_dict , topK)
