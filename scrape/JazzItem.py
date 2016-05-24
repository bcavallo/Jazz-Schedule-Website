import scrapy

class JazzItem(scrapy.Item):

  artist = scrapy.Field()
  date = scrapy.Field()
  venue = scrapy.Field()
