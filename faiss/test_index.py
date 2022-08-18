import sys
import time
import faiss
import math
import numpy as np
import random

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

def load_conf(conf_file):
    conf_list = []
    with open(conf_file) as f:
        for line in f:
            line_list = line.strip('\n').split('\t')
            if len(line_list) < 1:
                continue
            if "#" in line_list[0] or "name" == line_list[0]:
                continue
            conf_list.append(line_list)
    return conf_list

def get_passages(offsetss):
    passages_list = []
    fo = open('./data/stp_emb_0', "r")
    for offsets in offsetss:
        passages = []
        for offset in offsets:
            fo.seek(offset)
            line = fo.readline()
            line = line.strip()
            fields = line.split("\t")
            if len(fields) == 4:
                passage = fields[0] + "\t" + fields[1] + "\t" + fields[2]
                passages.append(passage)
        passages_list.append(passages)
    return passages_list

def test_engine(index, query_emb, topk):

    res_dist, res_p_id = index.search(query_emb.astype('float32'), int(topk))
    return res_dist, res_p_id

def write_res(res_dist, res_p_id, passages_list, res_file):
    fo = open(res_file, 'w')
    for i in range(len(res_p_id)):
        res_list = []
        for j in range(len(res_p_id[i])):
            p_id = res_p_id[i][j]
            passage_id = passages_list[i][j]
            score = res_dist[i][j]
            res_list.append([p_id, score])
            #print(str(p_id) + "\t" + str(score))
            fo.write(str(i) + "\t" + str(p_id) + "\t" + str(passage_id) + "\t'"+ str(score) + "\n")

def main():

    conf_file = sys.argv[1] #索引配置
    query_file = sys.argv[2] #检索query向量文件
    conf_list = load_conf(conf_file)
    query_vec, query_list = load_vector_query(query_file)
    topk = 50

    for conf in conf_list:
        index_name = conf[0]
        engine = faiss.read_index("./index/" + index_name)
        #faiss.ParameterSpace().set_index_parameter(engine, "nprobe", int(100))
        #config = faiss.GpuIndexIVFScalarQuantizerConfig()
        #config.device = 0   # simulate on a single GPU
        #res = faiss.StandardGpuResources()
        #engine = faiss.index_cpu_to_gpu(res, 0, engine)
        print("load done:" + str(index_name))
        for nt in [4097]:
        #for nt in [1]:
            #index_name, nprobe = conf[0:2]
            res_file = "./res/" + index_name + "_" + str(nt)

            #nt = "默认"
            #faiss.omp_set_num_threads(nt)
            #engine.nprobe = int(nprobe)
            #engine.efSearch = int(nt)
            #faiss.ParameterSpace().set_index_parameter(engine, "efSearch", int(nt))
            #faiss.ParameterSpace().set_index_parameter(engine, "nprobe", int(100))
            #faiss.GpuParameterSpace().set_index_parameter(engine, "nprobe", int(nt))
            #print(engine.nlist)
            #print(engine.nprobe)
            #print(engine.M)
            #print(engine.efConstruction)
            #print(engine.efSearch)

            begin_time = time.time()
            test_engine(engine,  np.asarray([query_vec[1]]), topk)
            end_time = time.time()
            a = float(end_time - begin_time)
            print(index_name + "@thread=" + str(nt) + "\t"  + "search time: " + str(end_time - begin_time))
            begin_time = time.time()
            test_engine(engine,  np.asarray([query_vec[2]]), topk)
            end_time = time.time()
            b = float(end_time - begin_time)
            print(index_name + "@thread=" + str(nt) + "\t"  + "search time: " + str(end_time - begin_time))
            begin_time = time.time()
            test_engine(engine,  np.asarray([query_vec[3]]), topk)
            end_time = time.time()
            c = float(end_time - begin_time)
            print(index_name + "@thread=" + str(nt) + "\t"  + "search time: " + str(end_time - begin_time))
            begin_time = time.time()
            print(index_name + "@thread=" + str(nt) + "\t" + "search time agv: " + str((a+b+c)/3))

            begin_time = time.time()
            res_dist, res_p_id = test_engine(engine, np.asarray(query_vec), topk)
            passages_list = get_passages(res_p_id)
            end_time = time.time()
            print(index_name + "@thread=" + str(nt) + "\t" + "search_all time: " + str(end_time - begin_time))
            write_res(res_dist, res_p_id, passages_list, res_file)

if __name__ == "__main__":
    main()

