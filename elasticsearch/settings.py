#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
common settings
"""
import os
from consts import const
import json

BASE_DIR = os.getenv('BASE_DIR', '/home/work')
BASE_SERVER_IP = os.getenv('BASE_SERVER_IP', '127.0.0.1')
DEFAULT_DB_DBHOST = os.getenv('DEFAULT_DB_DBHOST', '127.0.0.1')
DEFAULT_DB_DBPORT = os.getenv('DEFAULT_DB_DBPORT', '3306')
DEFAULT_DB_DBUSER = os.getenv('DEFAULT_DB_DBUSER', 'root')
DEFAULT_DB_DBPWD = os.getenv('DEFAULT_DB_DBPWD', 'aurora@2022')
DEFAULT_DB_DBNAME = os.getenv('DEFAULT_DB_DBNAME', 'aurora')

#DEFAULT_ES_HOST = os.getenv('DEFAULT_ES_HOST', '127.0.0.1')
DEFAULT_ES_HOST = os.getenv('DEFAULT_ES_HOST', '192.168.1.4')
DEFAULT_ES_PORT = os.getenv('DEFAULT_ES_PORT', '9200')
DEFAULT_ES_USER = os.getenv('DEFAULT_ES_USER', 'elastic')
DEFAULT_ES_PASSWD = os.getenv('DEFAULT_ES_PASSWD', '1234')
DATA_API_HOSTNAME = os.getenv('DATA_API_HOSTNAME', 'data-api')
DATA_API_PORT = os.getenv('DATA_API_TCP_PORT', 8024)

DEFAULT_LOG_LEVEL = os.getenv('DEFAULT_LOG_LEVEL', 'info')
LOG_DIR = os.getenv('LOG_DIR', './log')

DATABASE_DEPLOYMENT_TYPE = os.getenv('DATABASE_DEPLOYMENT_TYPE',
                                     'elasticsearch')

# 解决k8s 环境变量冲突，重新设置容器内启动端口
WEB_API_PORT = os.getenv('WEB_API_TCP_PORT', 8100)
WEB_API_HOSTNAME = os.getenv("WEB_API_SERVER", "web-api")
WEB_API_DATA_PATH = os.getenv("WEB_API_DATA_PATH", "/ceph/data/web-api")

ANN_MANAGE_API_PORT = os.getenv('ANN_MANAGE_API_TCP_PORT', 8101)
ANN_MANAGE_API_HOSTNAME = os.getenv("ANN_MANAGE_API_SERVER", "ann-manage-api")
ANN_MANAGE_API_DATA_PATH = os.getenv("ANN_MANAGE_API_DATA_PATH", "/ceph/data")

KVSTORE_PORT = os.getenv('KVSTORE_TCP_PORT', 8900)
KVSTORE_HOSTNAME = os.getenv("KVSTORE_SERVER", "kvstore-kvproxy-online")
KVSTORE_MAP_STR = os.getenv(
    "KVSTORE_MAP", '{\
                      "http://kvstoreonline-kvstore-0.kvstore-kvstore-online:8901":"/ceph/data/kvstore0", \
                      "http://kvstoreonline-kvstore-1.kvstore-kvstore-online:8901":"/ceph/data/kvstore1", \
                      "http://kvstoreonline-kvstore-2.kvstore-kvstore-online:8901":"/ceph/data/kvstore2" \
                    }')
KVSTORE_MAP = json.loads(KVSTORE_MAP_STR)
KVSTORE_OFFLINE_PORT = os.getenv('KVSTORE_OFFLINE_TCP_PORT', 8900)
KVSTORE_OFFLINE_HOSTNAME = os.getenv("KVSTORE_OFFLINE_SERVER",
                                     "kvstore-kvproxy")
KVSTORE_OFFLINE_DATA_PATH = os.getenv("KVSTORE_OFFLINE_DATA_PATH",
                                      "/ceph/data/offline/kvstore0")

ASYNC_FRAMEWORK_PORT = os.getenv('ASYNC_FRAMEWORK_TCP_PORT', 8104)
ASYNC_FRAMEWORK_HOSTNAME = os.getenv("ASYNC_FRAMEWORK_SERVER",
                                     "async-framework")

ANN_CONTROLLER_PORT = os.getenv('ANN_CONTROLLER_TCP_PORT', 8106)
ANN_CONTROLLER_HOSTNAME = os.getenv('ANN_CONTROLLER_SERVER', "ann-controller")

PARALLEL_NUM = os.getenv('PARALLEL_NUM', 1)

DOC_SHARDS = os.getenv('DOC_SHARDS', 8)
DOC_REPLICAS = os.getenv('DOC_REPLICAS', 1)
PARA_SHARDS = os.getenv('PARA_SHARDS', 4)
PARA_REPLICAS = os.getenv('PARA_REPLICAS', 1)

FAISS_SHARDS = os.getenv('FAISS_SHARDS', 1)

OFFLINE_REPLICAS = os.getenv('OFFLINE_REPLICAS', 1)
ONLINE_REPLICAS = os.getenv('ONLINE_REPLICAS', 3)

PARA_SIZE = os.getenv("PARA_SIZE", 768)

ALERT_PROJECT_COUNT = os.getenv("ALERT_PROJECT_COUNT", 2000)
ALERT_TEST_PERIOD = os.getenv("ALERT_TEST_PERIOD", 3600000)  # seconds
ALERT_USER_LIST = os.getenv("ALERT_USER_LIST", "wangyifei06").split(',')
PROJECT_ENV_NAME = os.getenv("PROJECT_ENV_NAME", "aurora")

META_SERVERS = os.getenv(
    'META_SERVERS',
    'http://kvstore-organizer-0.kvstore-organizer:8902,http://kvstore-organizer-1.kvstore-organizer:8902,http://kvstore-organizer-2.kvstore-organizer:8902'
).split(',')
HB_TIMEOUT = 1

NAMESPACE = os.getenv('K8S_NAMESPACE', 'engine')

SEARCH_API_HTTP_PORT = os.getenv('SEARCH_API_HTTP_PORT', 8872)

settings = dict(
    base_dir=BASE_DIR,
    database_deployment_type=DATABASE_DEPLOYMENT_TYPE,
    doc_shards=DOC_SHARDS,
    doc_replicas=DOC_REPLICAS,
    para_shards=PARA_SHARDS,
    para_replicas=PARA_REPLICAS,
    databases={
        const.DEFAULT_DB_KEY: {
            const.DBHOST_KEY: DEFAULT_DB_DBHOST,
            const.DBPORT_KEY: DEFAULT_DB_DBPORT,
            const.DBUSER_KEY: DEFAULT_DB_DBUSER,
            const.DBPWD_KEY: DEFAULT_DB_DBPWD,
            const.DBNAME_KEY: DEFAULT_DB_DBNAME
        }
    },
    es_default_config={
        "ip": DEFAULT_ES_HOST,
        "port": DEFAULT_ES_PORT,
        "user": DEFAULT_ES_USER,
        "passwd": DEFAULT_ES_PASSWD,
        "number_of_shards": 32,
        "number_of_replicas": 0,
        "metric": "dot_product",
        "dim": 768,
        "index_arg_m": 32,
        "index_arg_ef": 500,
        "num_candidates": 800
    },
    log={
        const.LOG_DIR: LOG_DIR,
        const.LOG_MIN_LEVEL: DEFAULT_LOG_LEVEL,
        const.LOG_RETENTION_DAYS: 7,
        const.LOG_IS_CONSOLE: True
    },
    apps={
        const.WEB_API: {
            const.APP_NAME: const.WEB_API,
            const.APP_PORT: WEB_API_PORT,
            const.APP_SERVER: '{}:{}'.format(WEB_API_HOSTNAME, WEB_API_PORT),
            const.ROUTER_PARALLEL_NUM: PARALLEL_NUM,
            const.DATA_PATH: WEB_API_DATA_PATH,
            const.WEBAPI_PROJECT_STATE: {
                const.WEBAPI_STATE_NEW_KEY: const.WEBAPI_STATE_NEW_VALUE,
                const.WEBAPI_STATE_IMPORTING_KEY:
                const.WEBAPI_STATE_IMPORTING_VALUE,
                const.WEBAPI_STATE_IMPORT_ERROR_KEY:
                const.WEBAPI_STATE_IMPORT_ERROR_VALUE,
                const.WEBAPI_STATE_IMPORT_SUCCESS_KEY:
                const.WEBAPI_STATE_IMPORT_SUCCESS_VALUE,
                const.WEBAPI_STATE_INDEX_DOING_KEY:
                const.WEBAPI_STATE_INDEX_DOING_VALUE,
                const.WEBAPI_STATE_INDEX_ERROR_KEY:
                const.WEBAPI_STATE_INDEX_ERROR_VALUE,
                const.WEBAPI_STATE_SUCCESS_KEY:
                const.WEBAPI_STATE_SUCCESS_VALUE
            },
            const.WEBAPI_DOC_IMPORT_STATE: {
                const.WEBAPI_STATE_NONE_KEY:
                const.WEBAPI_STATE_NONE_VALUE,
                const.WEBAPI_STATE_IMPORTING_KEY:
                const.WEBAPI_STATE_IMPORTING_VALUE,
                const.WEBAPI_STATE_IMPORT_ERROR_KEY:
                const.WEBAPI_STATE_IMPORT_ERROR_VALUE,
                const.WEBAPI_STATE_IMPORT_SUCCESS_KEY:
                const.WEBAPI_STATE_IMPORT_SUCCESS_VALUE
            },
            const.WEBAPI_VECTOR_BUILD_STATE: {
                const.WEBAPI_STATE_NONE_KEY: const.WEBAPI_STATE_NONE_VALUE,
                const.WEBAPI_STATE_INDEX_DOING_KEY:
                const.WEBAPI_STATE_INDEX_DOING_VALUE,
                const.WEBAPI_STATE_INDEX_ERROR_KEY:
                const.WEBAPI_STATE_INDEX_ERROR_VALUE,
                const.WEBAPI_STATE_SUCCESS_KEY:
                const.WEBAPI_STATE_SUCCESS_VALUE
            }
        },
        const.ANN_MANAGE_API: {
            const.APP_NAME:
            const.ANN_MANAGE_API,
            const.APP_PORT:
            ANN_MANAGE_API_PORT,
            const.APP_SERVER:
            '{}:{}'.format(ANN_MANAGE_API_HOSTNAME, ANN_MANAGE_API_PORT),
            const.ROUTER_PARALLEL_NUM:
            PARALLEL_NUM
        },
        const.KVSTORE: {
            const.APP_NAME: const.KVSTORE,
            const.APP_PORT: KVSTORE_PORT,
            const.APP_SERVER: '{}:{}'.format(KVSTORE_HOSTNAME, KVSTORE_PORT),
            # pro版不使用变量WORK_PATH
            const.WORK_PATH: BASE_DIR + "/kvstore_online",
            "kvstore_map": KVSTORE_MAP
        },
        const.KVSTORE_OFFLINE: {
            const.APP_NAME:
            const.KVSTORE_OFFLINE,
            const.APP_PORT:
            KVSTORE_OFFLINE_PORT,
            const.APP_SERVER:
            '{}:{}'.format(KVSTORE_OFFLINE_HOSTNAME, KVSTORE_OFFLINE_PORT),
            const.WORK_PATH:
            KVSTORE_OFFLINE_DATA_PATH
        },
        const.ASYNC_TASK: {
            const.APP_NAME:
            const.ASYNC_TASK,
            const.APP_PORT:
            ASYNC_FRAMEWORK_PORT,
            const.APP_SERVER:
            '{}:{}'.format(ASYNC_FRAMEWORK_HOSTNAME, ASYNC_FRAMEWORK_PORT)
        },
        const.ANN_CONTROLLER: {
            const.APP_NAME:
            const.ANN_CONTROLLER,
            const.APP_PORT:
            ANN_CONTROLLER_PORT,
            const.APP_SERVER:
            '{}:{}'.format(ANN_CONTROLLER_HOSTNAME, ANN_CONTROLLER_PORT),
            const.ROUTER_PARALLEL_NUM:
            PARALLEL_NUM
        },
        const.SEARCH_API: {
            const.APP_NAME: const.SEARCH_API,
            const.APP_PORT: SEARCH_API_HTTP_PORT,
            const.APP_SERVER: '{}:{}'.format(BASE_SERVER_IP,
                                             SEARCH_API_HTTP_PORT)
        },
        const.ES_API: {
            const.ES_HOST: DEFAULT_ES_HOST,
            const.ES_PORT: DEFAULT_ES_PORT
        },
        const.DATA_API: {
            const.DATA_API_NAME: DATA_API_HOSTNAME,
            const.DATA_API_PORT: DATA_API_PORT
        },
    })
