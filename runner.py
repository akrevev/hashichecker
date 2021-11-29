# -*- coding: utf-8 -*-
import logging
from pythonjsonlogger import jsonlogger
from lib.ipo_checker import IPOChecker
from lib.rss_checker import RSSChecker
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    # IPOChecker.run()
    RSSChecker.run()