'''
extrator_html: 根据每行字数的分布对网页中的正文进行提取
'''
# -- encoding:utf-8 --
import pymongo
from bs4 import BeautifulSoup, Comment
import json
import re
import sys
import traceback
import logging
import loggingconfig

# 导入自定义模块
sys.path.append('/Users/likai/Documents/Learningbydoing/python/webscraping/')

# 定义logging
logger = loggingconfig.logger
DBUG = 0

class Extractorhtml():
    __docs = None
    mainbody = []

    def __init__(self, **kwargs):
        if kwargs.get('file') is not None:
            logger.info('读取：%s', file)
            with open(kwargs['file'], 'r') as fn:
                self.__docs = json.load(fn)
            logger.info('文件读入成功')
        else:
            try:
                logger.info('读取mongo数据库')
                docs = self.__read_mongo()
            except Exception:
                logger.error('数据读入错误', exc_info=True)
            else:
                logger.info('数据库读入正确')
        self.extract_html()
        self.__save_to_json()

    def __read_mongo(self):
        try:
            db = pymongo.MongoClient(host='127.0.0.1',
                                     port=27017)
            docs = db.search_baidu.html.find()
        except Exception:
            logger.error('Fail to get docs from mongo', exc_info=True)
        else:
            logger.info('finished get docs from mongo')
        return docs

    def extract_html(self):
        if DBUG:
            logger.debug(type(self.__docs))
        for doc in self.__docs:
            mainbody = self.extract_main_body_text(doc['text'])
            if mainbody:
                self.mainbody.append(mainbody)
        logger.info('所有documents提取成功')

    def extract_main_body_text(self, doc):
        info = dict()
        article = []
        try:
            soup = BeautifulSoup(doc, 'lxml')
            if soup.title is not None:
                info['title'] = soup.title.get_text(strip=True)
            tag_p = soup.find_all('p')
            if tag_p:
                for p in tag_p:
                    article.append(p.get_text(strip=True))
                info.update(article=article.copy())
        except Exception:
            if DBUG:
                logger.debug(traceback.format_exc)
        else:
            if info:
                return info.copy()
            else:
                return None

    def __save_to_json(self):
        with open('data.json', 'w+') as fn:
            json.dump(self.mainbody, fn)
        logger.info('json文件写入成功')


if __name__ == '__main__':
    file = '/Users/likai/Documents/我的大论文/DataAnalysis/database/html_json.txt'
    test = Extractorhtml(file=file)
