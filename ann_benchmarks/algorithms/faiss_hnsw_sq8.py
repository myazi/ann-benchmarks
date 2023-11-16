from __future__ import absolute_import
import os
import faiss
import numpy as np
from ann_benchmarks.constants import INDEX_DIR
from ann_benchmarks.algorithms.base import BaseANN
from ann_benchmarks.algorithms.faiss import Faiss


class FaissHNSW_SQ8(Faiss):
    def __init__(self, metric, method_param):
        self._metric = metric
        self.method_param = method_param

    def fit(self, X):
        qtype = getattr(faiss.ScalarQuantizer, "QT_8bit")
        self.index = faiss.IndexHNSWSQ(len(X[0]), qtype, self.method_param["M"]) #默认L2 相似性度量，可以通过数据集中的distance字段判断数据使用的相似性度量，同步使用一致的相似性度量，其他地方没有存储相似性度量标识
        #self.index = faiss.IndexHNSWSQ(len(X[0]), qtype, self.method_param["M"], faiss.METRIC_INNER_PRODUCT)
        self.index.hnsw.efConstruction = self.method_param["efConstruction"]

        self.index.verbose = True

        if X.dtype != np.float32:
            X = X.astype(np.float32)
        self.index.train(X)
        self.index.add(X)
        faiss.omp_set_num_threads(1)

    def fit_batch(self, X, dim):
        qtype = getattr(faiss.ScalarQuantizer, "QT_8bit")
        self.index = faiss.IndexHNSWSQ(dim, qtype, self.method_param["M"])
        #self.index = faiss.IndexHNSWSQ(dim, qtype, self.method_param["M"], faiss.METRIC_INNER_PRODUCT)
        self.index.hnsw.efConstruction = self.method_param["efConstruction"]

        self.index.verbose = True
        for x in X:
            if self.index.is_trained == False:
                print("training")
                self.index.train(x)
                print("train done")
            print("adding")
            self.index.add(x)
            self.index.is_trained = True
        faiss.omp_set_num_threads(1)

    def query(self, v, n):
        if self._metric == 'angular':
            v /= np.linalg.norm(v)
        D, I = self.index.search(np.expand_dims(
            v, axis=0).astype(np.float32), n)
        return I[0]
        ##大规模数据，无法重新暴力计算相似分，使用下面的返回
        R = []
        for i in range(len(I[0])):
            R.append((I[0][i], D[0][i]))
        return R
    def set_query_arguments(self, ef):
        faiss.cvar.hnsw_stats.reset()
        self.index.hnsw.efSearch = ef

    def get_additional(self):
        return {"dist_comps": faiss.cvar.hnsw_stats.ndis}

    def __str__(self):
        return 'faiss (%s, ef: %d)' % (self.method_param, self.index.hnsw.efSearch)

    def freeIndex(self):
        del self.p
