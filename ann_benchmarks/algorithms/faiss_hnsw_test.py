from __future__ import absolute_import
import os
import faiss
import numpy as np
from ann_benchmarks.constants import INDEX_DIR
from ann_benchmarks.algorithms.base import BaseANN
from ann_benchmarks.algorithms.faiss import Faiss


class FaissHNSW_test(Faiss):
    def __init__(self, metric, method_param):
        self._metric = metric
        self.method_param = method_param

    def fit(self, X):
        self.index = faiss.IndexHNSWFlat(len(X[0]), self.method_param["M"])
        self.index.hnsw.efConstruction = self.method_param["efConstruction"]
        self.index.verbose = True

        if self._metric == 'angular':
            X = X / np.linalg.norm(X, axis=1)[:, np.newaxis]
        if X.dtype != np.float32:
            X = X.astype(np.float32)

        self.index.add(X)
        faiss.omp_set_num_threads(1)

    def fit_batch(self, X, dim):
        self.index = faiss.IndexHNSWFlat(dim, self.method_param["M"])
        self.index.hnsw.efConstruction = self.method_param["efConstruction"]
        self.index.verbose = True
        for x in X:
            self.index.add(x)
        faiss.omp_set_num_threads(1)

    def query(self, v, n):
        if self._metric == 'angular':
            v /= np.linalg.norm(v)
        D, I = self.index.search(np.expand_dims(
            v, axis=0).astype(np.float32), n)
        return I[0]
        R = []
        for i in range(len(I[0])):
            R.append((I[0][i], D[0][i]/2)) ##默认返回的距离度量为L2 = 2 - 2IP, 因为IP=cos，L2 = 2 - 2cos； 因为angular= 1 - cos，L2 = 2 * angular
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
