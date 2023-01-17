"""
common constants
"""

import os


class _const(object):
    """
    check constant
    """

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise Exception("Can't rebind const (%s)" % name)
        if not name.isupper():
            raise Exception("Const must be upper.")
        self.__dict__[name] = value


const = _const()

### common args definition
const.REST_CODE = "errCode"
const.REST_MSG = "errMsg"
const.REST_SUCCESS_CODE = 0
const.REST_SUCCESS_MSG = "Success"
const.REST_RESULT = "result"
const.REST_UNKNOWN_CODE = 400000
const.REST_UNKNOWN_ERROR = "ServerInternalError"
const.BASE_DIR = 'base_dir'
const.DATA_PATH = "data_path"
const.WORK_PATH = 'work_path'
const.HEALTHZ_URL = "/healthz"
const.DATABASE_DEPLOYMENT_TYPE = "database_deployment_type"
const.ELASTICSEARCH = "elasticsearch"
# es create index name format
const.ELASTICSEARCH_INDEX_NAME = "baizhong_ann_{}"

### db
const.DB_CONFIG_ITEM = 'databases'
const.DEFAULT_DB_KEY = 'default'
const.DBHOST_KEY = 'host'
const.DBPORT_KEY = 'port'
const.DBUSER_KEY = 'user'
const.DBPWD_KEY = 'pwd'
const.DBNAME_KEY = 'name'

# apps
const.APP_CONFIG_ITEM = 'apps'
const.APP_NAME = "app_name"
const.APP_PORT = 'app_port'
const.APP_SERVER = 'app_server'
const.ROUTER_PARALLEL_NUM = 'router_parallel_num'
# logs
const.LOG_KEY = "log"
const.LOG_DIR = 'log_dir'
const.LOG_MIN_LEVEL = 'log_min_level'
const.LOG_RETENTION_DAYS = 'log_retention_days'
const.LOG_IS_CONSOLE = 'log_is_console'

# web-api
const.WEB_API = "web-api"
const.WEBAPI_PROJECT_STATE = "project_state"
const.WEBAPI_STATE_NONE_KEY = 0
const.WEBAPI_STATE_NEW_KEY = 1
const.WEBAPI_STATE_IMPORTING_KEY = 2
const.WEBAPI_STATE_IMPORT_ERROR_KEY = -2
const.WEBAPI_STATE_IMPORT_SUCCESS_KEY = 3
const.WEBAPI_STATE_INDEX_DOING_KEY = 4
const.WEBAPI_STATE_INDEX_ERROR_KEY = -4
const.WEBAPI_STATE_SUCCESS_KEY = 5
const.WEBAPI_DOC_IMPORT_STATE = "doc_import_state"
const.WEBAPI_VECTOR_BUILD_STATE = "vector_build_state"
const.WEBAPI_STATE_NONE_VALUE = '暂无导入状态'
const.WEBAPI_STATE_NEW_VALUE = '已创建'
const.WEBAPI_STATE_IMPORTING_VALUE = "数据导入中"
const.WEBAPI_STATE_IMPORT_ERROR_VALUE = "导入失败"
const.WEBAPI_STATE_IMPORT_SUCCESS_VALUE = "数据导入成功"
const.WEBAPI_STATE_INDEX_DOING_VALUE = "向量建库中"
const.WEBAPI_STATE_INDEX_ERROR_VALUE = "向量建库失败"
const.WEBAPI_STATE_SUCCESS_VALUE = "已完成，可检索"
const.WEBAPI_PROJECT_SCHEMA_DATATYPE = "type"
const.WEBAPI_PROJECT_SCHEMA_SHORTINDEX = "shortindex"
const.WEBAPI_PROJECT_SCHEMA_LONGINDEX = "longindex"
const.WEBAPI_PROJECT_SCHEMA__ID = "_id"
const.WEBAPI_PROJECT_NAME_RE = r'^[\u4E00-\u9FA5A-Za-z0-9_]+$'

