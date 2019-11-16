import scrapy
import json
import re

class WhatsOnZwiftSpider(scrapy.Spider):
    name = 'whatsonzwiftspider'
    start_urls = ['https://whatsonzwift.com/workouts/']
    image_urls = scrapy.Field()
    def parse(self, response):
        for article in response.css('article.workout'):
            data = {'title': article.css('div.breadcrumbs>h4.flaticon-bike::text').get(),
                'category': article.css('div.breadcrumbs>a.button::text').get(),
                'data': []
            }
            for textbar in article.css('div.workoutlist').css('div.textbar'):
                data['data'].append(textbar.css('::text').get())
            if data['title']:
                yield data

        for next_page in response.css('div.card-link>a.button::attr("href")'):
            yield response.follow(next_page, self.parse)
