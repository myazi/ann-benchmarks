# !/usr/bin/env python3
# Copyright (C) 2019-2020 Zilliz. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License
# is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
# or implied. See the License for the specific language governing permissions and limitations under the License.

import sys
import time
import random
from typing import NoReturn
import numpy as np
import os
import struct
import traceback
import faiss
import math
import base64
import configparser

def vec_2_b64str(self, vec, fmt='768f'):
    """
    @summary: change vector to base64 string to save space
    @param: vec 向量
    @fmt: struct格式
    """
    b_vec = base64.b64encode(struct.pack(fmt, *vec))
    s_vec = str(b_vec, encoding='utf-8')
    return s_vec

def b64str_2_vec(str, fmt='768f'):
    """
    change base64 string to vector
    """
    return struct.unpack(fmt, base64.b64decode(str))

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
                #fields = line.split("\t")
                #if(len(fields) < 4):
                #    continue
                line_count = line_count + 1
    
    print(f"vector count = %d" % line_count)
    return line_count

def dot_product(v1, v2):
    matrix = np.dot(v1, v2)
    return np.diagonal(matrix)

def vector_norm(p_rep):
    p_rep = np.asarray(p_rep)
    p_vector = dot_product(p_rep ,p_rep.T)
    norm = np.sqrt(p_vector)
    return p_rep / norm.reshape(-1, 1)

def index_type_none(dim=768):
    faiss_index = faiss.IndexFlatIP(dim)
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index

def index_type_ivf(nlist, nprobe, dim=768):
    quantizer = faiss.IndexFlatIP(dim)
    faiss_index = faiss.IndexIVFFlat(quantizer, dim, nlist, faiss.METRIC_INNER_PRODUCT)
    faiss_index.cp.min_points_per_centroid = 100
    faiss_index.nprobe = nprobe
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index
def index_type_ivf_gpu(nlist, nprobe, dim=768):
    config = faiss.GpuIndexIVFFlatConfig()
    config.device = 0   # simulate on a single GPU
    res = faiss.StandardGpuResources()
    faiss_index = faiss.GpuIndexIVFFlat(res, dim, nlist, faiss.METRIC_INNER_PRODUCT, config)
    faiss_index.nprobe = nprobe
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index
def index_type_ivf_sq8_gpu(nlist, nprobe, dim=768):
    config = faiss.GpuIndexIVFScalarQuantizerConfig()
    config.device = 0   # simulate on a single GPU
    res = faiss.StandardGpuResources()
    quantizer = faiss.IndexFlatIP(dim)
    qtype = getattr(faiss.ScalarQuantizer, "QT_8bit")
    faiss_index = faiss.GpuIndexIVFScalarQuantizer(res, dim, nlist, qtype, faiss.METRIC_INNER_PRODUCT, True, config)
    #faiss_index.nprobe = nprobe
    faiss_index.setNumProbes(nprobe)
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index

def index_type_ivf_sq8(nlist, nprobe, dim=768):
    quantizer = faiss.IndexFlatIP(dim)
    qtype = getattr(faiss.ScalarQuantizer, "QT_8bit")
    faiss_index = faiss.IndexIVFScalarQuantizer(quantizer, dim, nlist, qtype, faiss.METRIC_INNER_PRODUCT)
    faiss_index.nprobe = nprobe
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index

def index_type_hnsw(m, ef, dim=768):
    faiss_index = faiss.IndexHNSWFlat(dim, m, faiss.METRIC_INNER_PRODUCT)
    faiss_index = faiss.IndexIDMap(faiss_index)
    faiss_index.efConstruction = ef
    return faiss_index

def index_type_hnsw_sq8(m, ef, dim=768):
    qtype = getattr(faiss.ScalarQuantizer, "QT_8bit")
    faiss_index = faiss.IndexHNSWSQ(dim, qtype, m, faiss.METRIC_INNER_PRODUCT)
    #faiss_index = faiss.IndexIDMap(faiss_index)
    faiss_index.efConstruction = ef
    return faiss_index

def index_type_ivf_hnsw_sq8(nlist, nprobe, m, ef, dim=768):
    faiss_index = faiss.index_factory(dim, "IVF" + str(nlist) +"_HNSW" + str(m) + ",SQ8", faiss.METRIC_INNER_PRODUCT)
    faiss_index = faiss.IndexIDMap(faiss_index)
    faiss_index.nprobe = nprobe
    faiss_index.efConstruction = ef
    return faiss_index

def index_type_pq(m, nbits, dim=768):
    faiss_index = faiss.IndexPQ(dim, m, nbits)
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index

def index_type_lsh(nbits, dim=768):
    faiss_index = faiss.IndexLSH(dim, nbits)
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index

