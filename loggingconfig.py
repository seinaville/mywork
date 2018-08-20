'''
logging 配置文件
'''
import logging

logger = logging.getLogger('Extractorhtml')
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(lineno)d : %(asctime)s - %(name)s - '
                              '%(levelname)s - %(message)s')

# FileHandler
file_handler = logging.FileHandler(filename = 'html_log.txt',
                                   mode = 'w')
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# StreamHandler
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