# SERVER OF SEARCH-API
# search-api
const.SEARCH_API = "search-api"
const.SEARCH_API_RESOURCE_CHECK_TIMESPAN_SECOND = 2
## name of pipeline that will work via pipeline as the name as
### `create_$NAME_pipeline` for search-api, eg: create_common_search_pipeline
### `create_$NAME_recall_and_faiss_only_pipeline` for recall-api
### default value is "common"
const.SEARCH_API_PIPELINE_NAME = "pro_common"
## ip:port lists of downstream services
### eg: const.SEARCH_API_IP_LIST_RECALL = ["127.0.0.1:6666"]
const.SEARCH_API_IP_LIST_RECALL = ["query-emb:8099"]
const.SEARCH_API_IP_LIST_PARA_EMB = ["para-emb:8374"]
const.SEARCH_API_IP_LIST_FAISS = ["ann-controller:8106"]
const.SEARCH_API_IP_LIST_RANK = ["rank:8001"]
const.SEARCH_API_IP_LIST_MRC = ["mrc:8107"]
const.SEARCH_API_APP_URI_SEARCH = r'/baizhong/search-api'
const.SEARCH_API_APP_URI_CUT = r'/baizhong/cut-api'
const.SEARCH_API_APP_URI_QUERY_EMB = r'/baizhong/query-emb'
const.SEARCH_API_APP_URI_RECALL = r'/baizhong/recall'
const.SEARCH_API_APP_URI_RANK = r'/baizhong/rank'
const.SEARCH_API_APP_URI_DOC = r'/baizhong/doc'
## api uri of downstream service after host:port
const.SEARCH_API_URI_DEFAULT = '/'
## max request times of downstream service
### should greater than 1
const.SEARCH_API_MAX_REQUEST_TIMES_DEFAULT = 1
const.SEARCH_API_MAX_REQUEST_TIMES_RECALL = 2
const.SEARCH_API_MAX_REQUEST_TIMES_FAISS = 2
const.SEARCH_API_MAX_REQUEST_TIMES_RANK = 1
const.SEARCH_API_MAX_REQUEST_TIMES_DOC = 2
const.SEARCH_API_MAX_REQUEST_TIMES_MRC = 2
const.SEARCH_API_MAX_REQUEST_TIMES_PARA_EMB = 2
## request timeout(second) of downstream service
### should greater than 1
const.SEARCH_API_TIMEOUT_SEC_DEFAULT = 1
const.SEARCH_API_TIMEOUT_SEC_RECALL = 1
const.SEARCH_API_TIMEOUT_SEC_FAISS = 2
const.SEARCH_API_TIMEOUT_SEC_RANK = 3
const.SEARCH_API_TIMEOUT_SEC_DOC = 1
const.SEARCH_API_TIMEOUT_SEC_MRC = 3
const.SEARCH_API_TIMEOUT_SEC_PARA_EMB = 1
## guarantee result:
### if rank failed, return the same sequence as faiss/recall
### and fill up zero as the rank result
const.SEARCH_API_GUARANTEE_RANK_ENABLE = True
### if doc failed, 'doc' in result will be filled with 'para'
const.SEARCH_API_GUARANTEE_DOC_ENABLE = True
## cache config of search-api
### type of cache: none, local, remote
const.SEARCH_API_CACHE_TYPE = 'none'
### search-api local cache: a lru-cache
#### maxsize of local cache items, None means unlimited
const.SEARCH_API_LOCAL_CACHE_MAX_SIZE = 128
## search-api remote cache: remote
const.SEARCH_API_REMOTE_CACHE_HOST = "127.0.0.1"
const.SEARCH_API_REMOTE_CACHE_PORT = "9527"
const.SEARCH_API_REMOTE_CACHE_PASSWD = "abcdefg"
const.SEARCH_API_REMOTE_CACHE_EXPIRE = 86400
const.SEARCH_API_REMOTE_CACHE_KEY_PREFIX = "remote_cache#"
# cut-api
const.SEARCH_API_ENABLE_CUT_APP = True
# sub-apps
const.SEARCH_API_IS_GATEWAY_APP = False
const.SEARCH_API_GATEWAY_URI_RANK = r'/baizhong/model-api/rank'
const.SEARCH_API_GATEWAY_URI_QUERY_EMB = r'/baizhong/model-api/query-emb'
const.SEARCH_API_GATEWAY_URI_PARA_EMB = r'/baizhong/model-api/para-emb'
# rank-api
const.SEARCH_API_ENABLE_RANK_APP = False
const.SEARCH_API_RANK_APP_MAX_SIZE = 200
# recall-api
const.SEARCH_API_ENABLE_RECALL_APP = False
const.SEARCH_API_RECALL_APP_MAX_SIZE = 300
# doc-api
const.SEARCH_API_ENABLE_DOC_APP = False
const.DOC_APP_ARGUMENT_MAX_SIZE = 300
# query-embedding-api
const.SEARCH_API_ENABLE_QUERY_EMB_APP = False
# para-embedding-api
const.SEARCH_API_ENABLE_PARA_EMB_APP = False
# api auth module
const.SEARCH_API_ENABLE_AUTH = True
const.SEARCH_API_AUTH_NO_EXPLICIT_FAIL_AS_PASS = True
const.SEARCH_API_AUTH_GUARD_TYPE = "DefaultAuthGuard"
const.SEARCH_API_AUTH_GUARD_RANK = "rank"
const.SEARCH_API_AUTH_GUARD_QUERY_EMBEDDING = "query_emb"
const.SEARCH_API_AUTH_GUARD_PARA_EMBEDDING = "para_emb"
## kv-cache flow control and auth
const.SEARCH_API_AUTH_CACHE_TYPE = "none"
const.SEARCH_API_AUTH_CACHE_HOST = "127.0.0.1"
const.SEARCH_API_AUTH_CACHE_PORT = 6379
const.SEARCH_API_AUTH_CACHE_PASSWD = "abcdefg"
const.SEARCH_API_AUTH_FLOW_CTRL_PREFIX = "flowctrl"
const.SEARCH_API_AUTH_FLOW_CTRL_MAX_QPS_PER_USER = 1
const.SEARCH_API_AUTH_SEC_FLOW_CTRL_KEY_EXPIRE = 10

