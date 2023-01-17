#########################################################################
# File Name: es.py
# Author: yingwenjie
# mail: yingwenjie@baidu.com
# Created Time: Wed 26 Oct 2022 04:55:17 PM CST
#########################################################################
import sys
import time
import json
import numpy as np
import argparse
import threading
import random

from time import sleep
from urllib.error import URLError
from urllib.request import Request, urlopen
import urllib3
urllib3.disable_warnings()

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch.helpers import parallel_bulk

from es_config import es_config
from get_data import get_train, get_test

def es_wait(uri):
    print("Waiting for elasticsearch health endpoint...")
    req = Request(uri + "/_cluster/health?wait_for_status=yellow&timeout=1s")
    for i in range(30):
        try:
            res = urlopen(req)
            if res.getcode() == 200:
                print("Elasticsearch is ready")
                return
        except URLError:
            pass
        sleep(1)
    raise RuntimeError("Failed to connect to local elasticsearch")

class ES():
    """
    KNN using the Elasticsearch dense_vector datatype and script score functions.
    - Dense vector field type: https://www.elastic.co/guide/en/elasticsearch/reference/master/dense-vector.html
    - Dense vector queries: https://www.elastic.co/guide/en/elasticsearch/reference/master/query-dsl-script-score-query.html
    """

    def __init__(self, es_config):
        self.ip = es_config["ip"]
        self.port = es_config["port"]
        self.index_name = es_config["index_name"]
        self.number_of_shards = es_config["number_of_shards"]
        self.number_of_replicas = es_config["number_of_replicas"]
        self.metric = es_config["metric"]
        self.dimension = es_config["dim"]
        self.index_arg_m = es_config["index_arg_m"]
        self.index_arg_ef = es_config["index_arg_ef"]
        self.num_candidates = es_config["num_candidates"]
        uri = "https://" + str(self.ip) + ":" + str(self.port)
        self.es = Elasticsearch([uri], http_auth=("elastic", "1234"), verify_certs=False, timeout=1000000)
        self.body = dict(settings=dict(number_of_shards=self.number_of_shards, number_of_replicas=self.number_of_replicas), \
                mappings = dict(properties=dict(
                    _doc_id=dict(type="keyword", store=True),
                    _vectors=dict(type="dense_vector", dims=self.dimension, index=True, similarity= self.metric, \
                            index_options=dict(type="hnsw", m=self.index_arg_m, ef_construction=self.index_arg_ef)),
                    _title=dict(type="text", store=True),
                    _para=dict(type="text", store=True),
                    _doc_data=dict(type="text", store=True)
                )
            )
        )
        #es_wait(uri)
    
    def create(self, index_name="", dim=768, field_info={}):
        if index_name != "":
            self.index_name = index_name
        for key, value in field_info.items():
            self.body["mappings"]["properties"].setdefault(key, dict(type=value))
        
        print(self.index_name)
        print(field_info)
        print(self.body)
        if self.es.cat.count == 0:
            self.es.indices.delete(index=self.index_name, allow_no_indices=True)
            self.es.indices.create(index=self.index_name, body=self.body)
        else:
            self.es.indices.delete(index=self.index_name, allow_no_indices=True)
            self.es.indices.create(index=self.index_name, body=self.body)

    def update_mapping(self, index_name="", field_info={}):
        if index_name != "":
            self.index_name = index_name
        res = self.es.indices.put_mapping(index=index_name, properties=field_info)
         
    def update_setting(self, index_name, replicas=0):
        settings = dict(settings=dict(number_of_replicas=replicas))
        res = self.es.indices.put_settings(index=index_name, settings=settings)
    def delete_index(self, index_name):
        res = self.es.indices.delete(index=index_name, allow_no_indices=True)

    def build(self, datas):
        def gen():
            for data in datas:
                content = {"_op_type": "index", "_index": self.index_name}
                for key, val in data.items():
                    content.setdefault(key, val)
                yield content

        (_, errors) = bulk(self.es, gen(), chunk_size=10000, max_retries=9)
        assert len(errors) == 0, errors

        self.es.indices.refresh(index=self.index_name)
        self.es.indices.forcemerge(index=self.index_name, max_num_segments=1)

    def add(self, datas):
        ##某一条插入失败处理
        for data in datas:
            content = {"_op_type": "index", "index": self.index_name}
            for key, val in data.items():
                content.setdefault(key, val)
            try:
                self.es.index(index=self.index_name, body=content)
            except:
                print("add is fail" + "\t" + str(data))
        self.es.indices.refresh(index=self.index_name)
    
    def delete(self, ids):
        body = {"query":{"terms":{"_doc_id":ids}}}
        res = self.es.delete_by_query(index=self.index_name, body=body)
        return res

    def update(self, id_infos):
        for id_info in id_infos:
            i = id_info.get("_doc_id", -1)
            field_info = id_info.get("update_info", {})
            one_update = []
            for key, value in field_info.items():
                one_update.append("ctx._source." + key + "=" + str(value))
            content = {"query":{"term":{"_doc_id":i}}, "script":{"source": ";".join(one_update), \
                    "lang":"painless"}}
            res = self.es.update_by_query(index=self.index_name, body=content, wait_for_completion=False)
        return res

    def get(self, ids):
        body = {"query":{"terms":{"_doc_id":ids}}}
        res = self.es.search(index=self.index_name, body=body)
        return res 

    def search(self, query_info, topk):
        query_vector = query_info.get("query_vector", []) 
        condition = query_info.get("condition", [])
        if len(query_vector) != self.dimension:
            print("query_vector dim is error" + "\t" + str(len(query_vector)))
            return 
        if len(condition) == 0:
            print("Filter condition is except")
            return
        body = {
                "knn": {
                    "field": "_vectors",
                    "query_vector": query_vector,
                    "k": topk,
                    "num_candidates": self.num_candidates,
                    "filter": {
                        "bool": {
                            "should":[
                            ]
                        }
                    }
                }
               }
        for cond in condition:
            body["knn"]["filter"]["bool"]["should"].append({"terms": cond})
        #print(body)
        #res = self.es.search(index=self.index_name, body=body, size=topk, _source=False, docvalue_fields=['id'],
        #                     stored_fields="_none_", filter_path=["hits.hits.fields.id"])
        #return [int(h['fields']['id'][0]) - 1 for h in res['hits']['hits']]

        res = self.es.search(index=self.index_name, body=body, size=topk, _source=False, stored_fields=['_doc_id','_title','_para','_doc_data'])
        #res = self.es.search(index=self.index_name, body=body, size=topk, _source=True)
        return [str(h) for h in res['hits']['hits']]

