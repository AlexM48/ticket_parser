# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TicketlandItem(scrapy.Item):
    sector = scrapy.Field()
    row = scrapy.Field()
    seat = scrapy.Field()
    price = scrapy.Field()
    count = scrapy.Field()