# ann
const.ANN_MANAGE_API = "ann_manange_api"
const.ANN_DELETE = '/baizhong/ann-manage-api/ann/delete'
const.ANN_DEL_DATA = "/baizhong/ann-manage-api/ann/del"
const.ANN_BUILD_INDEX = "/baizhong/ann-manage-api/ann/build"

### re check
# 匹配 yyyy-MM-dd HH:mm:ss|yyyy-MM-dd
const.DATE_FORMAT_VALID = r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2})|(\d{4}-\d{1,2}-\d{1,2})"
const.REPX_UNDERLINE = r"(_)+"
const.DATE_COMMON_FORMAT = "%Y-%m-%d %H:%M:%S"

# app url
const.WEBAPI_PROJECT_ADD_URL = "/baizhong/web-api/project/add"
const.WEBAPI_PROJECT_GET_URL = "/baizhong/web-api/project/get"
const.WEBAPI_PROJECT_DELETE_URL = "/baizhong/web-api/project/delete"
const.WEBAPI_PROJECT_STATE_GET_URL = "/baizhong/web-api/project-state/get"
const.WEBAPI_PROJECT_STATE_UPDATE_URL = "/baizhong/web-api/project-state/update"
const.WEBAPI_PROJECT_FILENUM_UPDATE_URL = "/baizhong/web-api/project-filenum/update"
const.WEBAPI_PROJECT_INFO_UPDATE_URL = "/aurora/web-api/project/update"

const.WEBAPI_PROJECT_LIST_URL = "/baizhong/web-api/project/list"
const.WEBAPI_PROJECT_COUNT_URL = "/baizhong/web-api/project/count"
const.WEBAPI_PROJECT_SCHEMA_GET_URL = "/baizhong/web-api/project-schema/get"
const.WEBAPI_PROJECT_SCHEMA_CREATE_URL = "/baizhong/web-api/project-schema/create"
const.WEBAPI_PROJECT_SCHEMA_UPDATE_URL = "/baizhong/web-api/project-schema/update"
const.WEBAPI_DOC_FILE_IMPORT_URL = "/baizhong/web-api/doc-file/import"
const.WEBAPI_DOC_FILE_IMPORT_V2_URL = "/baizhong/build/v1/docfile/import"
const.WEBAPI_DOC_FILE_DATA_IMPORT_URL = "/baizhong/web-api/doc-file/data_import"
const.WEBAPI_DOC_FILE_BUILD_INDEX_URL = "/baizhong/web-api/doc-file/build_index"
const.WEBAPI_DOC_FILE_DELETE_URL = "/baizhong/web-api/doc-file/delete"
const.WEBAPI_DOC_FILE_UPLOAD_URL = "/baizhong/web-api/doc-file/upload"

# v2版本，es部署时调用
const.WEBAPI_V2_PROJECT_ADD_URL = "/baizhong/web-api/v2/project/add"
const.WEBAPI_V2_PROJECT_UPDATE_URL = "/baizhong/web-api/v2/project/update"
const.WEBAPI_V2_PROJECT_GET_URL = "/baizhong/web-api/v2/project/get"
const.WEBAPI_V2_PROJECT_COUNT_URL = "/baizhong/web-api/v2/project/count"
const.WEBAPI_V2_PROJECT_LIST_URL = "/baizhong/web-api/v2/project/list"
const.WEBAPI_V2_PROJECT_FILENUM_UPDATE_URL = "/baizhong/web-api/v2/project-filenum/update"
const.WEBAPI_V2_PROJECT_DELETE_URL = "/baizhong/web-api/v2/project/delete"
const.WEBAPI_V2_PROJECT_SCHEMA_CREATE_URL = "/baizhong/web-api/v2/project-schema/create"
const.WEBAPI_V2_PROJECT_SCHEMA_UPDATE_URL = "/baizhong/web-api/v2/project-schema/update"
const.WEBAPI_V2_PROJECT_SCHEMA_GET_URL = "/baizhong/web-api/v2/project-schema/get"

