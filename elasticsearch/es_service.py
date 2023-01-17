"""
File Name: es_service.py
Author: yingwenjie
mail: yingwenjie@baidu.com
Created Time: Wed 09 Nov 2022 05:24:13 PM CST
"""
import sys
import json
import time
import tornado.web
import tornado.ioloop
import tornado.httpserver
import uuid
import copy

from es import ES
from log import Log
from consts import const
from settings import *
import os

class CreateHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.es = ES(settings[const.ES_DEFAULT_CONFIG])

    def get(self):
        pass

    def post(self):
        """
        arg format:
        {
            "projectId": "123", ##索引名称 baizhong_123
            "databaseType": "ElasticSearch", ##ann
            "followIndexFlag": "Ture" ##是否建正排
            "dataBody":{
                repoScope: keyword，##文档是否公开1
                Scope: keyword，##文档是否公开
                userRight: keyword，##文档所属用户组
                xxx: type, ## xxx为需要建倒排字段，type：text, keyword, date, int..
              }
        }
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        input_data = json.loads(self.request.body)
        projectId = input_data.get('projectId', 0)
        databaseType = input_data.get('databaseType', "ElasticSearch")
        followIndexFlag = input_data.get('followIndexFlag', True)
        dataBody = input_data.get('dataBody', {})
        print(str(dataBody))
        index_name = "baizhong_ann_" + str(projectId)
        res_json = self.es.create(index_name=index_name, mappings=dataBody)
        self.write("Create: " + str(res_json))

class IndexHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.es = ES(settings[const.ES_DEFAULT_CONFIG])

    def get(self):
        pass

    def post(self):
        """
        arg format:
        {
            "projectId": "123", ##索引名称 baizhong_123
            "dataBody":{
                repoScope: keyword，##文档是否公开1
                Scope: keyword，##文档是否公开
                userRight: keyword，##文档所属用户组
                xxx: type, ## xxx为需要建倒排字段，type：text, keyword, date, int..
                "shard": 32, #分片数
                "replical" 2 #副本数
              },
              "deleteFlag": "false" ## 是否删除索引
        }
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        input_data = json.loads(self.request.body)
        projectId = input_data.get('projectId', 0)
        dataBody = input_data.get('dataBody', {})
        deleteFlag = input_data.get('deleteFlag', "False")
        index_name = "baizhong_ann_" + str(projectId)
        if deleteFlag == "True":  #删除index
            res_json = self.es.delete_index(index_name=index_name)
            self.write("delete index " + str(res_json))
        if "shards" in dataBody or "replicas" in dataBody:  ##修改setting
            shards = dataBody.get("shards", 32)
            replicas = dataBody.get("replicas", 0)
            res_json = self.es.update_setting(index_name=index_name,
                                              replicas=replicas)
        else:  ##修改mapping
            res_json = self.es.update_mapping(index_name=index_name,
                                              field_info=dataBody)
class AddHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.es = ES(settings[const.ES_DEFAULT_CONFIG])
        self.web_api = WebApiClient()
        self.schemaObj = Schema()

    def get(self):
        pass

    def post(self):
        """
        {
            "projectId": "123", ##索引名称 baizhong_123
            "followIndexFlag": "Ture" ##是否建正排
            "dataBody": [
                {
                    "id": "10000112",
                    "title": "xxx", 
                    "content_se": "xxx",
                    "repoScope":["11"],
                    "Scope":["5"],
                    "imGroups": ["im_123",..],
                    "emailGroups": ["xxx@baidu.com"],
                    "userRight": ["uuu"],
                    "orgGroups": ["org"]
                 }
             ] ##支持实时小batch插入，比如100条内
        }
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        input_data = json.loads(self.request.body)
        projectId = input_data.get('projectId', 0)
        datas = input_data.get("dataBody", [])
        followIndexFlag = input_data.get('followIndexFlag', True)
        index_name = "baizhong_ann_" + str(projectId)
        if isinstance(datas, list) == False:
            print("add es, data type is error")

        ##cut
        schemaJson = self.web_api.get_schema_v2(projectId)
        self.schemaObj.from_json(schemaJson)

        #predict params
        data_loader_name = const.PREDICT_DATALOADER
        predict_table_name = const.PREDICT_TABLE
        max_workers = const.PREDICT_MAX_WORKS
        predict_args = {
            'data_loader_name': data_loader_name,
            'predict_table_name': predict_table_name,
            'max_workers': max_workers
        }
        log.error("predict_args: " + str(predict_args))
        try:
            for data in datas:
                _doc_data = json.dumps(copy.deepcopy(data), ensure_ascii=False)
                title, paras = self.schemaObj.json2paras(data)
                log.error("cut paras: " + str(paras))
                predict_input = []
                data["_id"] = str(data.get("_id", uuid.uuid1()))
                data['title'] = title
                for para in paras:
                    data['para'] = para
                    predict_input.append(data)
                log.error("predict_input: " + str(predict_input))
                result, out = predict_paras(predict_input, **predict_args)
                ##返回的out中包含 vactor 以及title，para，以及data原始字段
                if result != 0:
                    res_json[const.REST_CODE] = -3
                    res_json[const.REST_MSG] = out
                else:
                    for o in out:
                        if "title" not in o or "para" not in o or "vector" not in o:
                            log.error("predict out is error: " + str(out))
                            raise Exception("predict out is error, title para vector not in out")
                        o["_doc_id"] = o.pop("_id")
                        o["_title"] = o.pop("title")
                        o["_para"] = o.pop("para")
                        o["_vectors"] = o.pop("vector")
                        o["_doc_data"] = _doc_data
                    log.error("es data" + str(out))
                    res_json = self.es.add(index_name, out)
        except Exception as e:
            log.error("data-api add is fail: " + str(e))
        self.write("add: " + str(res_json))


class DeleteHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.es = ES(settings[const.ES_DEFAULT_CONFIG])

    def get(self):
        pass

    def post(self):
        """
        arg format:
        {
            "projectId": "123", ##索引名称 baizhong_123
            "followIndexFlag": "Ture" ##是否建正排
            "dataBody": ["1000003", "1000234"] ##文档doc_id
        }
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        input_data = json.loads(self.request.body)
        projectId = input_data.get('projectId', 0)
        ids = input_data.get('dataBody', [])
        followIndexFlag = input_data.get('followIndexFlag', True)
        index_name = "baizhong_ann_" + str(projectId)
        if isinstance(ids, list) == False:
            print("delete es, ids type is error")
            return

        res_json = self.es.delete(index_name, ids)
        self.write("delete: " + str(res_json))

class UpdateHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.es = ES(settings[const.ES_DEFAULT_CONFIG])
        self.web_api = WebApiClient()
        self.schemaObj = Schema()

    def get(self):
        pass

    def post(self):
        """
        {
            "projectId": "123", ##索引名称 baizhong_123
            "followIndexFlag": "Ture" ##是否建正排
            "dataBody": [
                {
                    "id": "10000112", #必须字段
                    "repoScope":["11"],
                    "Scope":["5"],
                    "imGroups": ["im_123",..],
                    "emailGroups": ["xxx@baidu.com"],
                    "userRight": ["uuu"],
                    "orgGroups": ["org"]
                 }
            ]
        }
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        input_data = json.loads(self.request.body)
        projectId = input_data.get('projectId', 0)
        datas = input_data.get("dataBody", [])
        followIndexFlag = input_data.get('followIndexFlag', True)
        index_name = "baizhong_ann_" + str(projectId)
        if isinstance(datas, list) == False:
            print("update es, data type is error")

        ##cut
        schemaJson = self.web_api.get_schema_v2(projectId)
        self.schemaObj.from_json(schemaJson)

        #predict params
        data_loader_name = const.PREDICT_DATALOADER
        predict_table_name = const.PREDICT_TABLE
        max_workers = const.PREDICT_MAX_WORKS
        predict_args = {
            'data_loader_name': data_loader_name,
            'predict_table_name': predict_table_name,
            'max_workers': max_workers
        }

        try:
            for data in datas:
                if "_id" not in data:
                    log.notice("update data, _id is null: " + str(data))
                    continue
                if "title" in data or "content_se" in data:
                    _doc_data = copy.deepcopy(data)
                    ids = [data["_id"]]
                    title, paras = self.schemaObj.json2paras(data)
                    log.error("cut paras: " + str(paras))
                    predict_input = []
                    data['title'] = title
                    for para in paras:
                        data['para'] = para
                        predict_input.append(data)
                    log.error("predict_input: " + str(predict_input))
                    result, out = predict_paras(predict_input, **predict_args)
                    ##返回的out中包含 vactor 以及title，para，以及data原始字段
                    if result != 0:
                        res_json[const.REST_CODE] = -3
                        res_json[const.REST_MSG] = out
                    else:
                        for o in out:
                            if "title" not in o or "para" not in o or "vector" not in o:
                                log.error("predict out is error: " + str(out))
                                raise Exception("predict out is error, title para vector not in out")
                            o["_doc_id"] = o.pop("_id")
                            o["_title"] = o.pop("title")
                            o["_para"] = o.pop("para")
                            o["_vectors"] = o.pop("vector")
                            o["_doc_data"] = _doc_data
                        log.error("es data" + str(out))
                        res_json = self.es.delete(index_name, ids)
                        res_json = self.es.add(index_name, out)
                else:
                    data["_doc_id"] = data.pop("_id")
                    res_json = self.es.update(index_name, [data])
        except Exception as e:
            log.error("data-api update is fail: " + str(e))
        self.write("update: " + str(res_json))

class SearchHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.es = ES(settings[const.ES_DEFAULT_CONFIG])

    def get(self):
        pass

    def post(self):
        """
        arg format:
        {
            "projectId": "123", ##索引名称 baizhong_123
            "queryVector": [-0.0355,0.035568..,0.04353], #query向量, 向量需要请求query预测服务生成
            "condition": [
                    {"repoScope": ["11"]}, 
                    {"userRight": ["uuu"]}
            ] ##检索过滤条件
            "topk": 100
        }
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        input_data = json.loads(self.request.body)
        projectId = input_data.get('projectId', 0)
        query_vector = input_data.get('queryVector', [])
        condition = input_data.get('condition', [])
        topk = input_data.get('topk', 100)
        index_name = "baizhong_ann_" + str(projectId)
        if isinstance(topk, int) == False:
            print("arg topk type is error")
            return
        if isinstance(query_vector, list) == False:
            print("arg query type is error")
            return
        if topk > 10000 or topk < 0:
            print("search es, topk is error:" + "\t" + topk)
        res_json = self.es.search(index_name, query_vector, condition, topk)
        self.write(json.dumps(res_json, ensure_ascii=False))

class GetHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request)
        self.es = ES(settings[const.ES_DEFAULT_CONFIG])

    def get(self):
        pass

    def post(self):
        """
        arg format:
        {
            "projectId": "123", ##索引名称 baizhong_123
            "followIndexFlag": "Ture" ##是否建正排
            "dataBody": ["1000003", "1000234"] ##文档doc_id
        }
        """
        res_json = {const.REST_CODE: 0, const.REST_MSG: "", "result": []}
        input_data = json.loads(self.request.body)
        projectId = input_data.get('projectId', 0)
        ids = input_data.get('dataBody', [])
        followIndexFlag = input_data.get('followIndexFlag', True)
        index_name = "baizhong_ann_" + str(projectId)
        res_json = self.es.get(index_name, ids)
        self.write("get: " + str(res_json))

        self.write("Update index " + str(res_json))

if __name__ == "__main__":

    es = ES(settings[const.ES_DEFAULT_CONFIG])

    port = int(settings[const.APP_CONFIG_ITEM][const.DATA_API][const.DATA_API_PORT])
    app = tornado.web.Application(handlers=[
        (r"/baizhong/build/v1/database/create", CreateHandler),
        (r"/baizhong/build/v1/database/update", IndexHandler),
        #(r"/baizhong/data-api/v2/doc-file/import", BuildHandler),
        (r"/baizhong/common-search/v2/search", SearchHandler),
        (r"/baizhong/data-api/v2/flush/add", AddHandler),
        (r"/baizhong/data-api/v2/flush/delete", DeleteHandler),
        (r"/baizhong/data-api/v2/flush/update", UpdateHandler),
        (r"/baizhong/data-api/v2/flush/get", GetHandler)
    ])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(port)
    print("Server started on port: %d" % port)
    tornado.ioloop.IOLoop.instance().start()

