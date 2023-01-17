#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#########################################################################
# File Name: data.py
# Author: yingwenjie
# mail: yingwenjie.com
# Created Time: Tue 08 Nov 2022 03:10:53 PM CST
#########################################################################
import os
import sys
import time
import numpy as np
import struct
import base64
import h5py
import argparse
import faiss

def vec_2_b64str(self, vec, fmt='768f'):
    b_vec = base64.b64encode(struct.pack(fmt, *vec))
    s_vec = str(b_vec, encoding='utf-8')
    return s_vec

def b64str_2_vec(str, fmt='768f'):
    return struct.unpack(fmt, base64.b64decode(str))

def dot_product(v1, v2):
    matrix = np.dot(v1, v2)
    return np.diagonal(matrix)

def vector_norm(p_rep):
    p_rep = np.asarray(p_rep)
    p_vector = dot_product(p_rep ,p_rep.T)
    norm = np.sqrt(p_vector)
    return p_rep / norm.reshape(-1, 1)

def get_vector_num(inp_file):
    line_count = int(0)
    with open(inp_file, "r") as f:
        while 1:
            try:
                line = f.readline()
                if not line:
                    break
                line_count += 1
            except:
                line_count += 1
    print(f"get vector count = %d" % (line_count ))
    return line_count

def get_test(test_file, dim=768):
    train_num = get_vector_num(test_file)
    vectors = np.zeros((train_num, dim), dtype="float32")
    index_line = 0
    with open(test_file) as f:
        for line in f:
            try:
                vecs, query = line.strip('\n').split('\t')
                vec_list = vecs.split(' ')
                #vectors[index_line, :] = np.asarray(vec_list)
                vectors[index_line, :] = vector_norm([np.asarray(vec_list, dtype="float32")]) ##归一化
                index_line += 1
            except:
                continue
    print("test query len:" + "\t" + str(len(vectors)))
    return vectors

def get_train(train_file, dim=768):
    index_line = 0
    train_num = get_vector_num(train_file)
    vectors = np.zeros((train_num, dim), dtype="float32")
    with open(train_file) as f:
       while 1:
            try:
                line = f.readline()
                if not line:
                    break
                line_list = line.strip('\n').split('\t')
                u, t, p, vec = line_list
                vector_ub = b64str_2_vec(vec, str(dim) + "f")
                vectors[index_line, :] = vector_norm([np.asarray(vector_ub)]) ##归一化
                #vectors[index__line, :] = np.asarray([np.asarray(vector_ub)]) 
            except:
                vectors[index_line, :] = np.zeros((1, dim), dtype="float32")
                print("data error:" + "\t" + str(index_line))
            index_line += 1

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
            if insert_line == page_size:
                try:
                    faiss_index.add(vectors)
                except:
                    print(str(index_line) + "\t" + 'insert failed...')
                print(f"line count = %d" % index_line)
                vectors = np.zeros((page_size, dim), dtype="float32")
                insert_line = int(0)

            try:
                line = f.readline()
                if not line:
                    break
                line_list = line.strip('\n').split('\t')
                u, t, p, vec = line_list
                vector_ub = b64str_2_vec(vec, str(dim) + "f")
                vectors[insert_line, :] = vector_norm([np.asarray(vector_ub)]) ##归一化
                #vectors[insert_line, :] = np.asarray([np.asarray(vector_ub)])
            except:
                vectors[insert_line, :] = np.zeros((1, dim), dtype="float32")
                print("data error:" + "\t" + str(index_line))

            index_line += 1
            insert_line += 1

    if insert_line > 0:
        try:
            faiss_index.add(vectors[0:insert_line])
        except:
            print('insert failed, retrying...')
    print(f"line count = %d" % (index_line))
    end_time = time.time()
    print('faiss index count %d' % (faiss_index.ntotal))
    print(f'Insert data done. Cost %.2fs' % (end_time - start_time))

    index_name = train_file.split('/')[-1]
    start_time = time.time()
    faiss.write_index(faiss_index, "./indexs/faiss_baseline_" + index_name + ".index")
    end_time = time.time()
    print('save index %.2fs' % (end_time - start_time))

    return faiss_index

def get_top(faiss_index, test, topk=100):
    neighbors = []
    distances = []
    top_list = []
    start_time = time.time()
    res_dist, res_p_id = faiss_index.search(np.asarray(test).astype('float32'), int(topk))
    end_time = time.time()
    print('Search done: Cost %.4fs' % (end_time - start_time))
    for i in range(len(res_dist)):
        distances.append(res_dist[i])
        neighbors.append(1 + res_p_id[i])

    return tuple(neighbors), tuple(distances)

def data2h5(train_file, test_file, out_file, topk):
    dim = 512
    test = get_test(test_file, dim)
    faiss_index = knn(train_file, test, dim=dim)
    neighbors, distances = get_top(faiss_index, test, topk)
    train = get_train(train_file, dim)
    
    start_time = time.time()
    f = h5py.File(out_file + ".hdf5", 'w')
    f.create_dataset("train", data=train)
    f.create_dataset("test", data=test)
    f.create_dataset("distances", data=distances)
    f.create_dataset("neighbors", data=neighbors)
    f.attrs["type"] = "dense"
    f.attrs['point_type'] = "float"
    f.attrs['dimension'] = dim
    f.attrs["distance"] = "ip"
    f.close()
    end_time = time.time()
    print('save hdf5 %.2fs' % (end_time - start_time))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--task_name',
        metavar='NAME',
        help='task name save hdf5',
        default='test_aurora_1M')
    parser.add_argument(
        "-k", "--count",
        default=100,
        type=int,
        help="the number of near neighbours to search for")
    parser.add_argument(
        '--input_para',
        metavar='FILE',
        help='input para vector and content'
             ' the best result',
        default='')
    parser.add_argument(
        '--input_query',
        metavar='FILE',
        help='input query vector and content',
        default='')
    args = parser.parse_args()

    data2h5(args.input_para, args.input_query, args.task_name, args.count)