def pre_data(X, title_paras):
    datas = []
    assert len(X) == len(title_paras)
    for i, vec in enumerate(X):
        data = {}
        start = i // 10000 * 10000
        end = (i // 10000 + 1) * 10000
        vals = list(range(start, end))
        repoScope = [11] if i < 10000000 else [13, 14]
        Scope = [5, 6] if i < 10000000 else [7, 8]
        im_vals = list(range(start, start + 20))
        email_vals = list(range(start, start + 50))
        user_vals = list(range(start, start + 10))
        org_vals = list(range(start, start + 5))
        imGroups = ["im_" + str(val) for val in im_vals]
        emailGroups = ["email_" + str(val) for val in email_vals]
        userRight = ["user_" + str(val) for val in user_vals]
        orgGroups = ["org_" + str(val) for val in org_vals]
        title = title_paras[i][0]
        para = title_paras[i][1]
        data["_doc_id"] = i 
        data["_vectors"] = vec
        data["_title"] = title
        data["_para"] = para
        data["_doc_data"] = para
        data["repoScope"] = repoScope
        data["Scope"] = Scope
        data["imGroups"] = imGroups
        data["emailGroups"] = emailGroups
        data["userRight"] = userRight
        data["orgGroups"] = orgGroups
        datas.append(data)
        #rr = []
        #for key, value in data.items():
        #    rr.append(key + ":" + str(value))
        #print("\t".join([str(i) for i in rr]))
    return datas
    

def pre_search(X):
    datas = []
    for x in X:
        data = {}
        data["query_vector"] = x
        data["condition"] = []
        condition1 = {}
        condition2 = {}
        condition3 = {}
        condition4 = {}
        condition5 = {}
        condition6 = {}
        condition1["repoScope"] = ["11"]
        condition2["Scope"] = ["5"]
        condition3["imGroups"] = ["im_14000004", "im_14100004", "im_14200004"]
        condition4["emailGroups"] = ["email_14300004", "email_14400004", "email_14500004", "email_14600004"]
        condition5["userRight"] = ["user_14700004", "user_14800004", "user_14900004"]
        condition6["orgGroups"] = ["org_14700004", "org_14800004", "org_14900004"]
        data["condition"].append(condition1)
        data["condition"].append(condition2)
        data["condition"].append(condition3)
        data["condition"].append(condition4)
        data["condition"].append(condition5)
        data["condition"].append(condition6)
        datas.append(data)
    return datas

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            "--para_file",
            default="../data/base_vec_data_1M",
            help="build data")
    parser.add_argument(
            "--query_file",
            default="../data/query_1W.emb",
            help="search data")

    args = parser.parse_args()
    print(es_config)
    es = ES(es_config)

    #create
    field_info = {"repoScope": "keyword", "Scope": "keyword", "userRight": "keyword", "imGroups": "keyword", "emailGroups": "keyword", "orgGroups": "keyword"}
    es.create(field_info=field_info)

    # get_data
    train, title_paras = get_train(args.para_file)
    datas = pre_data(train, title_paras)
    print(len(datas))

    # build
    begin_time = time.time()
    es.build(datas)
    end_time = time.time()
    print("build time:" + "\t" + str(end_time - begin_time))

    # add
    #begin_time = time.time()
    #es.add(datas)
    #end_time = time.time()
    #print("add time:" + "\t" + str(end_time - begin_time))

    # delete
    #ids = []
    #for i in range(10000):
    #    ids.append(i+1000000)
    #begin_time = time.time()
    #es.delete(ids)
    #end_time = time.time()
    #print("delete time:" + "\t" + str(end_time - begin_time))

    # update
    #id_infos = []
    #field_info = {}
    #for i in range(10):
    #    group_filter = ["group_" + str(val) for val in range(1000000, i+1000000 + 1)]
    #    email_filter = ["email_" + str(val) for val in range(1000000, i+1000000 + 2)]
    #    user_filter = ["user_" + str(val) for val in range(1000000, i+1000000 + 3)]
    #    field_info = {"group_filter": group_filter, "email_filter": email_filter, "user_filter": user_filter}
    #    id_infos.append({"id": i+1000000, "field_info": field_info})
    #begin_time = time.time()
    #es.update(id_infos)
    #end_time = time.time()
    #print("update time:" + "\t" + str(end_time - begin_time))
    
    # get
    #ids = []
    #for i in range(10):
    #    ids.append(i+1000000)
    #begin_time = time.time()
    #res = es.get(ids)
    #end_time = time.time()
    #print("get time:" + "\t" + str(end_time - begin_time))
    #print(res)

    #exit()
    # search
    test, querys = get_test(args.query_file) 
    datas = pre_search(test)
    time_sum = 0
    for i, q in enumerate(datas):
        #if i >= 100: break
        #sleep(random.randint(10,1000)/1000)
        begin_time = time.time()
        res = es.search(q, 100)
        end_time = time.time()
        print(end_time - begin_time)
        time_sum += (end_time - begin_time)
        for r in res:
            print(str(i) + "\t" + str(querys[i]) + "\t" + str(r))
    print(time_sum)

