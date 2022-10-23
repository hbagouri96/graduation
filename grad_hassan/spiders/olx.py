import scrapy
import pprint
import re

from scrapy.http import TextResponse

from jsonltojson import jsonltojson

pp = pprint.PrettyPrinter(indent=4)

class OlxProperties(scrapy.Spider):
    name = "olx"

    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    base_url = "https://www.olx.com.eg/en/properties/villas-for-sale/"
    start_urls = [base_url]


    def parse(self, response: TextResponse):
        articles = response.xpath('//article')
        for article in articles:
            id = article.css('a::attr(href)').re_first(r'ID\d*')
            url = 'https://www.olx.com.eg' + article.xpath('.//a/@href').get()
            listing = {
                'id': id,
                'title': article.xpath('.//div[@aria-label="Title"]/text()').get(),
                'location': article.xpath('.//span[@aria-label="Location"]/text()').get(),
                'area': int(article.xpath('.//span[@aria-label="Area"]/span/text()').re_first(r'\d+')),
                'bedrooms': int(article.xpath('.//span[@aria-label="Bedrooms"]/text()').re_first(r'\d+')),
                'bathrooms': int(article.xpath('.//span[@aria-label="Bathrooms"]/text()').re_first(r'\d+')),
                'price': int(article.xpath('.//div[@aria-label="Price"]/span/text()').re_first(r'(?:\d+,?)+').replace(',', '')),
                'url': url,
            }

            yield response.follow(url, callback=self.parse_article, cb_kwargs={'listing': listing})

            last_url = response.xpath('//a[contains(@href, "page")]')

            if last_url.xpath('//a/div/@title')[-1].get() == 'Next':
             next_page = last_url[-1].css('a::attr(href)').get()
             yield response.follow(f'https://www.olx.com.eg{next_page}', callback=self.parse)

    def get_item(self, item):
        whitelist = ['Price', 'Down Payment', 'Area (m²)', 'Bedrooms', 'Bathrooms', 'Level', 'Delivery Date']
        if item[0] in whitelist and item[1].replace(',', '').isdigit():
            return int(item[1].replace(',', ''))
        else:
            return item[1]

    def parse_article(self, response: TextResponse, listing):
        all_details = response.xpath('.//div[@aria-label="Details and description"]/div/div/div')
        details = {}
        detail: TextResponse
        for detail in all_details:
            item = detail.xpath('.//div/span/text()').getall()
            if len(item) != 2: continue
            details[item[0].lower()] = self.get_item(item)
        listing['details'] = details
        return listing

    def closed(self, _):
        jsonltojson()



#  response.xpath('//div[@id="images"]/a/text()').get()
