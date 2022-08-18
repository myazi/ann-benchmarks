# -*- coding: utf-8 -*-

import sys
import urllib
import requests
import numpy as np
import random
import json
import time

def load_vector_query(inp_file):
    """
    入参: query向量文件， 格式 vec "\t" query内容, vec空格分割
    """
    vec_list = []
    query_list = []
    for line in open(inp_file):
        line_list = line.strip('\n').split("\t")
        if len(line_list) < 2:
            continue
        query_emb, query = line_list
        data = query_emb.strip('\n').split(' ')
        vector = [float(item) for item in data]
        vec_list.append(vector)
        query_list.append(query)
    return vec_list, query_list


def request_query_vec(query_file, topk):
    """
    query 原始数据，请求向量预测 + 检索
    """
    url = "http://10.37.119.235:49372" #query_vec
    with open(query_file, encoding="gb18030") as f:
        for line in f:
            query = line.strip('\n').split('\t')[0]
            data_dict = {}
            data_dict["query"] = [query]
            data_dict["title"] = ["-"]
            data_dict["para"] = ["-"]
            json_str = json.dumps(data_dict)#, encoding='utf8')
            start = time.time()
            result = requests.post(url, json_str)
            end = time.time()
            res_json = json.loads(result.text)
            query_vecs = res_json.get("q_rep",[[]])
            query_vec = query_vecs[0]
            query_list = [query]
            request_index(query_vecs, query_list, topk)
def request_mrc(qtp_file):
    url = "http://10.38.198.169:49003/gen_mrc/v0" #MRC
    with open(qtp_file) as f:
        for line in f:
            q, t, p = line.strip('\n').split('\t')[0:3]
            sample_dict = {}
            sample_dict["query_id"] = "0"
            sample_dict["query_text"] = q
            sample_dict["passage_text"] = p
            sample_dict["title"] = t
            data_dict = {}
            data_dict["samples"] = [sample_dict]
            data_dict["requestID"] = "0"
            json_str = json.dumps(data_dict)#, encoding='utf8')
            start = time.time()
            result = requests.post(url, json_str)
            end = time.time()
            res_json = json.loads(result.text)
            print(res_json)


def request_index(vec_list, query_list, topk):
    url = "http://10.21.218.123:8393" #80亿
    url = "http://10.179.72.28:8091" # kg_spo_2600
    for i in range(len(vec_list)):
        data_dict = {}
        data_dict['vectors'] = [[_ for _ in vec_list[i]]] #单条query向量
        data_dict['k'] = int(topk) # 返回topk相关para
        data_dict['query_id'] = i # query_id
        data_dict['query'] = query_list[i] # query文本内容
        data_dict['ef'] = 4096
        json_str = json.dumps(data_dict) #, encoding='utf8')
        start = time.time()
        result = requests.post(url, json_str)
        end = time.time()
        #print("cost time:" + "\t" + str(end - start))
        res_json = json.loads(result.text)
        print(res_json)
        query_id = res_json.get('query_id', "null")
        query = res_json.get('query', "null")
        paras = res_json.get('p', [])
        offsets = res_json.get('o', [])
        sim = res_json.get('s', [])
        #fid = res_json.get('f', [])
        if len(paras) != len(offsets):
            print("return error")
        for k in range(len(paras)):
            #print(str(query) + "\t" + str(query_id) + "\t" + "topk=" + str(k) + "\t" + paras[k] + "\t" + str(sim[k]) + "\t" + str(offsets[k]) + "\t" + str(fid[k]))
            print(str(query) + "\t" + str(query_id) + "\t" + "topk=" + str(k) + "\t" + paras[k] + "\t" + str(sim[k]) + "\t" + str(offsets[k]))
    

if __name__ == '__main__':
    query_file = sys.argv[1] #query文件
    request_mrc(query_file)

    query_file = sys.argv[1] #query文件
    topk = sys.argv[2]
    request_query_vec(query_file, topk) ##query -> 向量 -> 检索

    #vec_list, query_list = load_vector_query(query_file) ## query -> 向量
    #request_index(vec_list, query_list, topk) ##检索
