import datetime
import os
import scrapy
import unittest

"""
  Constants and helper functions for scrapers
"""


MDY_RX = r'[0-9]+/[0-9]+/[0-9]+'

def datetime_of_ampm(ampm):
  """
    Parse a string like '7pm' to a datetime
  """
  if " " in ampm:
    return datetime.datetime.strptime(ampm, "%I %M%p")
  else:
    return datetime.datetime.strptime(ampm, "%I%p")

def datetime_of_mdy(date_str_raw):
  """
    Build a datetime from a MONTH/DAY/YEAR string
  """
  strs = date_str_raw.split("/")
  if len(strs) != 3:
    return None
  m = strs[0].zfill(2)
  d = strs[1].zfill(2)
  y = strs[2] if len(strs[2]) == 4 else ("20%s" % strs[2])
  date_str = "/".join([m,d,y])
  return datetime.datetime.strptime(date_str, "%m/%d/%Y")

def extract_text(sel):
  """
    Concat and return all non-whitespace text from Selector `sel`
  """
  return " ".join((x for x in (x.strip() for x in sel.extract()) if x))

def mdy_of_datetime(dt):
  """
    Get a MONTH/YEAR/DAY string from a datetime
  """
  return dt.strftime("%m/%d/%Y")

def response_of_file(file_name, url=None):
  """
    Convert an HTML file to a Scrapy response object
    Code from: http://stackoverflow.com/a/12741030/5237018
  """
  if not url:
    url = 'http://www.example.com'

  request = scrapy.http.Request(url=url)
  if not file_name[0] == '/':
    responses_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(responses_dir, file_name)
  else:
    file_path = file_name

  with open(file_path, "r") as f:
    file_content = f.read()

  return scrapy.http.HtmlResponse(url=url
                     ,request=request
                     ,body=file_content
                     ,encoding="utf-8")


## -----------------------------------------------------------------------------
class TestScrapeUtil(unittest.TestCase):

  def setUp(self):
    html = "./test/scrape_util.html"
    if not os.path.exists(html):
      raise ValueError("Could not find sample HTML file at '%s', cannot run tests" % html)
    self.sample_html_file = html
    self.sample_url = "http://www.scrape-util-test.com"

  def test_datetime_of_ampm(self):
    dt0 = datetime_of_ampm("7pm")
    self.assertEqual(dt0.hour, 19)
    dt1 = datetime_of_ampm("6am")
    self.assertEqual(dt1.hour, 6)
    dt2 = datetime_of_ampm("9 30am")
    self.assertEqual(dt2.hour, 9)
    self.assertEqual(dt2.minute, 30)

  def test_datetime_of_mdy(self):
    y = 2015
    m = 5
    dt0 = datetime_of_mdy("%s/%s/%s" % (m, m, y))
    dt1 = datetime_of_mdy("0%s/0%s/%s" % (m, m, y))
    for dt in [dt0, dt1]:
      self.assertEqual(dt.year, y)
      self.assertEqual(dt.month, m)
      self.assertEqual(dt.day, m)

  def test_extract_text(self):
    r = response_of_file(self.sample_html_file)
    text = extract_text(r.xpath("//text()"))
    self.assertEqual(text, "sample text for unittest")

  def test_mdy_of_datetime(self):
    missing_zero = "4/4/99"
    dt = datetime_of_mdy(missing_zero)
    self.assertEqual(dt.month, 4)
    self.assertEqual(dt.day, 4)
    self.assertEqual(dt.year, 2099)

  def test_response_of_file(self):
    r = response_of_file(self.sample_html_file, url=self.sample_url)
    self.assertTrue(isinstance(r, scrapy.http.Response))
    self.assertEqual(self.sample_url, r.url)

