#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import datetime

from six.moves.urllib.parse import urlparse
import click
import scrapy
from scrapy.http import Request, HtmlResponse
from scrapy.linkextractors import LinkExtractor

from broad.items import Page
import logging

class BroadBenchSpider(scrapy.Spider):
    name = "broadspider"
    logname = 'sync-test.log'
    #logname = 'async-test.log'
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(logname)
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    port = 8880
    n_domains = 1000

    ratings_map = {
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
    }

    def __init__(self, **kw):
        super(BroadBenchSpider, self).__init__(**kw)

        self.link_extractor = LinkExtractor()
        self.cookies_seen = set()
        self.previtem = 0
        self.items = 0
        self.timesec = datetime.datetime.utcnow()
        self.start_urls = [
            'http://domain{}:{}/index.html'.format(i, self.port) for i in range(1, self.n_domains + 1)]

    def parse(self, response):
        """Parse a PageItem and all requests to follow"""
        page = self._get_item(response)
        r = [page]

        r.extend(self._extract_requests(response))
        self.items = self.crawler.stats.get_value('item_scraped_count', 0)
        pages = self.crawler.stats.get_value('response_received_count', 0)
        a = self.crawler.stats.get_value('start_time')
        b = datetime.datetime.utcnow()
        self.timesec = b - a

        return r

    def close(self, reason):
        with open("Benchmark.txt", 'w') as f:
            f.write(" {0}".format(
                (self.items * (1 / self.timesec.total_seconds()))))
        click.secho("\nThe average speed of the spider is {0} items/sec\n".format(
            self.items * (1 / self.timesec.total_seconds())), bold=True)

    def _get_item(self, response):
        item = Page(
            url=response.url,
            size=str(len(response.body)),
            referer=response.request.headers.get('Referer'),
            rating=response.css(
                'p.star-rating::attr(class)').extract_first().split(' ')[-1],
            title=response.css('.product_main h1::text').extract_first(),
            price=response.css(
                '.product_main p.price_color::text').re_first('£(.*)'),
            stock=''.join(
                response.css('.product_main .instock.availability ::text').re('(\d+)')),
            category=''.join(
                response.css('ul.breadcrumb li:nth-last-child(2) ::text').extract()).strip(),
        )

        self._set_new_cookies(item, response)
        return item

    def _extract_requests(self, response):
        r = []
        if isinstance(response, HtmlResponse):
            links = self.link_extractor.extract_links(response)
            r.extend(Request(x.url, callback=self.parse) for x in links)
        return r

    def _set_new_cookies(self, page, response):
        cookies = []
        for cookie in [x.split(b';', 1)[0] for x in
                       response.headers.getlist('Set-Cookie')]:
            if cookie not in self.cookies_seen:
                self.cookies_seen.add(cookie)
                cookies.append(cookie)
        if cookies:
            page['newcookies'] = cookies
