"""
File Name: es.py
Author: yingwenjie
mail: yingwenjie@baidu.com
Created Time: Wed 26 Oct 2022 04:55:17 PM CST
"""
import sys
import json
import time
from time import sleep
import urllib3
urllib3.disable_warnings()

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

from errors import *
from log import Log
from settings import *
from consts import const

workpath = os.path.curdir
log_dir = os.path.join(workpath, settings[const.LOG_KEY][const.LOG_DIR])
log=Log.get_log(log_dir, "es-build.",
            settings[const.LOG_KEY][const.LOG_MIN_LEVEL],
            settings[const.LOG_KEY][const.LOG_RETENTION_DAYS],
            settings[const.LOG_KEY][const.LOG_IS_CONSOLE])

class ES(object):
    """
    this is ES class. and include api create index, build datas
    add, delete, update, get
    filter search
    """
    def __init__(self, es_config):
        self.ip = es_config["ip"]
        self.port = es_config["port"]
        self.user = es_config["user"]
        self.passwd = es_config["passwd"]
        self.number_of_shards = es_config["number_of_shards"]
        self.number_of_replicas = es_config["number_of_replicas"]
        self.metric = es_config["metric"]
        self.dimension = es_config["dim"]
        self.index_arg_m = es_config["index_arg_m"]
        self.index_arg_ef = es_config["index_arg_ef"]
        self.num_candidates = es_config["num_candidates"]
        uri = "https://" + str(self.ip) + ":" + str(self.port)
        #self.es = Elasticsearch([uri], http_auth=(self.user, self.passwd), verify_certs=False, timeout=1000)
        self.es = Elasticsearch(["http://127.0.0.1:9200"], timeout=10000)

    def create(self, index_name, settings={}, mappings={}):
        """
        This is create index api.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        body = dict(settings=dict(number_of_shards=self.number_of_shards, \
                number_of_replicas=self.number_of_replicas), \
                mappings = dict(dynamic=False, properties=dict(
                    _doc_id=dict(type="keyword", index=False, store=True),
                    _vectors=dict(type="dense_vector", dims=self.dimension, index=True, \
                            similarity= self.metric, index_options=dict(type="hnsw", \
                            m=self.index_arg_m, ef_construction=self.index_arg_ef)),
                    _title=dict(type="keyword", index=False, store=True),
                    _para=dict(type="keyword", index=False, store=True),
                    _doc_data=dict(type="keyword", index=False, store=True)
                )
            )
        )
        if isinstance(settings, dict) == False or isinstance(mappings, dict) == False:
            log.error("create es, setting or mapping type is error." + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if "mappings" in mappings and "properties" in mappings["mappings"]:
            mappings = mappings["mappings"]["properties"]
        for key, value in mappings.items():
            if isinstance(key, str) == False:
                log.error("create es, key is errro:" + "\t" + str(key) + ":" + str(value) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -2
            body["mappings"]["properties"].setdefault(key, dict(type=value))

        for key, value in settings.items():
            if isinstance(key, str) == False:
                log.error("create es, key is errro:" + "\t" + str(key) + ":" + str(value) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -2
            body["settings"][key] = value
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "create es, setting or mapping is error."
        else:
            try:
                res = self.es.indices.create(index=index_name, body=body)
                res_json["result"] = str(res)
            except Exception as e:
                res_json[const.REST_CODE] = -1
                log.error("create es is fail. except: " + str(e) + "\t" + str(index_name) + "\t" + str(settings) + "\t" + str(mappings))
                res_json[const.REST_MSG] = "create es is fail: " + str(index_name)
        return res_json

    def update_mapping(self, index_name, field_info={}):
        """
        This is update mapping api.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if isinstance(field_info, dict) == False:
            log.error("update index, field_info type is error:" + "\t" + str(field_info) + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if "mappings" in field_info and "properties" in field_info["mappings"]:
            field_info = field_info["mappings"]["properties"]
        for key, value in field_info.items():
            if isinstance(key, str) == False:
                log.error("update index, key is errro:" + "\t" + str(key) + ":" + str(value) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -2

        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "update index, field_info is fail:" + str(field_info)
        else:
            try:
                res = self.es.indices.put_mapping(index=index_name, properties=field_info)
                res_json["result"] = str(res)
            except Exception as e:
                res_json[const.REST_CODE] = -1
                log.error("update index is fail. except: " + str(e) + "\t" + str(index_name) + "\t" + str(field_info))
                res_json[const.REST_MSG] = "update index is fail: " + str(index_name)
        return res_json

    def update_setting(self, index_name, replicas=0):
        """
        This is update setting api.
        Doing...
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if isinstance(replicas, int) == False:
            log.error("update setting, value is errro:" + "\t" + str(replicas))
            res_json[const.REST_CODE] = -2
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "update setting, replicas value is error."
        else:
            settings = dict(settings=dict(number_of_replicas=replicas))
            try:
                res = self.es.indices.put_settings(index=index_name, settings=settings)
                res_json["result"] = str(res)
            except Exception as e:
                res_json[const.REST_CODE] = -1
                log.error("update setting is fail. except: " +  str(e) + "\t" + str(index_name) + "\t" + str(replicas))
                res_json[const.REST_MSG] = "update setting is fail: " + str(index_name)
        return res_json

    def delete_index(self, index_name):
        """
        This is delete index api, must be careful.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        try:
            res = self.es.indices.delete(index=index_name, allow_no_indices=True)
            res_json["result"] = str(res)
        except Exception as e:
            res_json[const.REST_CODE] = -1
            log.error("delete index is fail. except: " + str(e) + "\t" + str(index_name))
            res_json[const.REST_MSG] = "delete index is fail: " + str(index_name)

        return res_json

    def build(self, index_name, datas):
        """
        This is build datas api.
        """
        def gen():
            """ data generator """
            for data in datas:
                content = {"_op_type": "index", "_index": index_name}
                for key, val in data.items():
                    content.setdefault(key, val)
                yield content

        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if isinstance(datas, list) == False:
            log.error("build es, datas is error" + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "build es, datas is not list." + str(index_name)
        else:
            try:
                (_, errors) = bulk(self.es, gen(), chunk_size=10, max_retries=9)
                assert len(errors) == 0, errors
            except Exception as e:
                res_json[const.REST_CODE] = -1
                log.error("build es is fail. except: " + str(e) + "\t" + str(index_name))
                res_json[const.REST_MSG] = "build es is fail: " + str(index_name)
                return res_json

        self.es.indices.refresh(index=index_name)
        return res_json

    def add(self, index_name, datas):
        """
        This is real time add api.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if isinstance(datas, list) == False:
            log.error("add es, datas is error" + "\t" + str(datas) + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "add es, datas is not list." + str(index_name)
            return res_json
        for data in datas:
            content = {"_op_type": "index", "index": index_name}
            for key, val in data.items():
                content.setdefault(key, val)
            try:
                self.es.index(index=index_name, body=content)
                self.es.indices.refresh(index=index_name)
            except Exception as e:
                log.notice("add is fail" + "\t" + str(data) + "\t" + str(index_name))
                log.error("add is fail. except: " + str(e) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -1
                res_json[const.REST_MSG] = "add es, has fail:" + str(index_name)

        return res_json
    
    def delete(self, index_name, ids):
        """
        This is real time delete api.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if isinstance(ids, list) == False:
            log.error("delete es, ids is error" + "\t" + str(ids) + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "delete es, ids is not list: " + str(ids)
        else:
            content = {"query":{"terms":{"_doc_id":ids}}}
            try:
                res = self.es.delete_by_query(index=index_name, body=content)
                res_json["result"] = str(res)
            except Exception as e:
                log.notice("delete ids is fail" + "\t" + str(ids) + "\t" + str(index_name))
                log.error("delet ids is fail. except: " + str(e) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -1
                res_json[const.REST_MSG] = "delete es, is fail: " + str(index_name)
        return res_json

    def update(self, index_name, id_infos):
        """
        This is real time update api.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if isinstance(id_infos, list) == False:
            log.error("update es, id_infos is error" + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "update es, id_infos is not list:" + str(id_infos)
            return res_json
        for id_info in id_infos:
            i = id_info.get("_doc_id", "-1")
            if i == "-1":
                log.error("update es, datas is error:" + "\t" + str(id_info) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -2
                res_json[const.REST_MSG] = "update es, id_info is error: " + str(id_info)
                return res_json
            one_update = []
            for key, value in id_info.items():
                if key == "_doc_id": continue
                one_update.append("ctx._source." + key + "=" + str(value))
            content = {"query":{"term":{"_doc_id":i}}, "script":{"source": ";".join(one_update), \
                    "lang":"painless"}}
            try:
                res = self.es.update_by_query(index=index_name, body=content, wait_for_completion=False)
            except Exception as e:
                log.notice("update is fail" + "\t" + str(id_infos) + "\t" + str(index_name))
                log.error("update is fail. except: " + str(e) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -1
                res_json[const.REST_MSG] = "update es, is fail: " + str(index_name)
                return res_json
        return res_json

    def get(self, index_name, ids):
        """
        This is get data with ids.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if isinstance(ids, list) == False:
            log.error("get es, ids is error" + "\t" + str(ids) + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "get es, ids is not list:" + str(ids)
        else:
            content = {"query":{"terms":{"_doc_id":ids}}}
            try:
                res = self.es.search(index=index_name, body=content)
            
                res_json["result"] = [str(h) for h in res['hits']['hits']]
            except Exception as e:
                log.error("get is fail. except: " + str(e) + "\t" + str(index_name))
                res_json[const.REST_CODE] = -1
                res_json[const.REST_MSG] = "get es, is fail:" + str(index_name)
        return res_json

    def search(self, index_name, query_vector, condition, topk):
        """
        This is search api.
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        if len(query_vector) != self.dimension:
            log.error("query_vector dim is error and dim=" + "\t" + str(len(query_vector)) + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if len(condition) == 0:
            log.error("Filter condition is except" + "\t" + str(condition) + "\t" + str(index_name))
            res_json[const.REST_CODE] = -2
        if res_json[const.REST_CODE] != 0:
            res_json[const.REST_MSG] = "search es, arg is error: " + str(index_name)
            return res_json
        content = dict(knn=dict(field="_vectors", query_vector=query_vector, \
                        k=topk, num_candidates=self.num_candidates, \
                    )
                )
        content["knn"]["filter"] = {}
        content["knn"]["filter"]["bool"] = {}
        content["knn"]["filter"]["bool"]["should"] = []
        for cond in condition:
            content["knn"]["filter"]["bool"]["should"].append({"terms": cond})
        try:
            res = self.es.search(index=index_name, body=content, size=topk, _source=False, \
                    stored_fields=['_doc_id', '_title', '_para', '_doc_data'])
            res_json["result"] = res['hits']['hits']
        except Exception as e:
            log.notice("search is fail: " + "\t" + str(index_name))
            log.error("search is fail. except: " + str(e) + "\t" + str(index_name))
            res_json[const.REST_CODE] = -1
            res_json[const.REST_MSG] = "search es, is fail: " + "\t" + str(index_name)
        return res_json
