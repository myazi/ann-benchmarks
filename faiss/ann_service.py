#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import json
import web
import faiss
import struct
import sys
import time


class GetIndex:
    def POST(self):
        web.header('content-type', 'text/json')
        params = json.loads(web.data())
        vector = params['vectors']
        k = params['k']
        query = params['query']
        p_emb_matrix = np.asarray(vector)
        if 'ef' in params:
            faiss.ParameterSpace().set_index_parameter(FINDEX, "efSearch", int(params['ef']))
        else:
            faiss.ParameterSpace().set_index_parameter(FINDEX, "efSearch", int(1200))
        start_time = time.time()
        D,I = FINDEX.search(p_emb_matrix.astype('float32'), k)
        end_request_time = time.time()
        print("search time %s" % str(end_request_time - start_time))
        passages_list = []
        for offsetList in I:
            passages = []
            for offset in offsetList:
                offset = int(offset)
                line = PARA_INDEX[offset]
                line = line.strip()
                fields = line.split("\t")
                passage = ''
                for ind in range(len(fields)):
                    passage += fields[ind]
                    if ind < len(fields)-1:
                        passage += "\t"
                passages.append(passage)
            passages_list.append(passages)

        end_para_time = time.time()
        print("para time %s" % str(end_para_time - end_request_time))
        response_object = {"error_code": "0", "error_message": "", "s": D.tolist(), \
                "o":I.tolist(), "p":passages_list,"query":query}
        message = json.dumps(response_object)
        return message


if __name__ == "__main__":
    global FINDEX
    FINDEX = faiss.read_index('/data/work/dqa/http/ann_server/index/faiss_HNSW_SQ8_all_process_qtp_new_vec.index')
    faiss.omp_set_num_threads(1)
    # load para
    global PARA_INDEX
    PARA_INDEX = {}
    with open('/data/work/dqa/http/ann_server/index/all_process_qtp_new_vec_base64') as para_doc:
        line_index = 0
        for line in para_doc:
            line_index += 1
            line_list = line.strip('\n').split('\t')
            if len(line_list) < 4: 
                line_list = ["error"] * 4
            sid, u, t, p = line_list[0:4]
            PARA_INDEX[line_index] = "\t".join([t, p, u, sid])
    print("load done")
    urls = (
            '/', 'GetIndex'
            )
    app = web.application(urls, globals())
    app.run()
