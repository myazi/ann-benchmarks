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
import math
import base64
import configparser
import h5py

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
                #if(len(fields) < 2):
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

def get_train(train_file):

    train_num = get_vector_num(train_file)
    vectors = np.zeros((train_num, 768), dtype="float32")
    line_index = 0
    with open(train_file) as f:
        for line in f:
            #u, t, p, tp, vec = line.strip('\n').split('\t')
            u, t, tp, p, vec = line.strip('\n').split('\t')
            #try:
            vector_ub = b64str_2_vec(vec)
            #except:
            #    print(line_index)
            #vectors[line_index, :] = vector_norm([np.asarray(vector_ub)]) ##需要归一化
            vectors[line_index, :] = np.asarray([np.asarray(vector_ub)]) ##不需要归一化
            line_index += 1
            #if line_index > 100000: break
            #print(vector_ub)
    return vectors#[0:100000,:]

def get_test(test_file):

    train_num = get_vector_num(test_file)
    vectors = np.zeros((train_num, 768), dtype="float32")
    line_index = 0
    with open(test_file) as f:
        for line in f:
            vecs, query = line.strip('\n').split('\t')
            vec_list = vecs.split(' ')
            vectors[line_index, :] = np.asarray(vec_list)
            line_index += 1
    return vectors

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

def data2h5(train_file, test_file, top_file, out_file):
    train = get_train(train_file)
    print(train.shape)
    test = get_test(test_file)
    print(test.shape)
    neighbors, distances = get_top(top_file)
    
    f = h5py.File(out_file, 'w')
    f.create_dataset("train", data=train)
    f.create_dataset("test", data=test)
    f.create_dataset("distances", data=distances)
    f.create_dataset("neighbors", data=neighbors)
    f.attrs["type"] = "dense"
    f.attrs['point_type'] = "float"
    f.attrs['dimension'] = 768
    f.attrs["distance"] = "ip" ##指定距离度量
    f.close()

if __name__ == "__main__":
    train_file = sys.argv[1]
    test_file = sys.argv[2]
    top_file = sys.argv[3]
    out_file = sys.argv[4]
    data2h5(train_file, test_file, top_file, out_file)
