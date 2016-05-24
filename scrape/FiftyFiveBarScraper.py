import re
import datetime
import scrape_util as util
from JazzScraper import JazzScraper, DEFAULT_TIMEDELTA
from JazzItem import JazzItem

## TODO use a logger

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

  def parse(self, response):
    items = self.items_of_response(response)
    yield from items
    latest_date = items[-1]['date']
    if latest_date < self.end_date:
      yield scrapy.Request(self.url_of_datetime(latest_date), callback=self.parse)

  def items_of_response(self, response):
    ths = response.xpath("//th[@scope='row']")
    items = []
    for i in range(0, len(ths), 2):
      date_sel = ths[i]
      artist_sel = ths[i+1]
      date_str = None
      time_str = None
      artist_str = None
      try:
        date_str = date_sel.xpath("./script/text()").extract()[0].split(";", 1)[0]
        date_str = re.search(util.MDY_RX, date_str).group(0)
      except:
        print("Error parsing date from selector '%s'" % date_sel.extract())
        date_str = None
      try:
        time_str = date_sel.xpath(".//font/text()").extract()[0].split(" - ", 1)[-1]
      except:
        print("Error parsing showtime from selector '%s'" % date_sel.extract())
        time_str = None
      try:
        artist_str = util.extract_text(artist_sel.xpath(".//text()"))
      except:
        print("Error parsing artist from selector '%s'" % artist_sel.extract())
      if date_str and time_str and artist_str:
        dt = util.datetime_of_mdy(date_str)
        tm = util.datetime_of_ampm(time_str)
        dt += datetime.timedelta(hours=tm.hour, minutes=tm.minute)
        items.append(JazzItem(date=dt
                             ,artist=artist_str
                             ,venue=self.name))
    return items

  def url_of_datetime(self, dt):
    return self.SEARCH_URL + "&GigDate=%3E%3D" + util.mdy_of_datetime(dt)

