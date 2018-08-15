'''
extrator_html: 根据每行字数的分布对网页中的正文进行提取
'''
# -- encoding:utf-8 --
import pymongo
from bs4 import BeautifulSoup, Comment
import json
import re
import sys
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
            if len(mainbody) != 0 :
                self.mainbody.append(mainbody)
        logger.info('所有documents提取成功')

    def extract_main_body_text(self, doc, threshold=50):
        threshold = threshold
        soup = BeautifulSoup(doc, 'lxml')
        # 清除页面中的评论、javascript和style
        comments = soup.find_all(text=lambda text:
                                 isinstance(text, Comment))
        [comment.extract() for comment in comments]
        [script.extract() for script in soup.find_all('script')]
        [style.extract() for style in soup.find_all('style')]
        # 将网页中的tag全部替换为''
        regsub = re.compile("<[^*>]*>")
        ls = regsub.sub('', soup.prettify()).split('\n')
        try:
            lstolen = [len(x) for x in ls]  # 计算每行字符长度
            starindex = 0  # 正文开始的行数
            endindex = 0  # 正文结束的行数
            maxindex = lstolen.index(max(lstolen))
            if DBUG:
                logger.debug('在第%d行存在最大的行字数：%d', maxindex + 1,
                         max(lstolen))
            for i, v in enumerate(lstolen[:maxindex - 3]):
                if (v > threshold and lstolen[i + 1] > 10 and
                        lstolen[i + 2] > 10 and lstolen[i + 3] > 10):
                    startindex = i
                    break
            for i, v in enumerate(lstolen[maxindex:len(lstolen) - 3]):
                if v < threshold and lstolen[maxindex + i + 1] < 10 and lstolen[maxindex + i + 2] < 10 and lstolen[maxindex + i + 3] < 10:
                    endindex = i
                    break
        except Exception:
            logger.error('提取开始或结束行错误', exc_info=True)
        else:
            mainbody = [x for x in ls[starindex:endindex + 1] if
                        len(x.strip()) > 0]
            if DBUG:
                logger.debug('mainbody\'s length is : %d', len(mainbody))
        return mainbody

    def __save_to_json(self):
        with open('data.json', 'w+') as fn:
            json.dump(self.mainbody, fn)
        logger.info('json文件写入成功')


if __name__ == '__main__':
    file = '/Users/likai/Documents/我的大论文/DataAnalysis/database/html_json.txt'
    test = Extractorhtml(file=file)