#通用降级接口
const.WEBAPI_SEARCH_GET_META_URL = "/baizhong/web-api/search/get_meta"
const.WEBAPI_SEARCH_SET_META_URL = "/baizhong/web-api/search/set_meta"
const.WEBAPI_SEARCH_SET_GLOBAL_URL = "/baizhong/web-api/search/set_global"
const.WEBAPI_SEARCH_GET_GLOBAL_URL = "/baizhong/web-api/search/get_global"
const.WEBAPI_SEARCH_SWAP_SPACE_URL = "/baizhong/web-api/search/swap_space"
const.WEBAPI_SEARCH_DROP_SPACE_URL = "/baizhong/web-api/search/drop_space"
const.WEBAPI_SEARCH_SET_SKIP_DOC_URL = "/baizhong/web-api/search/set_skip_doc"
const.WEBAPI_SEARCH_SET_SKIP_RANK_URL = "/baizhong/web-api/search/set_skip_rank"
const.WEBAPI_SEARCH_SET_DB_TOP_URL = "/baizhong/web-api/search/set_db_top"
const.WEBAPI_SEARCH_SET_RANK_SIZE_URL = "/baizhong/web-api/search/set_rank_size"
const.WEBAPI_SEARCH_SET_RANK_TOP_URL = "/baizhong/web-api/search/set_rank_top"
const.WEBAPI_ALERT_URL = "/baizhong/web-api/alert"

### kvstore
const.KVSTORE = 'kvstore'
const.KVSTORE_OFFLINE = 'kvstore_offline'
const.KVSTORE_GET = "/v1/space/{}/_get"
const.KVSTORE_PUT = "/v1/space/{}/_put"
const.KVSTORE_DEL = "/v1/space/{}/_del"
const.KVSTORE_CREATE = "/v1/space/{}/_create"
const.KVSTORE_REMOVE = "/v1/space/{}/_delete"

###  async
const.ASYNC_TASK = 'async_task'
const.ASYNC_TASK_SERVER = "http://localhost:8990"
const.TASK_APPLY_URI = "/baizhong/async-task/add"
const.ASYNC_QUERY_URI = "/baizhong/async-task/query"

const.PREDICT_DATALOADER = "para_to_vector_es"
const.PREDICT_TABLE = "t_bns_a10_article_v5"
const.PREDICT_MAX_WORKS = 10
const.PREDICT_BATCH_SIZE = 32

const.PREDICT_MYSQL_HOST = 'mysql-offline-mysql-ha-leader'
const.PREDICT_MYSQL_USER = 'root'
const.PREDICT_MYSQL_PAWD = 'root'
const.PREDICT_MYSQL_PORT = 3306
const.PREDICT_MYSQL_DB   = 'aurora'

const.ANN_CONTROLLER = "ann_contoller"
const.ANN_CONTROLLER_UPDATE_MAP = "/update"

### ES
const.ES_API = 'es_api'
const.ES_HOST = 'es_host'
const.ES_PORT = 'es_port'
const.ES_DEFAULT_CONFIG = 'es_default_config'

### data-api
const.DATA_API = 'data_api'
const.DATA_API_NAME = 'data_api_host'
const.DATA_API_PORT = 'data_api_port'


def get_env_or_config(name, default="", ignore="", env_first=True):
    global const
    if env_first:
        if name in os.environ:
            _env = str(os.environ.get(name, default)).strip()
            if _env != ignore:
                return _env
        return str(getattr(const, name, default)).strip()
    else:
        _cfg = str(getattr(const, name, default)).strip()
        if _cfg != ignore:
            return _cfg
        return str(os.environ.get(name, default)).strip()


def get_env_or_config_bool(name, default=False, env_first=True):
    if type(default) is not bool:
        raise Exception("Default value(%s) should be a bool." % str(default))
    _val = get_env_or_config(name, '', '', env_first).lower()
    if _val == 'true':
        return True
    elif _val == 'false':
        return False
    else:
        return default


def get_env_or_config_int(name, default=0, env_first=True):
    if type(default) is not int:
        raise Exception("Default value(%s) should be a integer." %
                        str(default))
    _val = get_env_or_config(name, '', '', env_first)
    if _val.isdigit() == True:
        return int(_val)
    elif len(_val) == 0:
        return default
    else:
        raise Exception("Value of %s is %s, which is not an integer." %
                        (name, str(_val)))
