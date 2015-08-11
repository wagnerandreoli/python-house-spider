# -*- coding: utf-8 -*-
"""A spider to crawl the Immobilien Scout 24 website."""
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader

from home_spider.items import ApartmentItem, json_config


class ImmobilienScout24Spider(scrapy.Spider):

    """A spider to crawl the Immobilien Scout 24 website."""

    name = "immobilien_scout_24"
    allowed_domains = ["immobilienscout24.de"]
    start_urls = (
        'http://www.immobilienscout24.de/',
    )

    CITY = ' Berlin,'
    DIV_PRE_MAPPING = {
        'description': 'is24qa-objektbeschreibung',
        'equipment': 'is24qa-ausstattung',
        'location': 'is24qa-lage',
        'other': 'is24qa-sonstiges'
    }

    def parse(self, response):
        """Parse a search results HTML page."""
        for link in LinkExtractor(allow=r'expose/[0-9]+$').extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_item)

    def parse_item(self, response):
        """Parse an ad page, with an apartment."""
        item = ItemLoader(ApartmentItem(), response=response)
        item.add_value('url', response.url)
        item.add_css('title', 'h1#expose-title::text')

        for field, css_class in self.DIV_PRE_MAPPING.items():
            item.add_xpath(field, "//div/pre[contains(@class, '{}')]/text()".format(css_class))

        full_address = ''.join(response.xpath("//span[@data-qa='is24-expose-address']/text()").extract()).strip()
        parts = full_address.split(self.CITY)
        if len(parts) == 1:
            item.add_value('address', full_address)
        else:
            item.add_value('address', (parts[0] + self.CITY).strip(' ,'))
            item.add_value('neighborhood', ''.join(parts[1:]).strip(' ,'))

        item.add_css('cold_rent', 'div.is24qa-kaltmiete::text')
        item.add_css('warm_rent', 'dd.is24qa-gesamtmiete::text')
        yield item.load_item()

ImmobilienScout24Spider.start_urls = json_config(__file__, 'start_urls')
