# -*- coding: utf-8 -*-
import sys
import struct

def read_bin_file(file_name):
    buffer_page = 1024 * 1024 * 1

    in_fp = open(file_name, "rb")
    in_fp.seek(0, 0)
    data = in_fp.read(buffer_page)
    cursor = 0
    while 1:
        vectors = struct.unpack('{}f'.format(768), data[cursor: cursor + 4 * 768])
        cursor += 768 * 4
        #cursor += 1
        #print >>sys.stderr, vectors
        #print vectors
        value_len = struct.unpack('I', data[cursor: cursor + 4])[0]
        value_len_int = int(value_len)
        cursor += 4
        #cursor += 1
        #print("value_len = %d" % value_len_int)
        print(" ".join([str(a) for a in vectors]) + "\t" + str(data[cursor: cursor + value_len_int]))#.decode("UTF-8")
        cursor += value_len_int
        #cursor += 1

def load_vector_query(inp_file):
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
    return vec_list,query_list

def cal_ip(a, b):
    ip = 0
    for i in range(len(a)):
        ip += a[i] * b[i]
    return ip

def read_para(faiss_file, bin_file, query_file):
    #fo = open("./data/part-00000.bin", "rb")
    fo = open(bin_file, "rb")
    fo.seek(0, 0)
    buffer_page = 1024 * 1024 * 1

    query_emb = {}
    #vec_list, query_list = load_vector_query("./data/query_1W.emb")
    vec_list, query_list = load_vector_query(query_file)
    for i in range(len(vec_list)):
        query_emb[str(i)] = vec_list[i] 


    with open(faiss_file) as f:
        for line in f:    
            line_list = line.strip('\n').split('\t')
            if len(line_list) < 2:
                continue
            qid, query_content, pid, offset, dist = line_list
            offset = int(offset)
            offset -= 4 * 768
            fo.seek(offset, 0)
            data = fo.read(buffer_page)
            p_vec = struct.unpack('{}f'.format(768), data[0: 4 * 768])
            offset += 4 * 768
            fo.seek(offset, 0)
            data = fo.read(buffer_page)
            value_len = struct.unpack('I', data[0: 4])[0]
            value_len_int = int(value_len) #读取文本长度:
            #print(value_len_int)
            passage = str(data[4: 4 + value_len_int]) #读取passage内容
            line_list[3] = passage
            #ip = cal_ip(query_emb[qid], p_vec)
            print("\t".join(line_list) + "\t" + str(ip))
            #print("\t".join(line_list) + "\t" + " ".join([str(a) for a in query_emb[qid]]) + "\t" + " ".join([str(a) for a in p_vec]) + "\t" + str(ip))
            #print("query" + "\t" + query_content + "\t" + " ".join([str(a) for a in query_emb[qid]]))
            #print("paragraph" + "\t" + passage + "\t" + " ".join([str(a) for a in p_vec]))
            #print(passage)
if __name__ == '__main__':
    faiss_file = sys.argv[1]
    bin_file = sys.argv[2]
    query_file = sys.argv[3]
    read_para(faiss_file, bin_file, query_file)
