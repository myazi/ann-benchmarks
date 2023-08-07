#########################################################################
# File Name: ann_service.sh
# Author: yingwenjie
# mail: yingwenjie@baidu.com
# Created Time: 2022年07月29日 星期五 22时03分53秒
#########################################################################
#!/bin/bash
nohup /root/anaconda3/envs/python_ann/bin/python ann_service.py 8085 > ann_log_new_spo & ##spo
#/root/anaconda3/envs/python_ann/bin/python ann_service.py 8184 #> ann_log & ##music
#nohup /root/anaconda3/envs/python_ann/bin/python ann_service.py 8084 > ann_log_new_movie & ##movie
