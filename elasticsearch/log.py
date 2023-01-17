#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log utils
"""
import os
import sys
import re
import logging
import logging.handlers
import inspect
import time
from multiprocessing import Lock
import errors as errors

INFO = logging.INFO
DEBUG = logging.DEBUG
ERROR = logging.ERROR
WARNING = logging.WARNING
LOG_NAME = 'aurora'


class MultiTimeRotatingFileHandler(logging.handlers.TimedRotatingFileHandler):
    """
    TimeRotatingFileHandler That Support Multiple Processes
    """

    def __init__(self,
                 filename,
                 when='h',
                 interval=1,
                 backupCount=0,
                 encoding=None,
                 delay=False,
                 utc=False):
        logging.handlers.TimedRotatingFileHandler.__init__(
            self, filename, when, interval, backupCount, encoding, delay, utc)

    def doRollover(self):
        """
        do a rollover; in this case, a date/time stamp is appended to the filename
        when the rollover happens.  However, you want the file to be named for the
        start of the interval, not the current time.  If there is a backup count,
        then we have to get a list of matching filenames, sort them and remove
        the one with the oldest suffix.

        Override,   1. if dfn not exist then do rename
                    2. _open with "a" model
        """
        if self.stream:
            self.stream.close()
            self.stream = None

        currentTime = int(time.time())
        dstNow = time.localtime(currentTime)[-1]
        t = self.rolloverAt - self.interval
        if self.utc:
            timeTuple = time.gmtime(t)
        else:
            timeTuple = time.localtime(t)
            dstThen = timeTuple[-1]
            if dstNow != dstThen:
                if dstNow:
                    addend = 3600
                else:
                    addend = -3600
                timeTuple = time.localtime(t + addend)
        dfn = self.baseFilename + "." + time.strftime(self.suffix, timeTuple)

        if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
            lock = Lock()
            lock.acquire()
            if not os.path.exists(dfn) and os.path.exists(self.baseFilename):
                os.rename(self.baseFilename, dfn)
            lock.release()

        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)
        if not self.delay:
            self.mode = "a"
            self.stream = self._open()
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval

        if (self.when == 'MIDNIGHT'
                or self.when.startswith('W')) and not self.utc:
            dstAtRollover = time.localtime(newRolloverAt)[-1]
            if dstNow != dstAtRollover:
                if not dstNow:
                    addend = -3600
                else:
                    addend = 3600
                newRolloverAt += addend
        self.rolloverAt = newRolloverAt


class Log(object):
    """ LOG Module """
    __instance = None

    def __init__(self,
                 log_path='.',
                 log_name=None,
                 min_level='debug',
                 days=7,
                 is_console=True,
                 log_hostname='localhost'):
        self.__logger = logging.getLogger(LOG_NAME)
        setattr(self.__logger, 'notice', getattr(self.__logger, 'warning'))
        setattr(self.__logger, 'initialize', getattr(Log, 'initialize'))
        try:
            if not os.path.exists(log_path):
                os.mkdir(log_path)
        except Exception as oe:
            print("log dir create failed: %s because %s" % (log_path, str(oe)))
            if os.path.isdir(log_path):
                print("log dir has been created in other program: %s" % log_path)
        if min_level == 'debug':
            self.__logger.setLevel(DEBUG)
        elif min_level == 'info':
            self.__logger.setLevel(INFO)
        elif min_level == 'error':
            self.__logger.setLevel(ERROR)
        elif min_level == 'notice':
            self.__logger.setLevel(WARNING)
        else:
            raise errors.ArgsInvalidError(
                'log level is not in [debug, info, error, notice]\n')

        if isinstance(days, int):
            if days <= 0:
                raise errors.ArgsInvalidError(
                    'days must be a positive integer')
        else:
            raise errors.ArgsInvalidError('days must be a positive integer')

        if not isinstance(is_console, bool):
            raise errors.ArgsInvalidError('is_console must be a bool')

        if min_level == 'debug':
            self.__formatter = logging.Formatter(
                "%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
                datefmt='%m-%d %H:%M:%S')
        else:
            self.__formatter = logging.Formatter(
                "%(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s",
                datefmt='%m-%d %H:%M:%S')

        if log_name is None:
            self.__console_handle = logging.StreamHandler(sys.stderr)
            self.__console_handle.setFormatter(self.__formatter)
            self.__logger.addHandler(self.__console_handle)
        elif not isinstance(log_name, str):
            raise errors.ArgsInvalidError('log_name must be a string')
        else:
            log_name = log_name + log_hostname
            # 先置空现在已有的console handler
            self.__logger.handlers = []

            # 错误日志分隔
            info_filter = logging.Filter()
            info_filter.filter = lambda record: record.levelno < logging.ERROR
            error_filter = logging.Filter()
            error_filter.filter = lambda record: record.levelno == logging.ERROR

            info_file_handler = MultiTimeRotatingFileHandler(
                '{}/{}.log'.format(log_path, log_name),
                when="midnight",
                interval=1,
                backupCount=days)
            info_file_handler.suffix = '%Y-%m-%d.log'
            info_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")
            info_file_handler.setFormatter(self.__formatter)

            error_file_handler = MultiTimeRotatingFileHandler(
                '{}/{}.error'.format(log_path, log_name),
                when="midnight",
                interval=1,
                backupCount=days)
            error_file_handler.suffix = '%Y-%m-%d.wf'
            error_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.wf$")
            error_file_handler.setFormatter(self.__formatter)

            info_file_handler.addFilter(info_filter)
            error_file_handler.addFilter(error_filter)

            self.__logger.addHandler(info_file_handler)
            self.__logger.addHandler(error_file_handler)

            if is_console:
                self.__console_handle = logging.StreamHandler(sys.stderr)
                self.__console_handle.setFormatter(self.__formatter)
                self.__logger.addHandler(self.__console_handle)

    @classmethod
    def get_log(cls, *args, **kwargs):
        """ get log instance"""
        if (not cls.__instance) or (len(args) > 0 or len(kwargs) > 0):
            cls.__instance = Log(*args, **kwargs)
        return cls.__instance.__logger

    @classmethod
    def initialize(cls, *args, **kwargs):
        """ initialize post - __init__"""
        cls.__instance = Log(*args, **kwargs)
        return cls.__instance.__logger


log = Log.get_log()

if __name__ == "__main__":
    a = time.time()
    log.info('this is a info')
    print(time.time() - a)
    a = time.time()
    log.debug('this is a debug')
    print(time.time() - a)
    a = time.time()
    log.notice('this is a notice')
    print(time.time() - a)
    a = time.time()
    log.error('this is a error')
    print(time.time() - a)
