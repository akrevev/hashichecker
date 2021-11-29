import logging
from lib.rss_details import RSSDetails
from lib.helpers import *
import requests
from xml.etree import ElementTree

logger = logging.getLogger('rss_checker')

class RSSChecker:

  @classmethod
  def run(cls):
    # load up cached data
    response = requests.get("https://data.sec.gov/rss?cik=1720671&count=5", headers=Helpers.headers())
    tree = ElementTree.fromstring(response.content)
    print(tree[0].text)
    # previous_rss_details = RSSDetails().from_cache()