def index_type_sq8(qname="QT_8bit", dim=768):
    qtype = getattr(faiss.ScalarQuantizer, qname)
    faiss_index = faiss.IndexScalarQuantizer(dim, qtype, faiss.METRIC_INNER_PRODUCT)
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index

def index_type_pca(pca, dim=768):
    pca_str = "PCA" + str(pca) + ",Flat"
    faiss_index = faiss.index_factory(dim, pca_str, faiss.METRIC_INNER_PRODUCT)
    faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index
def index_type_hnsw_pq(m, ef, pq_dim, dim=768):
    hnsw_pq_str = "HNSW" + str(m) + ",PQ" + str(pq_dim)
    faiss_index = faiss.index_factory(dim, hnsw_pq_str, faiss.METRIC_INNER_PRODUCT)
    faiss_index.hnsw.efConstruction = ef
    faiss_index.metric_type = faiss.METRIC_INNER_PRODUCT
    assert faiss_index.metric_type == faiss.METRIC_INNER_PRODUCT
    print(faiss_index.metric_type)
    #faiss_index = faiss.IndexIDMap(faiss_index)
    return faiss_index

def load_data(inp_file, file_id):
    dim = 768
    # 文件名格式：part-00000.bin
    print("inp_file = %s, file_id = %d" % (inp_file, file_id))

    #  insert data
    start_time = time.time()
    page_size = int(100000)
    line_count = int(0)
    insert_count = int(0)
    line_index = int(1)
    index_line = int(0)
    offset = 0

    #初始化faiss
    cf = configparser.ConfigParser()
    cf.read('./conf/conf.ini')
    index_type = cf.get('index_type', 'type')
    print(index_type)
    if 'None' == index_type:
        index_type = "baseline"
        faiss_index = index_type_none(dim) 
    elif 'IVF_SQ8' == index_type:
        nlist = int(cf.get('index_param', 'nlist'))
        nprobe = int(cf.get('index_param', 'nprobe'))
        print(nlist)
        print(nprobe)
        faiss_index = index_type_ivf_sq8(nlist, nprobe, dim)
    elif 'IVF' == index_type:
        nlist = int(cf.get('index_param', 'nlist'))
        nprobe = int(cf.get('index_param', 'nprobe'))
        print(nlist)
        print(nprobe)
        faiss_index = index_type_ivf(nlist, nprobe, dim)
    elif 'HNSW' == index_type:
        M = int(cf.get('index_param', 'M'))
        ef = int(cf.get('index_param', 'ef'))
        print(M)
        print(ef)
        faiss_index = index_type_hnsw(M, ef, dim)
    elif 'HNSW_SQ8' == index_type:
        M = int(cf.get('index_param', 'M'))
        ef = int(cf.get('index_param', 'ef'))
        print(M)
        print(ef)
        faiss_index = index_type_hnsw_sq8(M, ef, dim)
    elif 'IVF_HNSW_SQ8' == index_type:
        nlist = int(cf.get('index_param', 'nlist'))
        nprobe = int(cf.get('index_param', 'nprobe'))
        M = int(cf.get('index_param', 'M'))
        ef = int(cf.get('index_param', 'ef'))
        print(nlist)
        print(nprobe)
        print(M)
        print(ef)
        faiss_index = index_type_ivf_hnsw_sq8(nlist, nprobe, M, ef, dim)
    elif 'PQ' == index_type:
        m = int(cf.get('index_param', 'pq_m'))
        nbits = int(cf.get('index_param', 'pq_bits'))
        print(m)
        print(nbits)
        faiss_index = index_type_pq(m, nbits, dim)
    elif 'LSH' == index_type:
        nbits = int(cf.get('index_param','lsh_bits'))
        print(nbits)
        faiss_index = index_type_lsh(nbits, dim)
    elif 'SQ8' == index_type:
        faiss_index = index_type_sq8()
    elif 'PCA' == index_type:
        pca = int(cf.get('index_param', 'pca'))
        print(pca)
        faiss_index = index_type_pca(pca, dim)
    elif 'IVF_SQ8_GPU' == index_type:
        nlist = int(cf.get('index_param', 'nlist'))
        nprobe = int(cf.get('index_param', 'nprobe'))
        print(nlist)
        print(nprobe)
        faiss_index = index_type_ivf_sq8_gpu(nlist, nprobe, dim)
    elif 'IVF_GPU' == index_type:
        nlist = int(cf.get('index_param', 'nlist'))
        nprobe = int(cf.get('index_param', 'nprobe'))
        print(nlist)
        print(nprobe)
        faiss_index = index_type_ivf_gpu(nlist, nprobe, dim)
    elif 'HNSW_PQ' == index_type:
        M = int(cf.get('index_param', 'M'))
        ef = int(cf.get('index_param', 'ef'))
        pq_dim = int(cf.get('index_param', 'pq_dim'))
        faiss_index = index_type_hnsw_pq(M, ef, pq_dim, dim)
    else:
        print('index type error.')
        return

    # start faiss
    is_trained = faiss_index.is_trained
    print(is_trained)
    vector_num = get_vector_num(inp_file)
    #vector_num = 1000000
    train_num = math.ceil(vector_num/1)
    print(train_num)
    if is_trained == False:
        vectors = np.zeros((train_num, dim), dtype="float32")
        offsets = np.zeros((train_num), dtype="int64")
    else: 
        vectors = np.zeros((page_size, dim), dtype="float32")
        offsets = np.zeros((page_size), dtype="int64")

    with open(inp_file, "r") as f:
        file_size = os.path.getsize(inp_file)
        while 1:
            line = f.readline()
            index_line += 1
            #if index_line > 1000000: break
            if not line:
                break
            line_len = len(line.encode())
            fields = line.split("\t")
            if(len(fields) < 4):
                print("fields error: %d" % line_index)
                offset = offset + line_len
                line_index += 1
                continue
            try:
                vector_ub = b64str_2_vec(fields[3])
                #vec_norm = vector_norm([np.asarray(vector_ub)])
                vec_norm = [np.asarray(vector_ub)]
                vector = vec_norm[0]
            except:
                print("base64 error: %d" % line_index)
                offset = offset + line_len
                line_index += 1
                continue
            #vectors[insert_count,:] = np.asarray(vector)
            vectors[insert_count,:] = vector
            offsets[insert_count] = offset # 使用字符位置作为index
            offsets[insert_count] = index_line #使用行号作为index
            offset = offset + line_len
            line_count += 1
            line_index += 1
            insert_count += 1
            if line_count == train_num and is_trained == False:
                print("start train")
                is_done = False
                is_trained = True
                while not is_done:
                    print("start train")
                    try:
                        print(sys.getsizeof(vectors))
                        print(sys.getsizeof(offsets))
                        faiss_index.train(vectors)
                        print("index is trained")
                        #faiss_index.add_with_ids(vectors, offsets)
                        faiss_index.add(vectors)
                        print("index add first")
                        is_done = True
                    except:
                        is_done = False
                        # 获取异常信息
                        print(traceback.format_exc())
                        print('insert failed, retrying...')
                vectors = np.zeros((page_size, dim), dtype="float32")
                offsets = np.zeros((page_size), dtype="int64")
                insert_count = int(0)
                print(f"insert count = %d" % line_count)
                
            if insert_count > 0 and line_count % page_size == 0 and is_trained == True:
                is_done = False
                while not is_done:
                    try:
                        #faiss_index.add_with_ids(vectors, offsets)
                        faiss_index.add(vectors)
                        is_done = True
                    except:
                        is_done = False
                        # 获取异常信息
                        print(traceback.format_exc())
                        print('insert failed, retrying...')
                vectors = np.zeros((page_size, dim), dtype="float32")
                offsets = np.zeros((page_size), dtype="int64")
                insert_count = int(0)
                print(f"insert count = %d" % line_count)

        if insert_count > 0:
            is_done = False
            while not is_done:
                try:
                    #faiss_index.add_with_ids(vectors[0:insert_count], offsets[0:insert_count])
                    faiss_index.add(vectors[0:insert_count])
                    is_done = True
                except:
                    is_done = False
                    print(traceback.format_exc())
                    print('insert failed, retrying...')
            vectors = np.zeros((page_size, dim), dtype="float32")
            offsets = np.zeros((page_size), dtype="int64")
            insert_count = int(0)
            print(f"insert count = %d" % line_count)
            
        end_time = time.time()
        print(f'Insert data done. Cost %.4fs' % (end_time - start_time))
        index_type += "_" + inp_file.split('/')[-1]
        #faiss_index = faiss.index_gpu_to_cpu(faiss_index) ###GPU 训练和查询大batch下存在问题，所以训练可以采用cpu训练，检索时小batch检索
        faiss.write_index(faiss_index, "./faiss_test1" + index_type + ".index")
        print('faiss index count %d' % (faiss_index.ntotal))
        end_time_save = time.time()
        print('save faiss index done. Cost %.4fs' % (end_time_save - end_time))
        # write stat file
        stat_file = open("stat.json", "w")
        stat_file.write('{"file_size": %d, "origin_count": %d, "insert_count": %d, "insert_cost_seconds": %.0f}' % (file_size, vector_num, line_count, (end_time_save - start_time)))
        stat_file.close()    
        
inp_file = sys.argv[1]
file_id = int(sys.argv[2])
load_data(inp_file, file_id)
