import scrapy
import json

import logging


class WhatsOnZwiftSpider(scrapy.Spider):
    name = 'whatsonzwiftspider'
    #start_urls = ['https://whatsonzwift.com/workouts/crit-crusher/']
    #start_urls = ['https://whatsonzwift.com/workouts/4wk-ftp-booster/']
    start_urls = ['https://whatsonzwift.com/workouts/']
    image_urls = scrapy.Field()
    def parse(self, response):
        try:
            for article in response.css('article.workout'):
                title = ''
                for name in article.css('div.breadcrumbs>a.button::text'):
                    title += name.get() + ' '
                title += article.css('div.breadcrumbs>h4.flaticon-bike::text').get()
                logging.info('parsing data for {}'.format(title))
                data = {'title': title,
                    'creator': article.css('div.breadcrumbs>a.button::text').get(),
                    'MRC': []
                }
                for textbar in article.css('div.workoutlist').css('div.textbar'):
                    sz = ''.join(textbar.css('*::text').extract())
                    parts = sz.split('FTP,')
                    intensities = []

                    for p in parts:
                        intensities.append(p.split(' '))
                    
                    intensity_from = []
                    intensity_to = []
                    duration = []
                    repeat = []

                    for sz in intensities:
                        dur, rep, sz = ParseDuration(sz)
                        duration.append(dur)
                        repeat.append(rep)

                        if sz[0] == 'from':
                            intensity_from.append(int(sz[1]))
                            intensity_to.append(int(sz[3].replace('%', '')))
                        elif sz[0] == '@':
                            if 'rpm' in sz[1]:
                                sz = sz[1:]
                            intensity_to.append(int(sz[1].replace('%', '')))
                            intensity_from.append(int(sz[1].replace('%', '')))
                    for _ in range(repeat[0]):
                        for i in range(len(intensity_from)):
                            data['MRC'].append([duration[i], intensity_from[i], intensity_to[i]])
                
                if data['title']:
                    yield data
        except ValueError as e:
            logging.error(e)
        except TypeError as e:
            logging.error(e)

        for next_page in response.css('div.card-link>a.button::attr("href")'):
            yield response.follow(next_page, self.parse)


def ParseDuration(szArr : []) -> (float, int, []):
    duration = 0
    repeat = 1
    for i in range(len(szArr)):
        szDur = szArr[i]
        if 'hr' in szDur:
            duration += (int(szDur.replace('hr', '')) * 60)
        elif 'min' in szDur:
            duration += int(szDur.replace('min', ''))
        elif 'sec' in szDur:
            duration += (int(szDur.replace('sec', '')) / 60)
        elif 'x' in szDur:
            repeat = int(szDur.replace('x', ''))
        else:
            return (duration, repeat, szArr[i:])

