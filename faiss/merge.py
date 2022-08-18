# -*- coding: utf-8 -*-

import sys
import random
import numpy as np
import math
import time
import copy

def merge(score1, ids1, score2, ids2, topk):
    score = []
    ids = []
    i = j = 0
    while len(score) < topk and i < len(score1) and j < len(score2):
        if score1[i] >= score2[j]:
            score.append(score1[i])
            ids.append(ids1[i])
            i += 1
        else:
            score.append(score2[j])
            ids.append(ids2[j])
            j += 1
    return score, ids

def mergeSort(score, ids, topk):
    if len(score) < 2:
        return score[0], ids[0]
    mid = math.floor(len(score) / 2)
    score1, ids1 = mergeSort(score[0:mid, :], ids[0:mid, :], topk)
    score2, ids2 = mergeSort(score[mid:, :], ids[mid:, :], topk)
    score, ids = merge(score1, ids1, score2, ids2, topk)
    return score, ids

def merge2(score1, ids1, score2, ids2, score3, ids3, topk):
    score = []
    ids = []
    i = j = k = 0
    while len(score) < topk and i < len(score1) and j < len(score2) and k < len(score3):
        if score1[i] >= score2[j] and score1[i] >= score3[k]:
            score.append(score1[i])
            ids.append(ids1[i])
            i += 1
        if score2[j] > score1[i] and score2[j] >= score3[k]:
            score.append(score2[j])
            ids.append(ids2[j])
            j += 1
        if score3[k] > score1[i] and score3[k] > score2[j]:
            score.append(score3[k])
            ids.append(ids3[k])
            k += 1
    return score, ids

def mergeSort2(score, ids, topk):
    if len(score) == 1:
        return score[0], ids[0]
    if len(score) == 2:
        return merge(score[0], ids[0], score[1], ids[1], topk)
    mid1 = math.floor(len(score) / 3)
    mid2 = math.floor(len(score) / 3) * 2
    score1, ids1 = mergeSort2(score[0:mid1, :], ids[0:mid1, :], topk)
    score2, ids2 = mergeSort2(score[mid1:mid2, :], ids[mid1:mid2, :], topk)
    score3, ids3 = mergeSort2(score[mid2:, :], ids[mid2:, :], topk)
    score, ids = merge2(score1, ids1, score2, ids2, score3, ids3, topk)
    return score, ids

def mergeN(score, ids, para, topk):
    """
    score是所有节点返回的topk结果的矩阵，每一列是一个节点上的topk结果
    入参：score 相似分矩阵 numpy, ids offset id矩阵 numpy, para内容 list, topk 最终返回topk个结果
    返回值: topk 相似性list，offset list
    score: [
        [8, 7, 12],
        [5, 4, 6],
        [3, 2, 5]
    ]
    """
    res_score = []
    res_ids = []
    res_para = []
    index_flag = np.zeros(score.shape[0], dtype='int')
    for i in range(topk):
        index = np.argmax(score[:, 0])
        res_score.append(score[index, 0])
        res_ids.append(ids[index, 0])
        res_para.append(para[index][0])
        score[index, 0] = score[index, index_flag[index] + 1] #将第index个节点上的下一个最大值移到最大值位置上
        ids[index, 0] = ids[index, index_flag[index] + 1]
        para[index][0] = para[index][index_flag[index] + 1]
        index_flag[index] += 1
    return res_score, res_ids, res_para    
        
if __name__ == '__main__':
    topk = 100
    num = 1000
    
    score = [[random.random() for _ in range(topk)] for _ in range(num)]
    score_list = [] 
    score_map = {}
    k = 0
    for ss in score:
         ss.sort(reverse=True)
         score_list.append(ss)

    start = time.time()
    for ss in score:
         for s in ss:
             score_map[s] = k
             k += 1
    map_list = sorted(score_map.items(), key = lambda x:x[0],reverse = True)
    end = time.time()
    print("===================map_sort===================")
    print(map_list[0:topk])
    print("map_sort cost time: " + str(end - start))

    score = np.array(score_list) 
    ids = [_ for _ in range(topk * num)]
    ids = np.array(ids).reshape(num, topk)
    assert len(score) == len(ids)

    start = time.time()
    merge_score, merge_ids = mergeSort(score, ids, topk)
    end = time.time()
    print("===================merge_sort===================")
    print(merge_score)
    print(merge_ids)
    print("merge_sort cost time: " + str(end - start))

    start = time.time()
    merge2_score, merge2_ids = mergeSort2(score, ids, topk)
    end = time.time()
    print("===================merge2_sort===================")
    print(merge2_score)
    print(merge2_ids)
    print("merge2_sort cost time: " + str(end - start))

    start = time.time()
    score, ids = mergeN(score, ids, topk)
    end = time.time()
    print("===================mergeN_sort===================")
    print(score)
    print(ids)
    print("mergeN_sort cost time: " + str(end - start))

