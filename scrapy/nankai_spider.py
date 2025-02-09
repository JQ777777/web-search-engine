import scrapy
from ..items import NankaiNewsItem
from urllib.parse import urljoin
from pathlib import Path

class NankaiSpider(scrapy.Spider):
    name = 'nankai'
    allowed_domains = ['nankai.edu.cn']
    start_urls = ['https://news.nankai.edu.cn/']

    # 用于存储已经访问过的URL，避免重复抓取
    visited_urls = set()

    def parse(self, response):
        # 提取首页中的所有新闻链接
        news_links = response.css('div.news-item a::attr(href)').getall()

        # 跟进每个新闻链接，调用 parse_news_page 方法处理详情页
        for link in news_links:
            absolute_link = response.urljoin(link)
            yield scrapy.Request(absolute_link, callback=self.parse_news_page)

        # 如果有分页，继续抓取下一页
        next_page = response.css('a.next-page::attr(href)').get()
        if next_page:
            absolute_next_page = response.urljoin(next_page)
            yield scrapy.Request(absolute_next_page, callback=self.parse)

    def save_html_page(self, response):
        # 获取当前URL的文件名（去除协议和域名）
        page_url = response.url
        file_name = page_url.split('/')[-1] or 'index.html'
        file_path = Path('saved_pages') / file_name

        # 确保保存目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 将HTML内容写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(response.text)

        self.logger.info(f"Saved HTML page to {file_path}")

    def parse_news_page(self, response):
        item = NankaiNewsItem()

        # 提取新闻标题
        item['title'] = response.xpath('//h1/text()').get()

        # 提取新闻发布时间
        item['publish_time'] = response.xpath('//span[@class="time"]/text()').get()

        # 提取新闻内容
        item['content'] = ''.join(response.xpath('//div[@class="article-content"]//p//text()').getall()).strip()

        # 提取新闻关键词
        item['keywords'] = response.xpath('//meta[@name="keywords"]/@content').get(default='')

        # 提取新闻中的所有链接URL，并转换为绝对URL
        item['link_urls'] = [urljoin(response.url, url) for url in response.xpath('//div[@class="article-content"]//a/@href').getall()]

        # 当前URL
        item['current_url'] = response.url

        yield item

        # 提取页面中的所有链接，并跟进这些链接
        all_links = response.xpath('//a/@href').getall()
        for link in all_links:
            absolute_link = response.urljoin(link)

            # 检查是否已经访问过该链接
            if absolute_link not in self.visited_urls and self.is_allowed_domain(absolute_link):
                self.visited_urls.add(absolute_link)
                yield scrapy.Request(absolute_link, callback=self.parse_following_page)

    def parse_following_page(self, response):
        # 保存HTML页面
        self.save_html_page(response)

        # 提取页面中的所有链接，并继续跟进
        all_links = response.xpath('//a/@href').getall()
        for link in all_links:
            absolute_link = response.urljoin(link)

            # 检查是否已经访问过该链接
            if absolute_link not in self.visited_urls and self.is_allowed_domain(absolute_link):
                self.visited_urls.add(absolute_link)
                yield scrapy.Request(absolute_link, callback=self.parse_following_page)

    def is_allowed_domain(self, url):
        # 检查URL是否属于允许的域名
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        return parsed_url.netloc in self.allowed_domains