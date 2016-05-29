import re
import datetime
import logging
import scrape_util as util
from JazzScraper import JazzScraper, DEFAULT_TIMEDELTA
from JazzItem import JazzItem

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
    ths = response.xpath("//th[@scope='row']")
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

  def url_of_datetime(self, dt):
    return self.SEARCH_URL + "&GigDate=%3E%3D" + util.mdy_of_datetime(dt)

