from JazzItem import JazzItem
from JazzScraper import JazzScraper, DEFAULT_TIMEDELTA
import datetime
import logging
import re
import scrape_util as util
import scrapy
import unittest

class FiftyFiveBarScraper(JazzScraper):

  name = "FiftyFiveBar"

  start_date = None
  end_date = None

  SEARCH_URL = "http://www.55bar.com/cgi-bin/webdata_playinPrint.pl?cgifunction=Search"

  def __init__(self, start_date=None, end_date=None):
    """
      By default, scrapes all shows in from the past month
    """
    if end_date is None:
      end_date = datetime.datetime.today()
    if start_date is None:
      start_date = end_date - DEFAULT_TIMEDELTA
    self.start_date = start_date
    self.end_date = end_date
    start_urls = [self.url_of_datetime(start_date)]
    JazzScraper.__init__(self, start_urls)

  def items_of_response(self, response):
    ths = self.table_headers_of_response(response)
    items = []
    for i in range(0, len(ths), 2):
      date_sel = ths[i]
      artist_sel = ths[i+1]
      date_str = self.parse_date(date_sel)
      time_str = self.parse_time(date_sel) if date_str else None
      artist_str = self.parse_artist(artist_sel) if time_str else None
      if artist_str:
        dt = util.datetime_of_mdy(date_str)
        tm = util.datetime_of_ampm(time_str)
        dt += datetime.timedelta(hours=tm.hour, minutes=tm.minute)
        items.append(JazzItem(date=dt
                             ,artist=artist_str
                             ,venue=self.name))
    return items

  def parse(self, response):
    items = self.items_of_response(response)
    if items:
      yield from items
      latest_date = items[-1]['date']
      if latest_date < self.end_date:
        yield scrapy.Request(self.url_of_datetime(latest_date), callback=self.parse)

  def parse_artist(self, artist_sel):
    artist_str = None
    try:
      artist_str = util.extract_text(artist_sel.xpath(".//text()"))
    except:
      self.logger.error("Error parsing artist from selector '%s'" % artist_sel.extract())
    return artist_str

  def parse_date(self, date_sel):
    date_str = None
    try:
      date_str = date_sel.xpath("./script/text()").extract()[0].split(";", 1)[0]
      date_str = re.search(util.MDY_RX, date_str).group(0)
    except:
      self.logger.error("Error parsing date from selector '%s'" % date_sel.extract())
    return date_str

  def parse_time(self, date_sel):
    time_str = None
    try:
      time_str = date_sel.xpath(".//font/text()").extract()[0].split(" - ", 1)[-1]
    except:
      self.logger.error("Error parsing showtime from selector '%s'" % date_sel.extract())
    return time_str

  def table_headers_of_response(self, response):
    return response.xpath("//th[@scope='row']")

  def url_of_datetime(self, dt):
    return self.SEARCH_URL + "&GigDate=%3E%3D" + util.mdy_of_datetime(dt)


## -----------------------------------------------------------------------------
class FiftyFiveBarScraperTest(unittest.TestCase):

  def setUp(self):
    self.scraper = FiftyFiveBarScraper()
    self.sample_url = "http://55bar.com"
    self.response = util.response_of_file("test/FiftyFiveBar.html", self.sample_url)
    ths = self.scraper.table_headers_of_response(self.response)
    self.date_sel = ths[0]
    self.artist_sel = ths[1]

  def test_start_date(self):
    """
      `start_date` should be defined after `__init__`
    """
    self.assertIsNotNone(self.scraper.start_date)

  def test_end_date(self):
    """
      `end_date` should be defined and later in time than `start_date`
    """
    self.assertIsNotNone(self.scraper.end_date)
    self.assertLess(self.scraper.start_date, self.scraper.end_date)

  def test_start_urls(self):
    """
      `start_urls` should be defined an non-empty and all target 55bar
    """
    self.assertIsNotNone(self.scraper.start_urls)
    self.assertGreater(len(self.scraper.start_urls), 0)
    for url in self.scraper.start_urls:
      self.assertTrue(url.startswith(self.scraper.SEARCH_URL))

  def test_items_of_response(self):
    """
    """
    items = self.scraper.items_of_response(self.response)
    self.assertEqual(len(items), 62)
    i0 = items[0]
    i9 = items[9]
    for item in [i0, i9]:
      self.assertEqual(item['venue'], "FiftyFiveBar")
      self.assertEqual(item['date'].year, 2015)
    self.assertTrue(i0['artist'].startswith("Hope Debates"))
    self.assertTrue(i9['artist'].startswith("Mike Stern"))

  def test_parse(self):
    """
      Run `parse` on an example webpage
    """
    self.scraper.end_date = datetime.datetime(year=1800, month=11, day=2)
    items = list(self.scraper.parse(self.response))
    self.assertEqual(len(items), 62)
    for item in items:
      self.assertTrue(isinstance(item, JazzItem))

  #def test_parse_end2end(self):
  #  """
  #    Run `parse` on a new webpage; this should run without errors
  #  """
  #  # TODO
  #  pass

  def test_parse_artist(self):
    expected = "Hope Debates Hope Debates(Voice), Brad Shepik(Guitar), Scott Colberg(Bass), Jon Graboff(Pedal Steel), Diego Voglino(Drums)"
    self.assertEqual(self.scraper.parse_artist(self.artist_sel), expected)

  def test_parse_date(self):
    self.assertEqual(self.scraper.parse_date(self.date_sel), "10/17/15")

  def test_parse_time(self):
    self.assertEqual(self.scraper.parse_time(self.date_sel), "6pm")

  def test_url_of_datetime(self):
    year = 2005
    month = 12
    day = 1
    dt = datetime.datetime(year=year, month=month, day=day)
    url = self.scraper.url_of_datetime(dt)
    self.assertIsNotNone(url)
    self.assertTrue(url.startswith(self.scraper.SEARCH_URL))
    self.assertTrue(url.endswith(util.mdy_of_datetime(dt)))

