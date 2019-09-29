# coding: utf-8
import os
import sys
import logging
import logging.handlers
import ConfigParser
from abc import ABCMeta, abstractmethod
import pymysql

def getLogger(logname="app.log"):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.TimedRotatingFileHandler(
            filename = "logs/" + logname,
            when = 'D')
    formatter = '%(asctime)s:[%(process)d]:%(levelname)s:%(message)s'
    handler.setFormatter(logging.Formatter(formatter))
    logger.addHandler(handler)
    return logger


def getConfig(configname=".env"):
    config = ConfigParser.SafeConfigParser()
    config.read("config/" + configname)
    return config


class Mysql():

    def connect(self, config):
        self.conn = pymysql.connect(
                host=config.get("database", "host"),
                port=config.getint("database", "port"),
                user=config.get("database", "user"),
                password=config.get("database", "pass"),
                db=config.get("database", "db"),
                charset="utf8",
                cursorclass=pymysql.cursors.DictCursor)
    
    def disconnect(self):
        self.conn.close

    def select(self, query, params=()):
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result

    def insert(self, query, params=(), autocommit=True):
        return self.__modify(query, params, autocommit)

    def update(self, query, params=(), autocommit=True):
        return self.__modify(query, params, autocommit)

    def delete(self, query, params=(), autocommit=True):
        return self.__modify(query, params, autocommit)

    def __modify(self, query, params=(), autocommit=True):
        cursor = self.conn.cursor()
        result = cursor.execute(query, params)
        if autocommit:
            self.commit()
        return result

    def commit(self):
        self.conn.commit()
    
    def rollback(self):
        self.conn.rollback()

    
class Command():

    __metaclass__ = ABCMeta

    def __init__(self):
        # parase sys.argv
        self.args = []
        self.opts = {}
        for i, arg in enumerate(sys.argv):
            if i == 0:
                continue
            if arg.startswith("--"):
                params = arg.split("=")
                key = params[0].replace("--", "")
                self.opts[key] = params[1]
            else:
                self.args.append(arg)
        # register config
        if ("env" in self.opts):
            self.config = getConfig(".env.{0}".format(self.opts["env"]))
        else:
            self.config = getConfig()
        # logger
        self.logger = getLogger(self.command_name() + ".log")
        # DB
        self.mysql = Mysql()

    @abstractmethod
    def command_name(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    def main(self):
        lockfile = self.command_name() + ".lock"
        try:
            if os.path.exists(lockfile):
                self.logger.warning("process is running!")
                sys.exit(1)
            else:
                f = open(lockfile, "w")
                f.close()

                self.logger.info("[START]" + self.command_name())
                self.execute()
        except Exception as e:
            self.logger.exception("%s", e)
        finally:
            os.remove(lockfile)
            self.logger.info("[END]" + self.command_name())

if __name__ == "__main__":
    print("This script has no main function!")
