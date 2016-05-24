import datetime
import unittest

MDY_RX = r'[0-9]+/[0-9]+/[0-9]+'

def mdy_of_datetime(dt):
  return dt.strftime("%m/%d/%Y")

def datetime_of_ampm(ampm):
  """
    Parse a string like '7pm' to a datetime
  """
  if " " in ampm:
    return datetime.datetime.strptime(ampm, "%I %M%p")
  else:
    return datetime.datetime.strptime(ampm, "%I%p")

def datetime_of_mdy(date_str):
  return datetime.datetime.strptime(date_str, "%m/%d/%y")

def extract_text(sel):
  return " ".join((x for x in (x.strip() for x in sel.extract()) if x))

## -----------------------------------------------------------------------------

class TestScrapeUtil(unittest.TestCase):

  def test_mdy_of_datetime(self):
    missing_zero = "4/4/99"
    dt = datetime_of_mdy(missing_zero)
    self.assertEqual(dt.month, 4)
    self.assertEqual(dt.day, 4)
    self.assertEqual(dt.year, 1999)

  def test_datetime_of_ampm(self):
    dt0 = datetime_of_ampm("7pm")
    self.assertEqual(dt0.hour, 19)
    dt1 = datetime_of_ampm("6am")
    self.assertEqual(dt1.hour, 6)
    dt2 = datetime_of_ampm("9 30am")
    self.assertEqual(dt2.hour, 9)
    self.assertEqual(dt2.minute, 30)


## -----------------------------------------------------------------------------

if __name__ == "__main__":
  unittest.main()
