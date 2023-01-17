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
import numpy as np
import os
import struct
import base64
import h5py
import faiss

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
    line_count = int(0)
    page_size = int(10000)
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

def vector_norm(p_rep):
    p_rep = np.asarray(p_rep)
    p_vector = dot_product(p_rep ,p_rep.T)
    norm = np.sqrt(p_vector)
    return p_rep / norm.reshape(-1, 1)

def get_train(train_file):
    train_num = get_vector_num(train_file)
    vectors = np.zeros((train_num, 768), dtype="float32")
    line_index = 0
    with open(train_file) as f:
        for line in f:
            u, t, p, tp, vec = line.strip('\n').split('\t')
            try:
                vector_ub = b64str_2_vec(vec)
            except:
                print(line_index)
            vectors[line_index, :] = vector_norm([np.asarray(vector_ub)]) ##归一化
            #vectors[line_index, :] = np.asarray([np.asarray(vector_ub)]) 
            line_index += 1
    return vectors

def get_test(test_file):
    train_num = get_vector_num(test_file)
    vectors = np.zeros((train_num, 768), dtype="float32")
    line_index = 0
    with open(test_file) as f:
        for line in f:
            vecs, query = line.strip('\n').split('\t')
            vec_list = vecs.split(' ')
            vectors[line_index, :] = np.asarray(vec_list)
            #vectors[line_index, :] = vector_norm([np.asarray(vec_list)]) ##归一化
            line_index += 1
    return vectors

def knn(train_file, test, topk=100, dim=768):
    index_line = 0
    insert_line = 0
    page_size = 10000
    vectors = np.zeros((page_size, dim), dtype="float32")
    faiss_index = faiss.IndexFlatIP(dim)
    is_trained = faiss_index.is_trained
    start_time = time.time()
    with open(train_file, "r") as f:
        while 1:
            line = f.readline()
            index_line += 1
            if not line:
                break
            line_list = line.strip('\n').split('\t')
            if len(line_list) != 5:
                print('data format is error...')
            u, t, p, tp, vec = line_list
            try:
                vector_ub = b64str_2_vec(vec)
            except:
                print(index_line)
            vectors[insert_line, :] = vector_norm([np.asarray(vector_ub)]) ##归一化
            #vectors[insert_line, :] = np.asarray([np.asarray(vector_ub)])
            insert_line += 1
            if index_line % page_size == 0 and insert_line > 0 and is_trained == True:
                try:
                    faiss_index.add(vectors)
                except:
                    print(str(index_line) + "\t" + 'insert failed...')
                vectors = np.zeros((page_size, dim), dtype="float32")
                insert_line = int(0)
                print(f"insert count = %d" % index_line)
    if insert_line > 0:
        try:
            faiss_index.add(vectors[0:insert_line])
        except:
            print('insert failed, retrying...')
    end_time = time.time()
    print(f'Insert data done. Cost %.2fs' % (end_time - start_time))

    neighbors = []
    distances = []
    top_list = []
    num, dim = test.shape
    sum_time = 0
    for i in range(num):
        start_time = time.time()
        res_dist, res_p_id = faiss_index.search(np.asarray([test[i]]).astype('float32'), int(topk))
        end_time = time.time()
        sum_time += end_time - start_time
        distances.append(1 - res_dist[0]) # 1 -ip = angular
        neighbors.append(1 + res_p_id[0]) # id = id + 1
        res_list = []
        for j in range(len(res_p_id[0])):
            p_id = res_p_id[0][j]
            score = res_dist[0][j]
            top_list.append([i, p_id, 1 - score])
            print(str(i) + "\t" + str(p_id) + "\t" + str(1 - score))
    print('Search done: Avg Cost %.4fs' % (sum_time / num))

    start_time = time.time()
    index_name = train_file.split('/')[-1]
    faiss.write_index(faiss_index, "./faiss_baseline_" + index_name + ".index")
    end_time = time.time()
    print('faiss index count %d' % (faiss_index.ntotal))

    return tuple(neighbors), tuple(distances)

def get_top(top_file):
    neighbors = []
    distances = []
    neighbor = []
    distance = []
    pre_index = 0
    with open(top_file) as f:
        for line in f:
            index, top_index, sim = line.strip('\n').split('\t')
            index = int(index)
            top_index = int(top_index)
            sim = float(sim)
            #dis = 1 - sim # ip 转 arugula
            dis = sim
            if index != pre_index:
                distances.append(distance)
                neighbors.append(neighbor)
                pre_index = index
                neighbor = []
                distance = []
            distance.append(dis)
            neighbor.append(top_index)
    distances.append(distance)
    neighbors.append(neighbor)
    return tuple(neighbors), tuple(distances)

def data2h5(train_file, test_file, out_file):
    test = get_test(test_file)
    neighbors, distances = knn(train_file, test)
    train = get_train(train_file)
    
    start_time = time.time()
    f = h5py.File(out_file, 'w')
    f.create_dataset("train", data=train)
    f.create_dataset("test", data=test)
    f.create_dataset("distances", data=distances)
    f.create_dataset("neighbors", data=neighbors)
    f.attrs["type"] = "dense"
    f.attrs['point_type'] = "float"
    f.attrs['dimension'] = 768
    f.attrs["distance"] = "angular" ##指定距离度量
    f.close()
    end_time = time.time()
    print('save hdf5 %.2fs' % (end_time - start_time))

if __name__ == "__main__":
    train_file = sys.argv[1]
    test_file = sys.argv[2]
    out_file = sys.argv[3]
    data2h5(train_file, test_file, out_file)
