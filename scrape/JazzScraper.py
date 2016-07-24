import datetime
import scrapy
import unittest


DEFAULT_TIMEDELTA = datetime.timedelta(days=30)

class JazzScraper(scrapy.Spider):
  """
    Parent class for Jazz site scrapers
  """

  download_delay = 0.5 # seconds, time to wait between Requests
  name = None # Every Scrapy spider needs a name

  def __init__(self, start_urls):
    """
      start_urls = URLs to begin scraping from.
                   The `parse` method is called with responses from each.
    """
    self.start_urls = start_urls

  def parse(self, response):
    """
        Scrape a response from a URL in `self.start_urls`.
        Expected behavior:
        - parse data from the response, or spawn requests to URLs scraped from the response
        - yield a sequence of JazzItem objects
    """
    raise NotImplementedError()


## -----------------------------------------------------------------------------
class JazzScraperTest(unittest.TestCase):
  def setUp(self):
    self.scraper = JazzScraper([])

  def test_download_delay(self):
    """
      Expect (at least) a non-zero download delay
    """
    self.assertGreater(self.scraper.download_delay, 0)

  def test_parse(self):
    """
      Parse should be defined, but not implemented for JazzScraper
    """
    response = scrapy.http.Response("http://www.google.com")
    self.assertRaises(NotImplementedError, self.scraper.parse, [response])