def b64str_2_vec(str, fmt='768f'):
    """
    change base64 string to vector
    """
    return struct.unpack(fmt, base64.b64decode(str))

def vector_norm(p_rep):
    p_rep = np.asarray(p_rep)
    p_vector = dot_product(p_rep ,p_rep.T)
    norm = np.sqrt(p_vector)
    return p_rep / norm.reshape(-1, 1)

def get_vector_num(inp_file):
    page_size = int(10000)
    print("inp_file = %s" % (inp_file))
    line_count = int(0)

    with open(inp_file, "r") as f:
        while 1:
            lines = f.readlines(page_size)
            if not lines:
                break
            for line in lines:
                line_count = line_count + 1

    print(f"vector count = %d" % line_count)
    return line_count

def dot_product(v1, v2):
    matrix = np.dot(v1, v2)
    return np.diagonal(matrix)

def get_train(train_file):

    #train_num = get_vector_num(train_file)
    #train_num = 30000000
    train_num = 1000000
    vectors = np.zeros((train_num, 768), dtype="float32")
    line_index = 0
    title_paras = []
    with open(train_file) as f:
        for line in f:
            u, t, p, tp, vec = line.strip('\n').split('\t')
            title_paras.append([t, p])
            try:
                vector_ub = b64str_2_vec(vec)
            except:
                print(line_index)
            vectors[line_index, :] = vector_norm([vector_ub]) ##需要归一化
            #vectors[line_index, :] = np.asarray(vector_ub) ##不需要归一化
            line_index += 1
            if line_index >= train_num: break
    return vectors, title_paras #[0:100000,:]

def get_test(test_file):

    train_num = get_vector_num(test_file)
    vectors = np.zeros((train_num, 768), dtype="float32")
    line_index = 0
    querys = []
    with open(test_file) as f:
        for line in f:
            vecs, query = line.strip('\n').split('\t')
            vec_list = vecs.split(' ')
            vectors[line_index, :] = np.asarray(vec_list)
            line_index += 1
            querys.append(query)
    return vectors, querys

def pre_data(X, title_paras):
    datas = []
    assert len(X) == len(title_paras)
    for i, vec in enumerate(X):
        data = {}
        start = i // 10000 * 10000
        end = (i // 10000 + 1) * 10000
        vals = list(range(start, end))
        id_val = "id_0" if i < 10000000 else "id_1"
        group_vals = list(range(start, start + 20))
        email_vals = list(range(start, start + 50))
        user_vals = list(range(start, start + 10))
        print(str(i) + "\t" + str(user_vals))
        group_filter = ["group_" + str(val) for val in group_vals]
        email_filter = ["email_" + str(val) for val in email_vals]
        user_filter = ["user_" + str(val) for val in user_vals]
        title = title_paras[i][0]
        para = title_paras[i][1]
        data["id"] = i + 1000001
        if i > 10000: break
        data["vector"] = vec
        data["title"] = title
        data["para"] = para
        data["id_filter"] = [id_val]
        data["group_filter"] = group_filter
        data["email_filter"] = email_filter
        data["user_filter"] = user_filter
        datas.append(data)
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
        condition1["id_filter"] = ["id_0"]
        condition2["group_filter"] = ["group_14000004", "group_14100004", "group_14200004"]
        condition3["email_filter"] = ["email_14300004", "email_14400004", "email_14500004", "email_14600004"]
        condition4["user_filter"] = ["user_14700004", "user_14800004", "user_14900004"]
        data["condition"].append(condition1)
        data["condition"].append(condition2)
        data["condition"].append(condition3)
        data["condition"].append(condition4)
        datas.append(data)
    return datas

