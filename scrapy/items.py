# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ItcastItem(scrapy.Item):
    seq = scrapy.Field()
    page_url = scrapy.Field()  # 当前网页的 URL
    encode = scrapy.Field()  # 编码
    keywords = scrapy.Field()  # 关键词
    description = scrapy.Field()  # 描述
    title = scrapy.Field()  # 标题
    content = scrapy.Field()  # 完整的 HTML 内容
    html_file = scrapy.Field()  # 保存的 HTML 文件路径
    links = scrapy.Field()
    pr = scrapy.Field()
