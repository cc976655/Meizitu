#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import re
from scrapy import Spider, Request, Selector

from meizi.items import ItubaccItem


class zol_cpu(Spider):
    name = 'itubacc'
    start_urls = ['https://www.ituba.cc/meinvtupian/']
    allow_domains = ['https://www.ituba.cc']

    def parse(self, response):
        page_size = response.xpath('//html/body/div[3]/div[8]/ul/a[8]/text()').extract()[0]

        for index in range(1, int(page_size) + 1):
            page_url = 'https://www.ituba.cc/meinvtupian/p' + str(index) + '.html'
            print(page_url)
            yield Request(url=page_url, callback=self.parse_album)

    def parse_album(self, response):
        album_list = response.xpath('//div[@id="NewList"][1]/ul/li').extract()

        sort_1 = "美女图片"

        for album in album_list:
            album_selector = Selector(text=album)

            sort_2 = album_selector.xpath('//span/em/a/text()').extract()[0]
            name = album_selector.xpath('//a[@class="PicTxt"]/@title').extract()[0]
            album_first_url = album_selector.xpath('//a[1]/@href').extract()[0]
            id = re.findall(r'\d+?\d*', album_first_url)[0]
            base_url = album_selector.xpath('//span/em/a/@href').extract()[0]
            # size_temp = album_selector.xpath('//p[@class="Click"]/i[1]/text()').extract()[0]
            # try:
            #     size = re.findall(r'\d+?\d*', size_temp)[0]
            # except IndexError as e:
            #     print(album)
            first_pic_url = base_url + str(id) + '.html'
            yield Request(url=first_pic_url, callback=self.parse_total_image_size, meta={
                'id': id,
                'sort_1': sort_1,
                'sort_2': sort_2,
                'name': name,
                'base_url': base_url
            })

    def parse_total_image_size(self, response):
        try:
            total_image_size = int(response.xpath('/html/body/div[6]/div[3]/ul/a[7]/text()').extract()[0])
            base_url = response.meta['base_url']
            id = response.meta['id']
            for index in range(1, int(total_image_size)):
                pic_url = base_url + str(id) + '_' + str(index) + '.html'
                print(pic_url)
                yield Request(url=pic_url, callback=self.parse_origin_url, meta={
                    'sort_1': response.meta['sort_1'],
                    'sort_2': response.meta['sort_2'],
                    'name': response.meta['name'],
                    'order': index,
                })
        except ValueError as e:
            print(e)
        except IndexError as e:
            print(e)

    def parse_origin_url(self, response):
        origin_url = response.xpath('/html/body/div[6]/div[3]/ul/li/a/@href').extract()[0]
        item = ItubaccItem()
        item['sort_1'] = response.meta['sort_1']
        item['sort_2'] = response.meta['sort_2']
        item['name'] = response.meta['name']
        item['order'] = response.meta['order']
        item['origin_url'] = origin_url
        yield item
