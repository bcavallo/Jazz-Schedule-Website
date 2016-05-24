import datetime
import scrapy


DEFAULT_TIMEDELTA = datetime.timedelta(days=30)

class JazzScraper(scrapy.Spider):

  name = None # Every Scrapy spider needs a name

  download_delay = 0.5 # seconds, time to wait between Requests

  def __init__(self, start_urls):
    self.start_urls = start_urls

  def parse(self, response):
    """
        TODO document
    """
    raise NotImplementedError()

