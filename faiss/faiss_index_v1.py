import sys
import time
import faiss
import math
import numpy as np
import random
import os
import struct
import traceback

def load_data(inp_file):
    dim = 768
    # 文件名格式：part-00000.bin
    # file_id = int(inp_file[-9:][:5])
    #  insert data
    start_time = time.time()
    page_size = int(10000)
    line_count = int(0)
    #url_docs = []
    num = 10000000 #num必须大于等于实际数据量
    vectors = np.zeros((num, dim), dtype="float32")
    offsets = np.zeros((num), dtype="int64")
    with open(inp_file, "rb") as f:
        file_size = os.path.getsize(inp_file)
        cursor = 0
        buffer_page = 1024 * 1024 * 1
        file_cursor = 0
        current_file_cursor = 0
        data = f.read(buffer_page)
        data_len = buffer_page
        while file_cursor < file_size:
            if cursor > data_len:
                #print("file_cursor = %d, file_size = %d, buffer_size = %d" % (file_cursor, file_size, buffer_page))
                f.seek(file_cursor, 0)
                current_file_cursor = file_cursor
                if file_size - file_cursor >= buffer_page:
                    data = f.read(buffer_page)
                    data_len = buffer_page
                else:
                    data = f.read(file_size - file_cursor)
                    data_len = file_size - file_cursor
                cursor = 0
            cursor += 4 * dim
            if cursor > data_len:
                continue
            vector = struct.unpack("{}f".format(dim), data[cursor - 4 * dim: cursor])
            cursor += 4
            if cursor > data_len:
                continue
            value_len = struct.unpack("I", data[cursor - 4 : cursor])[0]
            cursor += value_len
            if cursor > data_len:
                continue
            #vectors.append(vector)
            vectors[line_count,:] = np.asarray(vector)
            offset = current_file_cursor + cursor - value_len - 4
            #offsets.append(offset)
            offsets[line_count] = offset
            file_cursor += dim * 4 + 4 + value_len
            line_count += 1
            if line_count % 10000 == 0:
                print(f"insert count = %d" % line_count)
        end_time = time.time()
        print(f'Insert data done. Cost %.4fs' % (end_time - start_time))
        
        return vectors[:line_count,], offsets[:line_count,]

def load_conf(conf_file):
    conf_list = []
    with open(conf_file) as f:
        for line in f:
            line_list = line.strip('\n').split('\t')
            if len(line_list) < 4:
                continue
            if "#" in line_list[0] or "name" == line_list[0]:
                continue
            conf_list.append(line_list)
    return conf_list

def baseline(para_emb, ids, dim, query_emb, topk):

    begin_time = time.time()
    index = ip_index(dim)
    index2 = faiss.IndexIDMap(index)
    index2.add_with_ids(para_emb, ids)
    #index.add(para_emb)
    end_time = time.time()
    print("baseline" + "\t" + "load & create index time: " + str(end_time - begin_time))
    begin_time = time.time()
    res_dist, res_p_id = index2.search(query_emb, topk)
    end_time = time.time()
    print("baseline" + "\t" + "search time: " + str(end_time - begin_time))
    return res_dist, res_p_id

def build_engine(para_emb, ids, dim, nlist, nprobe):

    index = IndexIVFSQ8(dim, nlist)

    index.nprobe = nprobe
    index.train(para_emb)
    index2 = faiss.IndexIDMap(index)
    index2.add_with_ids(para_emb, ids)
    #index.add(para_emb)
    print ("insert done", file=sys.stderr)

    return index2

def test_engine(index, query_emb, topk):

    res_dist, res_p_id = index.search(query_emb, topk)
    return res_dist, res_p_id

def write_res(res_dist, res_p_id, res_file):
    fo = open(res_file, 'w')
    for i in range(len(res_p_id)):
        res_list = []
        for j in range(len(res_p_id[i])):
            p_id = res_p_id[i][j]
            score = res_dist[i][j]
            res_list.append([p_id, score])
            #print(str(p_id) + "\t" + str(score))
            fo.write(str(i) + "\t" + str(p_id) + "\t" + str(score) + "\n")

def IndexIVFSQ8(d, nlist):
    quantizer = faiss.IndexFlatIP(d)
    #quantizer = faiss.IndexIVFFlat(quantizer, d, nlist, faiss.METRIC_INNER_PRODUCT)
    qtype = getattr(faiss.ScalarQuantizer, "QT_8bit")
    index = faiss.IndexIVFScalarQuantizer(quantizer, d, nlist, qtype, faiss.METRIC_INNER_PRODUCT)
    return index

def ip_index(d):
    index = faiss.IndexFlatIP(d)
    return index
    

def main():

    conf_file = sys.argv[1]
    conf_list = load_conf(conf_file)

    dim = 768
    num = 1000000
    #rs = np.random.RandomState(1338)
    #vectors = rs.normal(size=(num, dim))
    #vectors = vectors.astype('float32')
    #vectors = [[random.random() for _ in range(dim)] for _ in range(num)]
    #vectors = np.asarray(vectors).astype('float32')
    vectors, ids = load_data("data/part-00000.bin")
    print(vectors)
    print(vectors.shape)
    print(vectors.dtype)
    print(ids)
    print(ids.shape)
    print(ids.dtype)
    print("load done...")

    #res_dist, res_p_id = baseline(vectors, ids, dim, vectors[-1000:], 50)
    #write_res(res_dist, res_p_id, "res/baseline_offset")
    #exit()
    for t in conf_list:
        name, nlist, nprobe, topk = t[0:4]
        nlist = int(nlist)
        nprobe = int(nprobe)
        topk = int(topk)
        res_file = "./res/" + name + "_offset"

        begin_time = time.time()
        engine = build_engine(vectors, ids, dim, nlist, nprobe)
        end_time = time.time()
        print(name + "\t" + "load & create index time: " + str(end_time - begin_time))

        begin_time = time.time()
        test_engine(engine,  vectors[-1:], topk)
        end_time = time.time()
        print(name + "\t" + "search time: " + str(end_time - begin_time))

        res_dist, res_p_id = test_engine(engine,  vectors[-1000:], topk)
        write_res(res_dist, res_p_id, res_file)

if __name__ == "__main__":
    main()

